# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2022-2023 Edith Coates
# Copyright (C) 2022-2023 Colin B. Macdonald
# Copyright (C) 2023 Andrew Rechnitzer

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import APIException, ValidationError
from rest_framework import status

from django.core.exceptions import ObjectDoesNotExist
from django.core.files.uploadedfile import SimpleUploadedFile
from django.http import FileResponse

from Papers.services import SpecificationService
from Papers.models import Paper, Image

from Mark.services import MarkingTaskService, PageDataService
from Mark.models import AnnotationImage, MarkingTask

import logging


class QuestionMaxMark_how_to_get_data(APIView):
    """Return the max mark for a given question.

    TODO: how do I make the `data["q"]` thing work?  This always fails with KeyError
    """

    def get(self, request):
        data = request.query_params
        try:
            question = int(data["q"])
            version = int(data["v"])
        except KeyError:
            exc = APIException()
            exc.status_code = status.HTTP_400_BAD_REQUEST
            exc.detail = "Missing question and/or version data."
            raise exc
        except (ValueError, TypeError):
            exc = APIException()
            exc.status_code = status.HTTP_400_BAD_REQUEST
            exc.detail = "question and version must be integers"
            raise exc
        spec = SpecificationService()
        return Response(spec.get_question_mark(question))


class QuestionMaxMark(APIView):
    """Return the max mark for a given question.

    Returns:
        (200): returns the maximum number of points for a question
        (400): malformed, missing question, etc, TODO: not implemented
        (416): question values out of range
    """

    def get(self, request, *, question):
        spec = SpecificationService()
        try:
            return Response(spec.get_question_mark(question))
        except KeyError:
            exc = APIException()
            exc.status_code = status.HTTP_416_REQUESTED_RANGE_NOT_SATISFIABLE
            exc.detail = "question out of range"
            raise exc


class MarkingProgressCount(APIView):
    """Responds with a list of completed/total tasks.

    Returns:
        (200): returns two integers, first the number of marked papers
            for this question/version and the total number of papers for
            this question/version.
        (400): malformed such as non-integers for question/version.
        (416): question values out of range: NOT IMPLEMENTED YET.
            (In legacy, this was thrown by the backend).
    """

    def get(self, request):
        data = request.data
        try:
            question = int(data["q"])
            version = int(data["v"])
        except (ValueError, TypeError):
            exc = APIException()
            exc.status_code = status.HTTP_400_BAD_REQUEST
            exc.detail = "question and version must be integers"
            raise exc
        mts = MarkingTaskService()
        progress = mts.get_marking_progress(question, version)
        return Response(progress, status=status.HTTP_200_OK)


class MgetDoneTasks(APIView):
    """Retrieve data for questions which have already been graded by the user.

    Respond with status 200.

    Returns:
        200: list of [group-ids, mark, marking_time, [list_of_tag_texts], integrity_check ] for each paper.
    """

    def get(self, request, *args):
        data = request.data
        question = data["q"]
        version = data["v"]

        mts = MarkingTaskService()
        marks = mts.get_user_mark_results(
            request.user, question=question, version=version
        )

        # TODO: 3rd entry here is marking time: in legacy, we trust the client's
        # previously given value (which the client tracks including revisions)
        # Currently this tries to estimate a value server-side.  Decisions?
        # Previous code was `mark_action.time - mark_action.claim_action.time`
        # which is a `datatime.timedelta`.  Not sure how to convert to seconds
        # so currently using hardcoded value.
        # TODO: legacy marking time is int, but we may decide to change to float.
        rows = map(
            lambda annotation: [
                annotation.task.code,
                annotation.score,
                annotation.marking_time,
                mts.get_tags_for_task(annotation.task.code),
                annotation.task.pk,  # TODO: integrity check is not implemented yet
            ],
            marks,
        )
        return Response(rows, status=status.HTTP_200_OK)


class MgetNextTask(APIView):
    """Responds with a code for the next available marking task.

    Returns:
        200: An available task exists, returns the task code as a string.
        204: There are no available tasks.
    """

    def get(self, request, *args):
        data = request.data
        question = data["q"]
        version = data["v"]

        mts = MarkingTaskService()

        task = mts.get_first_available_task(question=question, version=version)
        if task:
            return Response(task.code, status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_204_NO_CONTENT)


class MclaimThisTask(APIView):
    def patch(self, request, code, *args):
        """Attach a user to a marking task and return the task's metadata."""
        mss = MarkingTaskService()
        the_task = mss.get_task_from_code(code)
        mss.assign_task_to_user(request.user, the_task)

        pds = PageDataService()
        paper, question = mss.unpack_code(code)
        question_data = pds.get_question_pages_list(paper, question)

        return Response([question_data, mss.get_tags_for_task(code), the_task.pk])

    def post(self, request, code, *args):
        """Accept a marker's grade and annotation for a task."""
        mts = MarkingTaskService()
        data = request.POST
        files = request.FILES

        plomfile = request.FILES["plomfile"]
        plomfile_data = plomfile.read().decode("utf-8")

        try:
            mark_data, annot_data, rubrics_used = mts.validate_and_clean_marking_data(
                request.user, code, data, plomfile_data
            )
        except ObjectDoesNotExist as e:
            return Response(e, status=status.HTTP_404_NOT_FOUND)
        except RuntimeError as e:
            return Response(e, status=status.HTTP_409_CONFLICT)
        except ValidationError as e:
            return Response(e, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        annotation_image = files["annotation_image"]
        try:
            img_md5sum = data["md5sum"]
            img = mts.save_annotation_image(img_md5sum, annotation_image)
        except FileExistsError:
            return Response(
                "Annotation image already exists.", status=status.HTTP_409_CONFLICT
            )
        except ValidationError:
            return Response(
                "Unsupported media type for annotation image",
                status=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            )

        mts.mark_task(
            request.user,
            code,
            mark_data["score"],
            mark_data["marking_time"],
            img,
            annot_data,
        )
        mts.mark_task_as_complete(code)

        return Response(
            [mts.get_n_marked_tasks(), mts.get_n_total_tasks()],
            status=status.HTTP_200_OK,
        )


class MgetPageDataQuestionInContext(APIView):
    """Get page metadata for a particular test-paper optionally with a question highlighted.

    APIs backed by this routine return a JSON response with a list of
    dicts, where each dict has keys: `pagename`, `md5`, `included`,
    `order`, `id`, `orientation`, `server_path` as documented below.

    This routine returns all pages, including ID pages, DNM pages and
    various sorts of extra pages.

    TODO: 409 versus 400?  Legacy used 409...
    A 400 is returned with an explanation if paper number not found.

    The list of dicts (we think of them as rows) have the keys:

    `pagename`
        A string something like `"t2"`.  Reasonable to use
        as a thumbnail label for the image or in other cases where
        a very short string label is required.

    `md5`
        A string of the md5sum of the image.

    `id`
        an integer like 19.  This is the key in the database to
        the image of this page.  It is (I think) possible to have
        two pages pointing to the same image, in which case the md5
        and the id could be repeated.  TODO: determine if this only
        happens b/c of bugs/upload issues or if its a reasonably
        normal state.
        Note this is nothing to do with "the ID page", that is the page
        where assessment writers put their name and other info.

    `order`
        None or an integer specifying the relative ordering of
        pages within a question.  As with `included`,
        this information only reflects the initial (typically
        scan-time) ordering of the images.  If its None, server has
        no info about what order might be appropriate, for example
        because this image is not thought to belong in `question`.

    `orientation`
        relative to the natural orientation of the image.
        This is an integer for the degrees of rotation.  Probably
        only multiples of 90 work and perhaps only [0, 90, 180, 270]
        but could/should (TODO) be generalized for arbitrary
        rotations.  This should be applied *after* any metadata
        rotations from inside the file instead (such as jpeg exif
        orientation).  As with `included` and `order`, this is only
        the initial state.  Clients may rotate images and that
        information belongs their annotation.

    `server_path`
        a string of a path and filename where the server
        might have the file stored, such as
        `"pages/originalPages/t0004p02v1.86784dd1.png"`.
        This is guaranteed unique (such as by the random bit before
        `.png`).  It is *not* guaranteed that the server actually
        stores the file in this location, although the current
        implementation does.

    `included`
        boolean, did the server *originally* have this page
        included in question number `question`?.  Note that clients
        may pull other pages into their annotating; you can only
        rely on this information for initializing a new annotating
        session.  If you're e.g., editing an existing annotation,
        you should rely on the info from that existing annotation
        instead of this.

    Example::

        [
          {'pagename': 't2',
           'md5': 'e4e131f476bfd364052f2e1d866533ea',
           'included': False,
           'order': None,
           'id': 19',
           'orientation': 0
           'server_path': 'pages/originalPages/t0004p02v1.86784dd1.png',
          },
          {'pagename': 't3',
           'md5': 'a896cb05f2616cb101df175a94c2ef95',
           'included': True,
           'order': 1,
           'id': 20,
           'orientation': 270
           'server_path': 'pages/originalPages/t0004p03v2.ef7f9754.png',
          }
        ]
    """

    def get(self, request, paper, question=None):
        service = PageDataService()

        try:
            # we need include_idpage here b/c this APIView Class serves two different
            # API calls: one of which wants all pages.  Its also documented above that
            # callers who don't want to see the ID page (generally b/c Plom does
            # anonymous grading) should filter this out.  This is the current behaviour
            # of the Plom Client UI tool.
            page_metadata = service.get_question_pages_metadata(
                paper, question=question, include_idpage=True, include_dnmpages=True
            )
            return Response(page_metadata, status=status.HTTP_200_OK)
        except Paper.DoesNotExist:
            return Response(
                detail="Test paper does not exist.", status=status.HTTP_400_BAD_REQUEST
            )


class MgetOneImage(APIView):
    """Get a page image from the server."""

    def get(self, request, pk, hash):
        pds = PageDataService()
        # TODO - replace this fileresponse(open(file)) with fileresponse(filefield)
        # so that we don't have explicit file-path handling.
        try:
            img_path = pds.get_image_path(pk, hash)
            return FileResponse(open(img_path, "rb"), status=status.HTTP_200_OK)
        except Image.DoesNotExist:
            return Response(
                detail="Image does not exist.",
                status=status.HTTP_400_BAD_REQUEST,
            )


class MgetAnnotations(APIView):
    """Get the latest annotations for a question."""

    def get(self, request, paper, question):
        mts = MarkingTaskService()
        annotation = mts.get_latest_annotation(paper, question)
        annotation_task = annotation.task
        annotation_data = annotation.annotation_data

        latest_task = mts.get_latest_task(paper, question)
        if latest_task != annotation_task:
            return Response(
                "Integrity error: task has been modified by server.",
                status=status.HTTP_406_NOT_ACCEPTABLE,
            )

        annotation_data["user"] = annotation.user.username
        annotation_data["annotation_edition"] = annotation.edition
        annotation_data["annotation_reference"] = annotation.pk

        return Response(annotation_data, status=status.HTTP_200_OK)


class MgetAnnotationImage(APIView):
    """Get an annotation-image."""

    def get(self, request, paper, question, edition=None):
        mts = MarkingTaskService()
        annotation = mts.get_latest_annotation(paper, question)
        if not annotation:
            return Response(
                f"No annotations for paper {paper} question {question}",
                status=status.HTTP_404_NOT_FOUND,
            )
        annotation_task = annotation.task
        annotation_image = annotation.image

        latest_task = mts.get_latest_task(paper, question)
        if latest_task != annotation_task:
            return Response(
                "Integrity error: task has been modified by server.",
                status=status.HTTP_406_NOT_ACCEPTABLE,
            )

        return FileResponse(
            open(annotation_image.path, "rb"), status=status.HTTP_200_OK
        )


class TagsFromCodeView(APIView):
    """Handle getting and setting tags for marking tasks."""

    def get(self, request, code):
        """Get all of the tags for a particular task.

        Args:
            code: str, question/paper code for a task

        Returns:
            200: list of tag texts

        Raises:
            406: Invalid task code
            404: Task is not found
        """
        mts = MarkingTaskService()
        try:
            return Response(mts.get_tags_for_task(code), status=status.HTTP_200_OK)
        except ValueError as e:
            return Response(str(e), status=status.HTTP_406_NOT_ACCEPTABLE)
        except RuntimeError as e:
            return Response(str(e), status=status.HTTP_404_NOT_FOUND)

    def patch(self, request, code):
        """Add a tag to a task. If the tag does not exist in the database, create it as a side effect.

        Args:
            code: str, question/paper code for a task

        Returns:
            200: OK response

        Raises:
            406: Invalid task code or tag text
            404: Task is not found
        """
        mts = MarkingTaskService()
        tag_text = request.data["tag_text"]
        tag_text = mts.sanitize_tag_text(tag_text)

        try:
            the_task = mts.get_task_from_code(code)
            the_tag = mts.get_tag_from_text(tag_text)
            if the_tag:
                mts.add_tag(the_tag, the_task)
                return Response(status=status.HTTP_200_OK)
            else:
                new_tag = mts.create_tag(request.user, tag_text)
                mts.add_tag(new_tag, the_task)
                return Response(status=status.HTTP_200_OK)
        except ValueError as e:
            return Response(str(e), status=status.HTTP_406_NOT_ACCEPTABLE)
        except ValidationError as e:
            # TODO: why not?
            # return Response(reason_phrase=str(e), status=status.HTTP_406_NOT_ACCEPTABLE)
            r = Response(status=status.HTTP_406_NOT_ACCEPTABLE)
            # TODO: yuck but works and looks better than str(e) for ValidationError
            (r.reason_phrase,) = e.args
            return r
        except RuntimeError as e:
            return Response(str(e), status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, code):
        """Remove a tag from a task.

        Args:
            request (Request): with ``tag_text`` (`str`) as a data field
            code: str, question/paper code for a task

        Returns:
            200: OK response

        Raises:
            409: Invalid task code, no such tag, or this task does not
                have this tag.
            404: Task is not found
        """
        mts = MarkingTaskService()
        tag_text = request.data["tag_text"]
        tag_text = mts.sanitize_tag_text(tag_text)

        try:
            mts.remove_tag_text_from_task_code(tag_text, code)
        except ValueError as e:
            r = Response(status=status.HTTP_409_CONFLICT)
            r.reason_phrase = str(e)
            return r
        except RuntimeError as e:
            r = Response(status=status.HTTP_404_NOT_FOUND)
            r.reason_phrase = str(e)
            return r
        return Response(status=status.HTTP_200_OK)


class GetAllTags(APIView):
    """Respond with all of the tags in the server."""

    def get(self, request):
        mts = MarkingTaskService()
        return Response(mts.get_all_tags(), status=status.HTTP_200_OK)
