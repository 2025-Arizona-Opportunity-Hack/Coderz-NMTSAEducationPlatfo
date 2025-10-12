from django.urls import path
from . import views

app_name = 'lms'

urlpatterns = [
    # Chat API endpoints
    path('api/chat/rooms/', views.chat_get_rooms, name='chat_get_rooms'),
    path('api/chat/rooms/<int:room_id>/messages/', views.chat_get_messages, name='chat_get_messages'),
    path('api/chat/rooms/<int:room_id>/send/', views.chat_send_message, name='chat_send_message'),
    path('api/chat/rooms/<int:room_id>/typing/', views.chat_update_typing, name='chat_update_typing'),
    path('api/chat/rooms/<int:room_id>/typing/status/', views.chat_get_typing, name='chat_get_typing'),
    
    # Course search with Supermemory
    path('api/courses/search/', views.search_courses_semantic, name='search_courses_semantic'),
]
