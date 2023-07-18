# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2023 Divy Patel

import json
from django.shortcuts import render

from Base.base_group_views import ManagerRequiredView


class HistogramView(ManagerRequiredView):
    """Histogram view for D3.js."""

    template_name = "Visualization/histogram.html"

    def get(self, request):
        return render(request, self.template_name)


class HeatMapView(ManagerRequiredView):
    """Heat map view for D3.js."""

    template_name = "Visualization/heat_map.html"

    def get(self, request):
        return render(request, self.template_name)
