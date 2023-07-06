# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2023 Colin B. Macdonald
# Copyright (C) 2023 Edith Coates

from django.shortcuts import get_object_or_404

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from Finish.services import ReassembleService

from Papers.models import Paper
from Mark.services import MarkingTaskService


class REPspreadsheet(APIView):
    def get(self, request):
        spreadsheet_data = ReassembleService().get_spreadsheet_data()
        return Response(
            spreadsheet_data,
            status=status.HTTP_200_OK,
        )


class REPidentified(APIView):
    def get(self, request):
        id_data = ReassembleService().get_identified_papers()
        return Response(
            id_data,
            status=status.HTTP_200_OK,
        )


class REPcompletionStatus(APIView):
    def get(self, request):
        completion_data = ReassembleService().get_completion_status()
        return Response(
            completion_data,
            status=status.HTTP_200_OK,
        )


class REPcoverPageInfo(APIView):
    def get(self, request, papernum):
        # Return value looks like this:
        # [["10130103", "Vandeventer, Irene"], [1, 1, 0], [2, 1, 1], [3, 2, 5]]
        reasseble = ReassembleService()
        paper = get_object_or_404(Paper, paper_number=papernum)
        cover_page_info = reasseble.get_cover_page_info(paper)
        return Response(cover_page_info, status=status.HTTP_200_OK)
