from django.db import models
from django.conf import settings


class ChatRoom(models.Model):
	"""
	Represents a chat room (direct message, group, or support chat).
	"""
	ROOM_TYPE_CHOICES = [
		('direct', 'Direct Message'),
		('group', 'Group Chat'),
		('support', 'Support Chat'),
	]
	
	name = models.CharField(
		max_length=200,
		help_text="Chat room name (auto-generated for direct chats)"
	)
	room_type = models.CharField(
		max_length=10,
		choices=ROOM_TYPE_CHOICES,
		default='direct'
	)
	participants = models.ManyToManyField(
		settings.AUTH_USER_MODEL,
		related_name='chat_rooms',
		help_text="Users in this chat room"
	)
	created_at = models.DateTimeField(auto_now_add=True)
	is_active = models.BooleanField(default=True)
	
	class Meta:
		db_table = 'chat_rooms'
		ordering = ['-created_at']
	
	def __str__(self):
		return f"{self.get_room_type_display()}: {self.name}"
	
	@property
	def last_message(self):
		"""Get the most recent message in this room"""
		return self.messages.order_by('-timestamp').first()


class ChatMessage(models.Model):
	"""
	Individual messages within a chat room.
	"""
	MESSAGE_TYPE_CHOICES = [
		('text', 'Text Message'),
		('system', 'System Message'),
		('notification', 'Notification'),
	]
	
	room = models.ForeignKey(
		ChatRoom,
		on_delete=models.CASCADE,
		related_name='messages'
	)
	sender = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		on_delete=models.CASCADE,
		related_name='sent_messages'
	)
	content = models.TextField(
		max_length=2000,
		help_text="Message content"
	)
	message_type = models.CharField(
		max_length=15,
		choices=MESSAGE_TYPE_CHOICES,
		default='text'
	)
	timestamp = models.DateTimeField(auto_now_add=True)
	is_read = models.BooleanField(default=False)
	
	class Meta:
		db_table = 'chat_messages'
		ordering = ['timestamp']
		indexes = [
			models.Index(fields=['room', '-timestamp']),
			models.Index(fields=['sender', '-timestamp']),
		]
	
	def __str__(self):
		return f"{self.sender.get_full_name()} in {self.room.name}: {self.content[:50]}"


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
