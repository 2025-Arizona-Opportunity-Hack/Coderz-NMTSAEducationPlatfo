"""
Chat API URLs
"""
from django.urls import path
from . import chat_views

urlpatterns = [
    # Conversations
    path('conversations', chat_views.get_conversations, name='chat-conversations'),
    path('conversations/<str:conversation_id>/messages', chat_views.get_messages, name='chat-messages'),
    path('conversations/<str:conversation_id>/typing', chat_views.get_typing_status, name='chat-typing-status'),
    path('conversations/<str:conversation_id>/typing', chat_views.update_typing_status, name='chat-update-typing'),
    path('conversations', chat_views.create_conversation, name='chat-create-conversation'),
    path('conversations/<str:conversation_id>', chat_views.delete_conversation, name='chat-delete-conversation'),
    
    # Messages
    path('messages', chat_views.send_message, name='chat-send-message'),
    path('messages/read', chat_views.mark_as_read, name='chat-mark-read'),
    
    # Unread count
    path('unread-count', chat_views.get_unread_count, name='chat-unread-count'),
]
