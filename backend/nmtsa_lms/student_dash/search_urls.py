"""
URL Configuration for AI-powered search endpoints
"""
from django.urls import path
from . import search_views

urlpatterns = [
    path('courses/contextual/', search_views.contextual_course_search, name='contextual_course_search'),
    path('courses/recommendations/', search_views.get_course_recommendations, name='course_recommendations'),
]
