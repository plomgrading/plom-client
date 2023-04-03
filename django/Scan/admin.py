# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2022 Edith Coates
# Copyright (C) 2022-2023 Brennen Chiu
# Copyright (C) 2023 Andrew Rechnitzer

from django.contrib import admin
from .models import (
    StagingBundle,
    StagingImage,
    PageToImage,
    ParseQR,
    KnownStagingImage,
    UnknownStagingImage,
    ExtraStagingImage,
    ErrorStagingImage,
    DiscardStagingImage,
)

# Register your models here.
admin.site.register(StagingBundle)
admin.site.register(StagingImage)
admin.site.register(KnownStagingImage)
admin.site.register(ExtraStagingImage)
admin.site.register(DiscardStagingImage)
admin.site.register(UnknownStagingImage)
admin.site.register(PageToImage)
admin.site.register(ParseQR)
