from django.contrib import admin
from .models import CompletedLesson, ForumPost, ForumComment, ForumLike


@admin.register(CompletedLesson)
class CompletedLessonAdmin(admin.ModelAdmin):
	list_display = ("id", "enrollment", "lesson", "completed_at")
	list_filter = ("completed_at",)
	search_fields = ("enrollment__user__email", "lesson__title")


@admin.register(ForumPost)
class ForumPostAdmin(admin.ModelAdmin):
	list_display = ("id", "title", "author", "is_pinned", "created_at")
	list_filter = ("is_pinned", "created_at")
	search_fields = ("title", "content", "author__email")
	readonly_fields = ("created_at", "updated_at")


@admin.register(ForumComment)
class ForumCommentAdmin(admin.ModelAdmin):
	list_display = ("id", "post", "author", "parent", "created_at")
	list_filter = ("created_at",)
	search_fields = ("content", "author__email", "post__title")
	readonly_fields = ("created_at", "updated_at")


@admin.register(ForumLike)
class ForumLikeAdmin(admin.ModelAdmin):
	list_display = ("id", "user", "post", "comment", "created_at")
	list_filter = ("created_at",)
	search_fields = ("user__email",)
	readonly_fields = ("created_at",)
