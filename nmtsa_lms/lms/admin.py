from django.contrib import admin
from .models import CompletedLesson


@admin.register(CompletedLesson)
class CompletedLessonAdmin(admin.ModelAdmin):
	list_display = ("id", "enrollment", "lesson", "completed_at")
	list_filter = ("completed_at",)
	search_fields = ("enrollment__user__email", "lesson__title")
