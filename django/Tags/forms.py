# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2023 Julian Lapenna

from django import forms

from Mark.models.tasks import MarkingTaskTag


class TagFormFilter(forms.Form):
    tag_filter_text = forms.CharField(required=False, widget=forms.TextInput, label="Tag Text")
    strict_match = forms.BooleanField(required=False, label="Strict Match")


class TagEditForm(forms.ModelForm):
    class Meta:
        model = MarkingTaskTag
        fields = ["task", "text"]
        widgets = {
            "task": forms.TextInput(attrs={"rows": 10, "cols": 100}),
            "text": forms.Textarea(attrs={"rows": 10, "cols": 100}),
        }
