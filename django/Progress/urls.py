# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2022-2023 Edith Coates
# Copyright (C) 2022-2023 Brennen Chiu
# Copyright (C) 2023 Andrew Rechnitzer

from django.urls import path

from Progress.views import (
    ScanOverview,
    ScanBundlesView,
    ScanCompleteView,
    ScanInCompleteView,
    PushedImageView,
    PushedImageWrapView,
    ProgressIdentifyHome,
    ProgressMarkHome,
    ProgressUserInfoHome,
    IDImageView,
    IDImageWrapView,
)


urlpatterns = [
    path("scan/overview/", ScanOverview.as_view(), name="progress_scan_overview"),
    path("scan/bundles/", ScanBundlesView.as_view(), name="progress_scan_bundles"),
    path("scan/complete/", ScanCompleteView.as_view(), name="progress_scan_complete"),
    path(
        "scan/incomplete/",
        ScanInCompleteView.as_view(),
        name="progress_scan_incomplete",
    ),
    path(
        "scan/pushed_img/<int:img_pk>",
        PushedImageView.as_view(),
        name="progress_pushed_img",
    ),
    path(
        "scan/pushed_img_wrap/<int:img_pk>",
        PushedImageWrapView.as_view(),
        name="progress_pushed_img_wrap",
    ),
    path(
        "mark/overview/",
        ProgressMarkHome.as_view(),
        name="progress_mark_home",
    ),
    path(
        "identify/overview/",
        ProgressIdentifyHome.as_view(),
        name="progress_identify_home",
    ),
    path(
        "identify/overview/id_img/<int:image_pk>",
        IDImageView.as_view(),
        name="ID_img",
    ),
    path(
        "identify/overview/id_img_wrap/<int:image_pk>",
        IDImageWrapView.as_view(),
        name="ID_img_wrap",
    ),
    path(
        "userinfo/overview/",
        ProgressUserInfoHome.as_view(),
        name="progress_user_info_home",
    ),
]
