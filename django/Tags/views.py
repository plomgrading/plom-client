# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2023 Julian Lapenna

from django.shortcuts import render, redirect

from Base.base_group_views import ManagerRequiredView
from Tags.forms import TagFormFilter, TagEditForm
from Tags.services.tag_service import TagService


class TagLandingPageView(ManagerRequiredView):
    """A landing page for displaying and analyzing papers by tag."""

    template_name = "Tags/tags_landing.html"
    ts = TagService()
    form = TagEditForm

    def get(self, request):
        context = self.build_context()
        text_field_form = TagFormFilter()

        tag_filter_text = request.session.get("tag_filter_text", "")
        tag_filter_strict = request.session.get("strict_match", "off")

        text_field_form.fields["tag_filter_text"].initial = tag_filter_text
        text_field_form.fields["strict_match"].initial = False
        if tag_filter_strict == "on":
            text_field_form.fields["strict_match"].initial = True

        if tag_filter_strict == "on":
            task_tags = self.ts.get_task_tags_with_tag_exact(tag_filter_text)
        else:
            task_tags = self.ts.get_task_tags_with_tag(tag_filter_text)

        papers = self.ts.get_papers_from_task_tags(task_tags)
        tag_counts = self.ts.get_task_tags_counts()

        context.update(
            {
                "tag_count": task_tags.__len__(),
                "task_tags": task_tags,
                "papers": papers,
                "tag_counts": tag_counts,
                "text_field_form": text_field_form,
                "tag_filter_text": tag_filter_text,
                "tag_filter_strict": tag_filter_strict,
            }
        )
        print("PAPERS: ", papers)

        return render(request, self.template_name, context=context)

    def tag_filter(request):
        """Filter papers by tag."""
        request.session["tag_filter_text"] = request.POST.get("tag_filter_text", "")
        request.session["strict_match"] = request.POST.get("strict_match", "off")

        return redirect("tags_landing")


class TagItemView(ManagerRequiredView):
    """A page for displaying a single tag and related information."""

    template_name = "Tags/tag_item.html"
    ts = TagService()
    form = TagEditForm

    def get(self, request, tag_id):
        context = self.build_context()

        print(request)
        print("GET: ", request.GET)
        print("POST: ", request.POST)

        tag = self.ts.get_tag_from_id(tag_id=tag_id)
        context.update({"tag": tag, "form": self.form(instance=tag)})

        return render(request, self.template_name, context=context)

    def post(request, tag_id):
        form = TagEditForm(request.POST)

        if form.is_valid():
            tag = TagItemView.ts.get_tag_from_id(tag_id=tag_id)
            for key, value in form.cleaned_data.items():
                tag.__setattr__(key, value)
            tag.save()
        return redirect("tag_item", tag_id=tag_id)

    def tag_delete(request, tag_id):
        """Delete a tag."""
        TagItemView.ts.delete_tag(tag_id=tag_id)
        return redirect("tags_landing")
