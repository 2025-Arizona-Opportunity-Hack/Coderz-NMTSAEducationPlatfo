from django.db import models


class CompletedLesson(models.Model):
	"""
	Tracks completion of individual lessons for a given enrollment.
	This enables accurate progress computation at the lesson level.
	"""
	enrollment = models.ForeignKey(
		'authentication.Enrollment',
		on_delete=models.CASCADE,
		related_name='completed_lessons'
	)
	lesson = models.ForeignKey(
		'teacher_dash.Lesson',
		on_delete=models.CASCADE,
		related_name='completions'
	)
	completed_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		db_table = 'completed_lessons'
		unique_together = ['enrollment', 'lesson']

	def __str__(self) -> str:
		return f"Enrollment {self.enrollment.pk} completed lesson {self.lesson.pk}"


class VideoProgress(models.Model):
	"""
	Tracks video playback progress for video lessons.
	Allows students to resume watching from where they left off.
	"""
	enrollment = models.ForeignKey(
		'authentication.Enrollment',
		on_delete=models.CASCADE,
		related_name='video_progress'
	)
	lesson = models.ForeignKey(
		'teacher_dash.Lesson',
		on_delete=models.CASCADE,
		related_name='video_progress'
	)
	last_position_seconds = models.IntegerField(
		default=0,
		help_text="Last watched position in seconds"
	)
	completed_percentage = models.IntegerField(
		default=0,
		help_text="Percentage of video watched (0-100)"
	)
	last_updated = models.DateTimeField(auto_now=True)

	class Meta:
		db_table = 'video_progress'
		unique_together = ['enrollment', 'lesson']

	def __str__(self) -> str:
		return f"Enrollment {self.enrollment.pk} - Lesson {self.lesson.pk}: {self.completed_percentage}%"


class ForumPost(models.Model):
	"""
	Forum post created by users to discuss topics, ask questions, etc.
	"""
	title = models.CharField(max_length=255)
	content = models.TextField()
	author = models.ForeignKey(
		'authentication.User',
		on_delete=models.CASCADE,
		related_name='forum_posts'
	)
	tags = models.JSONField(default=list, blank=True)
	is_pinned = models.BooleanField(default=False)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		db_table = 'forum_posts'
		ordering = ['-is_pinned', '-created_at']

	def __str__(self) -> str:
		return self.title

	@property
	def excerpt(self) -> str:
		"""Return first 200 characters of content"""
		return self.content[:200] + '...' if len(self.content) > 200 else self.content

	@property
	def comments_count(self) -> int:
		"""Count total comments on this post"""
		return self.comments.count()

	def get_likes_count(self) -> int:
		"""Count total likes on this post"""
		return self.likes.count()


class ForumComment(models.Model):
	"""
	Comment on a forum post
	"""
	post = models.ForeignKey(
		ForumPost,
		on_delete=models.CASCADE,
		related_name='comments'
	)
	content = models.TextField()
	author = models.ForeignKey(
		'authentication.User',
		on_delete=models.CASCADE,
		related_name='forum_comments'
	)
	parent = models.ForeignKey(
		'self',
		on_delete=models.CASCADE,
		null=True,
		blank=True,
		related_name='replies'
	)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		db_table = 'forum_comments'
		ordering = ['created_at']

	def __str__(self) -> str:
		return f"Comment on {self.post.title} by {self.author.email}"

	def get_likes_count(self) -> int:
		"""Count total likes on this comment"""
		return self.likes.count()


class ForumLike(models.Model):
	"""
	Like on a forum post or comment
	"""
	user = models.ForeignKey(
		'authentication.User',
		on_delete=models.CASCADE,
		related_name='forum_likes'
	)
	post = models.ForeignKey(
		ForumPost,
		on_delete=models.CASCADE,
		null=True,
		blank=True,
		related_name='likes'
	)
	comment = models.ForeignKey(
		ForumComment,
		on_delete=models.CASCADE,
		null=True,
		blank=True,
		related_name='likes'
	)
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		db_table = 'forum_likes'
		# Ensure user can only like a post or comment once
		unique_together = [
			['user', 'post'],
			['user', 'comment']
		]

	def __str__(self) -> str:
		if self.post:
			return f"{self.user.email} likes post {self.post.title}"
		return f"{self.user.email} likes comment {self.comment.pk}"
