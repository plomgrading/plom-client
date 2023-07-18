# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2023 Julian Lapenna
# Copyright (C) 2023 Colin B. Macdonald
# Copyright (C) 2023 Divy Patel

import arrow
import numpy as np
import statistics

# Yuck, replace this below when we drop Python 3.8 support
from typing import Dict, Any

from django.db.models import Max

from Mark.services import MarkingTaskService
from Mark.models import MarkingTask
from Papers.models.paper_structure import Paper
from Identify.models import PaperIDAction, PaperIDTask


class StudentMarkService:
    """Service for the Student Marks page."""

    def get_marks_from_paper(self, paper_num: int) -> dict:
        """Get the marks for a paper.

        Args:
            paper_num: The paper number.

        Returns:
            Dict keyed by paper number whose values are a dictionary holding
            the mark information for each question in the paper.
        """
        try:
            paper_obj = Paper.objects.get(pk=paper_num)
        except Paper.DoesNotExist:
            return {}
        marking_tasks = paper_obj.markingtask_set.all()

        questions = {}
        for marking_task in marking_tasks.order_by("question_number"):
            current_annotation = marking_task.latest_annotation

            if current_annotation:
                questions[marking_task.question_number] = {
                    "question": marking_task.question_number,
                    "version": marking_task.question_version,
                    "out_of": current_annotation.annotation_data["maxMark"],
                    "student_mark": current_annotation.score,
                }

        return {paper_num: questions}

    def get_all_marks(self) -> dict:
        """Get the marks for all papers.

        Returns:
            Dict containing the mark information for each question in each paper. Keyed by
            paper number whose values are a dictionary holding the mark information for each
            question in the paper.
        """
        paper_nums = MarkingTask.objects.values_list(
            "paper__paper_number", flat=True
        ).distinct()
        marks = {}
        for paper_num in paper_nums:
            marks.update(self.get_marks_from_paper(paper_num))
        # Sort by paper number
        return {k: marks[k] for k in sorted(marks)}
    
    def get_marks_from_papers(self, papers: dict) -> dict:
        """Get the marks for a list of papers.

        Args:
            papers: The list of papers.

        Returns:
            Dict keyed by question number whose values are a dictionary holding
            a list of marks for each question.
        """
        question_marks = {}

        # Iterate over the data
        for student_id in papers:
            student_data = papers[student_id]
            for question_number in student_data:
                question_info = student_data[question_number]
                question = question_info['question']
                student_mark = question_info['student_mark']
                
                if question not in question_marks:
                    question_marks[question] = []
                
                question_marks[question].append(student_mark)
        
        return question_marks
    
    def get_stats_for_questions(self, question_marks: dict) -> dict:
        """Get the question marks stats from a list of marks.

        Args:
            papers: The list of questions grades. (returned from get_marks_from_papers)

        Returns:
            Dict keyed by question number whose values are a dictionary holding
            the average and standard deviation for each question.
        """
        question_stats = {}
        for question in question_marks:
            marks = question_marks[question]
            avg = sum(marks) / len(marks)
            stdv = statistics.stdev(marks)
            question_stats[question] = {'avg': avg, 'stdv': stdv}
        
        return question_stats

    def convert_stats_to_hist_format(self, stats: dict) -> dict:
        """Convert the question stats to a format that can be used by the histogram.

        Args:
            stats: The question stats returned from get_stats_for_questions.

        Returns:
            data in dict format that can be used by the d3 histogram.
        """
        data = {
            "xLabel": "Question",
            "yLabel": "Average Grade",
            "values": []
        }

        for question in stats:
            data['values'].append({
                'label': question,
                'value': stats[question]['avg']
            })

        return data
    
    def get_correlation_between_questions(self, question_data: dict) -> np.ndarray:
        """Get the correlation matrix between questions.

        Args:
            question_data: The question data returned from get_stats_for_questions.

        Returns:
            The correlation matrix between questions.
        """
        min_length = min(len(lst) for lst in question_data.values())
        question_data = np.array([lst[:min_length] for lst in question_data.values()])
        question_correlation = np.corrcoef(question_data)
        return question_correlation

    def convert_correlation_to_heatmap_format(self, correlation: np.ndarray) -> dict:
        """Convert the correlation matrix to a format that can be used by the heatmap.
        
        Args:
            correlation: The correlation matrix returned from get_correlation_between_questions.
            
        Returns:
            data in dict format that can be used by the d3 heatmap.
        """
        data = {
            "rows": len(correlation),
            "cols": len(correlation[0]),
            "xTitle": "Question",
            "yTitle": "Question",
            "xLabel": list(range(1, len(correlation) + 1)),
            "yLabel": list(range(1, len(correlation) + 1)),
            "values": correlation.tolist(),
        }
        return data

    def get_marks_from_paper_set(self, paper_set: set) -> dict:
        """Get the marks for a set of papers.

        Args:
            paper_set: The set of (int) paper numbers.

        Returns:
            Dict containing the mark information for each question in each paper. Keyed by paper number whose
            values are a dictionary holding the mark information for each question in the paper.
        """
        marks = {}
        for paper_num in paper_set:
            marks.update(self.get_marks_from_paper(paper_num))

        return marks

    def get_n_of_question_marked(self, question: int, *, version: int = 0) -> int:
        """Get the count of how many papers have marked a specific question.

        Args:
            question: The question number.

        Keyword Args:
            version: The version of the question.

        Returns:
            The count of how many papers a mark for this question.

        Raises:
            None expected
        """
        service = MarkingTaskService()
        return service.get_tasks_from_question_with_annotation(
            question=question, version=version
        ).count()

    def get_student_info_from_paper(
        self,
        paper_num: int,
        version_info: bool,
        timing_info: bool,
        warning_info: bool,
    ) -> dict:
        """Get student info from a paper number.

        Args:
            paper_num: The paper number.
            version_info: Whether to include the version info.
            timing_info: Whether to include the timing info.
            warning_info: Whether to include the warning info.

        Returns:
            Dict keyed by string information about the student (i.e. "student_id": 1234, "q1_version" : 2).

        Raises:
            Paper.DoesNotExist: If the paper does not exist in the database.
        """
        try:
            paper_obj = Paper.objects.get(pk=paper_num)
        except Paper.DoesNotExist:
            raise Paper.DoesNotExist
        marking_tasks = paper_obj.markingtask_set.all()
        paper_id_task = PaperIDTask.objects.filter(paper=paper_obj).first()
        last_update = None

        student_info: Dict[str, Any] = {"paper_number": paper_num}

        # student info
        if paper_id_task:
            paper_id_action = PaperIDAction.objects.filter(task=paper_id_task).first()
            if paper_id_action:
                student_info.update(
                    {
                        "student_id": paper_id_action.student_id,
                        "student_name": paper_id_action.student_name,
                    }
                )

        # mark info
        total = 0
        for marking_task in marking_tasks.order_by("question_number"):
            current_annotation = marking_task.latest_annotation

            if current_annotation:
                student_info.update(
                    {
                        "q"
                        + str(marking_task.question_number)
                        + "_mark": current_annotation.score,
                    }
                )
                if version_info:
                    student_info.update(
                        {
                            "q"
                            + str(marking_task.question_number)
                            + "_version": marking_task.question_version,
                        }
                    )
                total += current_annotation.score
                last_update = current_annotation.time_of_last_update

        student_info.update(
            {
                "total_mark": total,
            }
        )

        if timing_info:
            student_info.update(
                {
                    "csv_write_time": arrow.utcnow().isoformat(" ", "seconds"),
                }
            )
            if last_update:
                student_info.update(
                    {
                        "last_update": arrow.get(last_update).isoformat(" ", "seconds"),
                    }
                )
        return student_info

    def get_all_students_download(
        self,
        version_info: bool,
        timing_info: bool,
        warning_info: bool,
    ) -> list:
        """Get the info for all students in a list for building a csv file to download.

        Args:
            version_info: Whether to include the version info.
            timing_info: Whether to include the timing info.
            warning_info: Whether to include the warning info.

        Returns:
            List where each element is a dictionary containing the information about an individual student.

        Raises:
            None expected
        """
        paper_nums = MarkingTask.objects.values_list(
            "paper__paper_number", flat=True
        ).distinct()
        csv_data = []
        for paper_num in paper_nums:
            csv_data.append(
                self.get_student_info_from_paper(
                    paper_num,
                    version_info,
                    timing_info,
                    warning_info,
                )
            )

        return csv_data

    def get_csv_header(
        self, spec, version_info: bool, timing_info: bool, warning_info: bool
    ) -> list:
        """Get the header for the csv file.

        Args:
            spec: The specification for the paper.
            version_info: Whether to include the version info.
            timing_info: Whether to include the timing info.
            warning_info: Whether to include the warning info.

        Returns:
            List holding the header for the csv file. Contains student info, marks,
            version info, timestamps and warnings.

        Raises:
            None expected
        """
        keys = ["student_id", "student_name", "paper_number"]
        for q in range(1, spec["numberOfQuestions"] + 1):
            keys.append("q" + str(q) + "_mark")
        keys.append("total_mark")
        if version_info:
            for q in range(1, spec["numberOfQuestions"] + 1):
                keys.append("q" + str(q) + "_version")
        if timing_info:
            keys.extend(["last_update", "csv_write_time"])
        if warning_info:
            keys.append("warnings")

        return keys
