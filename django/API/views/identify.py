# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2022-2023 Edith Coates
# Copyright (C) 2022-2023 Colin B. Macdonald
# Copyright (C) 2023 Andrew Rechnitzer
# Copyright (C) 2023 Natalie Balashov

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from Preparation.services import StagingStudentService
from Identify.services import IdentifyTaskService, IDReaderService


class GetClasslist(APIView):
    """Get the classlist."""

    def get(self, request):
        sstu = StagingStudentService()
        if sstu.are_there_students():
            students = sstu.get_students()

            # TODO: new StudentService or ClasslistService that implements
            # the loop below?
            for s in students:
                s["id"] = s.pop("student_id")
                s["name"] = s.pop("student_name")

            return Response(students)


class GetIDPredictions(APIView):
    """Get, put and delete predictions for test-paper identification.

    If no predictor is specified, get or delete all predictions.

    Client needs predictions to be formatted as a dict of lists,
    where each list contains an inner dict with prediction
    info for a particular predictor (could have more than one).
    """

    def get(self, request, *, predictor=None):
        id_reader_service = IDReaderService()
        if predictor == None:
            predictions = id_reader_service.get_ID_predictions()
        elif predictor == "prename":  # TODO: remove this block later
            sstu = StagingStudentService()
            if sstu.are_there_students():
                predictions = {}
                for s in sstu.get_students():
                    if s["paper_number"]:
                        predictions[s["paper_number"]] = [
                            {
                                "student_id": s["student_id"],
                                "certainty": 100,
                                "predictor": "prename",
                            }
                        ]
        else:
            predictions = id_reader_service.get_ID_predictions(predictor=predictor)
        return Response(predictions)

    def put(self, request):
        """Add or change ID predictions."""
        data = request.data
        user = request.user
        id_reader_service = IDReaderService()
        for paper_num in data:
            id_reader_service.add_or_change_ID_prediction(
                user,
                int(paper_num),
                data[paper_num]["student_id"],
                data[paper_num]["certainty"],
                data[paper_num]["predictor"],
            )
        return Response(status=status.HTTP_200_OK)

    def delete(self, request, predictor=None):
        """Remove ID predictions from a predictor."""
        data = request.data
        user = request.user
        id_reader_service = IDReaderService()
        if predictor:
            try:
                id_reader_service.delete_ID_predictions(user, predictor)
                return Response(status=status.HTTP_200_OK)
            except RuntimeError:
                return Response(status=status.HTTP_400_BAD_REQUEST)
        else:
            for predictor_name in ("MLLAP", "MLGreedy"):
                id_reader_service.delete_ID_predictions(user, predictor_name)
            return Response(status=status.HTTP_200_OK)


class IDgetDoneTasks(APIView):
    """When a id-client logs on they request a list of papers they have already IDd.

    Send back the list.
    """

    def get(self, request):
        its = IdentifyTaskService()
        tasks = its.get_done_tasks(request.user)

        return Response(tasks, status=status.HTTP_200_OK)

    # TODO: how do we log?


class IDgetNextTask(APIView):
    """Responds with a code for the the next available identify task.

    Note: There is no guarantee that task will still be available later but at this moment in time,
    no one else has claimed it

    Responds with status 200/204.

    TODO: Not implemented, just lies that we are done.
    TODO: see ``plom/db/db_identify:IDgetNextTask``
    """

    def get(self, request):
        its = IdentifyTaskService()
        next_task = its.get_next_task()
        if next_task:
            paper_id = next_task.paper.paper_number
            return Response(paper_id, status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_204_NO_CONTENT)


class IDprogressCount(APIView):
    def get(self, request):
        """Responds with a list of completed/total tasks."""
        its = IdentifyTaskService()
        progress = its.get_id_progress()
        return Response(progress, status=status.HTTP_200_OK)


class IDclaimThisTask(APIView):
    def patch(self, request, paper_id):
        """Claims this identifying task for the user."""
        its = IdentifyTaskService()
        try:
            its.claim_task(request.user, paper_id)
            return Response(status=status.HTTP_200_OK)
        except RuntimeError:
            return Response(
                f"ID task {paper_id} already claimed", status=status.HTTP_409_CONFLICT
            )

    def put(self, request, paper_id):
        """Assigns a name and a student ID to the paper."""
        data = request.data
        user = request.user
        its = IdentifyTaskService()
        its.identify_paper(user, paper_id, data["sid"], data["sname"])
        return Response(status=status.HTTP_200_OK)
