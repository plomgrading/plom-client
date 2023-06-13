# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2023 Julian Lapenna

from django.contrib import admin

from Tags.models import Tag


admin.site.register(Tag)
