"""
Course memory management utilities
Automatically sync course data to Supermemory for semantic search
Uses custom_id for idempotent upserts (same ID = update, not duplicate)
"""
import logging
from typing import Dict, Any
from .supermemory_client import get_supermemory_client

logger = logging.getLogger(__name__)


def add_course_to_memory(course_data: Dict[str, Any]) -> bool:
    """
    Add or update course in Supermemory for semantic search
    
    Uses custom_id to ensure idempotent operations - same course_id will UPDATE
    the existing memory instead of creating duplicates.
    
    Args:
        course_data: Dictionary containing course information
            - id: Course ID (required)
            - title: Course title
            - description: Course description
            - tags: List of tags
            - modules: List of module info
            - is_paid: Whether course is paid
            - is_published: Whether course is published
            
    Returns:
        True if successful, False otherwise
    """
    supermemory = get_supermemory_client()
    
    if not supermemory:
        logger.warning("Supermemory client not available")
        return False
    
    course_id = course_data.get('id')
    if not course_id:
        logger.error("Course ID is required for memory operations")
        return False
    
    try:
        # Format course content for semantic search
        title = course_data.get('title', 'Untitled Course')
        description = course_data.get('description', 'No description available')
        tags = course_data.get('tags', [])
        modules = course_data.get('modules', [])
        is_paid = course_data.get('is_paid', False)
        
        # Create rich content for better semantic matching
        content_parts = [
            f"Course Title: {title}",
            f"\nDescription: {description}",
        ]
        
        if tags:
            content_parts.append(f"\nTopics: {', '.join(tags)}")
        
        if modules:
            module_titles = [m.get('title', '') for m in modules if m.get('title')]
            if module_titles:
                content_parts.append(f"\nModules: {', '.join(module_titles)}")
        
        content_parts.append(f"\nCourse Type: {'Paid' if is_paid else 'Free'} Neurologic Music Therapy Education")
        
        content = ''.join(content_parts).strip()
        
        # Add to Supermemory with custom_id for upserts
        result = supermemory.add_memory(
            content=content,
            metadata={
                'type': 'course',
                'course_id': str(course_id),
                'title': title,
                'is_paid': is_paid,
                'is_published': course_data.get('is_published', False),
                'tags': tags[:5] if len(tags) > 5 else tags  # Limit tags
            },
            container_tag='nmtsa-courses',
            custom_id=f"course-{course_id}"  # Enables idempotent upserts
        )
        
        if result:
            logger.info(f"Successfully added/updated course {course_id} to memory")
            return True
        else:
            logger.warning(f"Failed to add course {course_id} to memory")
            return False
        
    except Exception as e:
        logger.error(f"Error adding course to memory: {e}")
        return False


def update_course_in_memory(course_id: int, course_data: Dict[str, Any]) -> bool:
    """
    Update course information in Supermemory
    
    Since we use custom_id, calling add_course_to_memory with the same course_id
    will automatically UPDATE the existing memory instead of creating duplicates.
    This is the idempotent upsert behavior.
    
    Args:
        course_id: Course ID
        course_data: Updated course information
        
    Returns:
        True if successful, False otherwise
    """
    course_data['id'] = course_id
    return add_course_to_memory(course_data)


def remove_course_from_memory(course_id: int) -> bool:
    """
    Remove course from Supermemory (when deleted or unpublished)
    
    Note: Current implementation is a placeholder. To fully implement:
    1. Search for memory by metadata (course_id)
    2. Delete by memory ID using client.memories.delete()
    
    Args:
        course_id: Course ID to remove
        
    Returns:
        True if successful, False otherwise
    """
    supermemory = get_supermemory_client()
    
    if not supermemory:
        logger.warning("Supermemory client not available")
        return False
    
    try:
        # TODO: Implement actual deletion
        # Would need to:
        # 1. Search for the memory with course_id metadata
        # 2. Extract the memory ID
        # 3. Call memory_client.memories.delete(memory_id)
        
        logger.info(f"Course {course_id} removal from memory (placeholder)")
        return True
        
    except Exception as e:
        logger.error(f"Error removing course from memory: {e}")
        return False


def add_website_info_to_memory() -> bool:
    """
    Add general NMTSA LMS website information to memory
    This provides context for the chatbot about the platform itself
    
    Returns:
        True if successful, False otherwise
    """
    supermemory = get_supermemory_client()
    
    if not supermemory:
        logger.warning("Supermemory client not available")
        return False
    
    website_info = """
NMTSA LMS - Neurologic Music Therapy Student Association Learning Management System

About the Platform:
The NMTSA LMS is a comprehensive learning management system designed specifically for neurologic music therapy education. It serves healthcare professionals, therapists, students, and families interested in special needs therapy.

Key Features:
- Dual Authentication: OAuth (Auth0) for students and teachers, Django admin for administrators
- Course Management: Teachers can create, publish, and manage comprehensive courses
- Student Progress Tracking: Automatic progress calculation, completed lessons tracking, video position memory
- Autism-Friendly UI: High contrast themes, adjustable fonts, zero animations, WCAG 2.1 AAA compliant
- Video Lessons: Built-in video player with progress tracking and resume functionality
- Blog Lessons: Rich text content with images for written educational materials
- Discussion Forums: Course-specific discussions for student engagement
- Teacher Verification: Admin-approved teacher verification system

User Roles:
1. Students/Families: Can enroll in courses, track progress, participate in discussions
2. Teachers/Educators: Can create courses (after verification), upload lessons, manage content
3. Administrators: Verify teachers, review courses before publication, manage platform

Course Features:
- Modular structure: Courses contain modules, modules contain lessons
- Two lesson types: Video lessons with transcripts, Blog lessons with rich content
- Tags and categories for easy discovery
- Both free and paid courses available
- Admin review required before courses go live

Enrollment Process:
1. Browse available courses
2. Click "Enroll" on course page
3. For paid courses: Complete PayPal payment
4. Access course content immediately
5. Progress is automatically tracked

Getting Started:
- Sign up via the main page
- Choose your role (Student/Family or Educator/Therapist)
- Complete onboarding
- For students: Start browsing courses
- For teachers: Submit credentials for verification

Support:
- Use the chat assistant for questions
- Contact admin for technical issues
- FAQ section available on website
"""
    
    try:
        result = supermemory.add_memory(
            content=website_info.strip(),
            metadata={
                'type': 'website_info',
                'category': 'platform_documentation'
            },
            container_tag='nmtsa-website',
            custom_id='nmtsa-website-info'
        )
        
        if result:
            logger.info("Successfully added website info to memory")
            return True
        else:
            logger.warning("Failed to add website info to memory")
            return False
            
    except Exception as e:
        logger.error(f"Error adding website info to memory: {e}")
        return False
