from django.db import models
from django.conf import settings
from taggit.managers import TaggableManager


class Course(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    published_date = models.DateTimeField(auto_now_add=True)
    is_published = models.BooleanField(default=False)
    num_enrollments = models.IntegerField(default=0)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    is_paid = models.BooleanField(default=False)
    is_submitted_for_review = models.BooleanField(default=False)
    admin_review_feedback = models.TextField(blank=True, null=True, help_text="Optional feedback from admin during course review")
    admin_approved = models.BooleanField(default=False, help_text="Indicates if the course has been approved by an admin")
    published_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    modules = models.ManyToManyField('Module', blank=True)
    tags = TaggableManager(blank=True)

    class Meta:
        db_table = 'courses'

    def __str__(self):
        return self.title


class Module(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    lessons = models.ManyToManyField('Lesson', blank=True)
    tags = TaggableManager(blank=True)

    class Meta:
        db_table = 'modules'

    def __str__(self):
        return self.title


class Lesson(models.Model):
    LESSON_TYPES = [
        ('video', 'Video'),
        ('blog', 'Blog'),
    ]
    title = models.CharField(max_length=200)
    lesson_type = models.CharField(max_length=10, choices=LESSON_TYPES)
    duration = models.IntegerField(help_text="Expected duration in minutes", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    tags = TaggableManager(blank=True)

    class Meta:
        db_table = 'lessons'

    def __str__(self):
        return self.title

class DiscussionPost(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='discussions')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='discussion_posts')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Threading support - parent post for replies
    parent_post = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='replies')

    # Moderation and metadata
    is_pinned = models.BooleanField(default=False, help_text="Pinned posts appear at the top")
    is_edited = models.BooleanField(default=False, help_text="Indicates if post was edited after creation")
    edited_at = models.DateTimeField(null=True, blank=True, help_text="Timestamp of last edit")

    class Meta:
        db_table = 'discussions'
        ordering = ['-is_pinned', '-created_at']
        indexes = [
            models.Index(fields=['course', '-created_at']),
            models.Index(fields=['parent_post']),
        ]

    def __str__(self):
        post_type = "Reply" if self.parent_post else "Post"
        return f"{post_type} by {self.user.get_full_name() or self.user.username} in {self.course.title}"

    def can_edit(self, user):
        """Check if a user can edit this post"""
        from django.utils import timezone
        from datetime import timedelta

        # Admins can edit any post
        if hasattr(user, 'is_admin_user') and user.is_admin_user:
            return True

        # Course teacher can edit any post in their course
        if self.course.published_by == user:
            return True

        # Users can edit their own posts within 24 hours
        if self.user == user:
            time_limit = self.created_at + timedelta(hours=24)
            if timezone.now() <= time_limit:
                return True

        return False

    def can_delete(self, user, course=None):
        """Check if a user can delete this post"""
        # Admins can delete any post
        if hasattr(user, 'is_admin_user') and user.is_admin_user:
            return True

        # Course teacher can delete any post in their course
        if self.course.published_by == user:
            return True

        # Users can delete their own posts
        if self.user == user:
            return True

        return False

    def can_pin(self, user):
        """Check if a user can pin this post"""
        # Only admins and course teacher can pin posts
        if hasattr(user, 'is_admin_user') and user.is_admin_user:
            return True

        if self.course.published_by == user:
            return True

        return False

    def get_replies(self):
        """Get all direct replies to this post"""
        return self.replies.all().select_related('user').order_by('created_at')

    def get_reply_count(self):
        """Get the count of direct replies"""
        return self.replies.count()

    @property
    def is_reply(self):
        """Check if this is a reply to another post"""
        return self.parent_post is not None

class VideoLesson(models.Model):
    lesson = models.OneToOneField(Lesson, on_delete=models.CASCADE, related_name='video')
    video_file = models.FileField(upload_to='videos/')
    transcript = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'video_lessons'

    def __str__(self):
        return f"Video: {self.lesson.title}"


class BlogLesson(models.Model):
    lesson = models.OneToOneField(Lesson, on_delete=models.CASCADE, related_name='blog')
    content = models.TextField()
    images = models.ImageField(upload_to='blog_images/', blank=True, null=True)

    class Meta:
        db_table = 'blog_lessons'

    def __str__(self):
        return f"Blog: {self.lesson.title}"