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
