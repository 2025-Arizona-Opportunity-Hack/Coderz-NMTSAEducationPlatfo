from django.urls import path

from . import views


urlpatterns = [
    path("", views.dashboard, name="teacher_dashboard"),
    path("courses/", views.courses, name="teacher_courses"),
    path("courses/create/", views.course_create, name="teacher_create_course"),
    path("courses/<slug:course_slug>/", views.course_detail, name="teacher_course_detail"),
    path("courses/<slug:course_slug>/edit/", views.course_edit, name="teacher_course_edit"),
    path("courses/<slug:course_slug>/delete/", views.course_delete, name="teacher_course_delete"),
    path("courses/<slug:course_slug>/publish/", views.course_publish, name="teacher_course_publish"),
    path("courses/<slug:course_slug>/unpublish/", views.course_unpublish, name="teacher_course_unpublish"),
    path("courses/<slug:course_slug>/modules/add/", views.module_create, name="teacher_module_create"),
    path("courses/<slug:course_slug>/modules/<slug:module_slug>/", views.module_detail, name="teacher_module_detail"),
    path("courses/<slug:course_slug>/modules/<slug:module_slug>/edit/", views.module_edit, name="teacher_module_edit"),
    path("courses/<slug:course_slug>/modules/<slug:module_slug>/delete/", views.module_delete, name="teacher_module_delete"),
    path(
        "courses/<slug:course_slug>/modules/<slug:module_slug>/lessons/add/",
        views.lesson_create,
        name="teacher_lesson_create",
    ),
    path(
        "courses/<slug:course_slug>/modules/<slug:module_slug>/lessons/<slug:lesson_slug>/edit/",
        views.lesson_edit,
        name="teacher_lesson_edit",
    ),
    path(
        "courses/<slug:course_slug>/modules/<slug:module_slug>/lessons/<slug:lesson_slug>/delete/",
        views.lesson_delete,
        name="teacher_lesson_delete",
    ),
    path(
        "courses/<slug:course_slug>/modules/<slug:module_slug>/lessons/<slug:lesson_slug>/preview/",
        views.lesson_preview,
        name="teacher_lesson_preview",
    ),
    path("courses/<slug:course_slug>/preview/", views.course_preview, name="teacher_course_preview"),
    path("videos/<path:video_path>", views.serve_video, name="serve_video"),
    path("courses/<slug:course_slug>/analytics/", views.course_analytics, name="teacher_course_analytics"),
    path("verification/", views.verification_status, name="teacher_verification_status"),
    path("export/", views.export_courses, name="teacher_export_courses"),
    # Discussion board
    path("courses/<slug:course_slug>/discussions/", views.course_discussions, name="teacher_course_discussions"),
    path("courses/<slug:course_slug>/discussions/create/", views.discussion_create, name="teacher_discussion_create"),
    path("courses/<slug:course_slug>/discussions/<int:post_id>/", views.discussion_detail, name="teacher_discussion_detail"),
    path("courses/<slug:course_slug>/discussions/<int:post_id>/reply/", views.discussion_reply, name="teacher_discussion_reply"),
    path("courses/<slug:course_slug>/discussions/<int:post_id>/edit/", views.discussion_edit, name="teacher_discussion_edit"),
    path("courses/<slug:course_slug>/discussions/<int:post_id>/delete/", views.discussion_delete, name="teacher_discussion_delete"),
    path("courses/<slug:course_slug>/discussions/<int:post_id>/pin/", views.discussion_pin_toggle, name="teacher_discussion_pin"),
]
