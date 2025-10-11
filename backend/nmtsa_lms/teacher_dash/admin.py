from django.contrib import admin
from .models import Course, Module, VideoLesson, BlogLesson, Lesson, DiscussionPost

# Register your models here.
admin.site.register(Course)
admin.site.register(Module)
admin.site.register(VideoLesson)
admin.site.register(BlogLesson)
admin.site.register(Lesson)
admin.site.register(DiscussionPost)
