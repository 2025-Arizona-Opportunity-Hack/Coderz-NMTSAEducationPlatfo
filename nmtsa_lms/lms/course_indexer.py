"""
Course Content Indexer for Supermemory
Builds searchable documents from Course, Module, and Lesson models
"""
from typing import Dict, Any, Tuple, List
import logging

logger = logging.getLogger(__name__)


def build_course_document(course) -> Tuple[str, Dict[str, Any]]:
    """
    Build a searchable document for a course.

    Args:
        course: Course model instance

    Returns:
        Tuple of (content, metadata)
        - content: Searchable text content
        - metadata: Dict with course metadata for filtering
    """
    try:
        # Build searchable content
        content_parts = [
            f"Course: {course.title}",
            f"Description: {course.description}",
        ]

        # Add tags if available
        if course.tags.exists():
            tags_list = [tag.name for tag in course.tags.all()]
            content_parts.append(f"Tags: {', '.join(tags_list)}")

        # Add module titles for context
        if course.modules.exists():
            module_titles = [m.title for m in course.modules.all()]
            content_parts.append(f"Modules: {', '.join(module_titles)}")

        content = "\n\n".join(content_parts)

        # Build metadata
        metadata = {
            "type": "course",
            "slug": course.slug,
            "title": course.title,
            "is_published": course.is_published,
            "is_paid": course.is_paid,
            "tags": [tag.name for tag in course.tags.all()] if course.tags.exists() else [],
            "teacher_id": str(course.published_by.id) if course.published_by else None,
        }

        return content, metadata

    except Exception as e:
        logger.error(f"Error building course document for course {getattr(course, 'id', 'unknown')}: {e}")
        raise


def build_module_document(module, course) -> Tuple[str, Dict[str, Any]]:
    """
    Build a searchable document for a module.

    Args:
        module: Module model instance
        course: Parent Course model instance

    Returns:
        Tuple of (content, metadata)
    """
    try:
        # Build searchable content
        content_parts = [
            f"Module: {module.title}",
            f"Description: {module.description}",
            f"Part of Course: {course.title}",
        ]

        # Add tags if available
        if module.tags.exists():
            tags_list = [tag.name for tag in module.tags.all()]
            content_parts.append(f"Tags: {', '.join(tags_list)}")

        # Add lesson titles for context
        if module.lessons.exists():
            lesson_titles = [l.title for l in module.lessons.all()]
            content_parts.append(f"Lessons: {', '.join(lesson_titles)}")

        content = "\n\n".join(content_parts)

        # Build metadata
        metadata = {
            "type": "module",
            "slug": module.slug,
            "course_slug": course.slug,
            "title": module.title,
            "course_title": course.title,
            "tags": [tag.name for tag in module.tags.all()] if module.tags.exists() else [],
        }

        return content, metadata

    except Exception as e:
        logger.error(f"Error building module document for module {getattr(module, 'id', 'unknown')}: {e}")
        raise


def build_lesson_document(lesson, module, course) -> Tuple[str, Dict[str, Any]]:
    """
    Build a searchable document for a lesson.

    For BlogLesson: includes full blog content
    For VideoLesson: includes only title and tags (NO transcript, NO video content)

    Args:
        lesson: Lesson model instance
        module: Parent Module model instance
        course: Parent Course model instance

    Returns:
        Tuple of (content, metadata)
    """
    try:
        # Build searchable content
        content_parts = [
            f"Lesson: {lesson.title}",
            f"Type: {lesson.get_lesson_type_display()}",
            f"Part of Module: {module.title}",
            f"Part of Course: {course.title}",
        ]

        # Add tags if available
        if lesson.tags.exists():
            tags_list = [tag.name for tag in lesson.tags.all()]
            content_parts.append(f"Tags: {', '.join(tags_list)}")

        # Add blog content if it's a blog lesson
        if lesson.lesson_type == 'blog':
            try:
                blog = lesson.blog
                if blog and blog.content:
                    content_parts.append(f"Content: {blog.content}")
            except Exception:
                # blog relation doesn't exist or error accessing it
                pass

        # For video lessons, do NOT add transcript or video content
        # Just title and tags (already added above)

        content = "\n\n".join(content_parts)

        # Build metadata
        metadata = {
            "type": "lesson",
            "slug": lesson.slug,
            "module_slug": module.slug,
            "course_slug": course.slug,
            "lesson_type": lesson.lesson_type,
            "title": lesson.title,
            "module_title": module.title,
            "course_title": course.title,
            "tags": [tag.name for tag in lesson.tags.all()] if lesson.tags.exists() else [],
        }

        return content, metadata

    except Exception as e:
        logger.error(f"Error building lesson document for lesson {getattr(lesson, 'id', 'unknown')}: {e}")
        raise


def get_course_from_module(module) -> Any:
    """
    Get the parent course for a module.

    Args:
        module: Module model instance

    Returns:
        Course model instance or None
    """
    try:
        # Module has ManyToMany relationship with Course
        # Get the first course (in practice, modules should belong to one course)
        return module.course_set.first()
    except Exception as e:
        logger.error(f"Error getting course from module {getattr(module, 'id', 'unknown')}: {e}")
        return None


def get_course_and_module_from_lesson(lesson) -> Tuple[Any, Any]:
    """
    Get the parent module and course for a lesson.

    Args:
        lesson: Lesson model instance

    Returns:
        Tuple of (module, course) or (None, None)
    """
    try:
        # Lesson has ManyToMany relationship with Module
        # Get the first module (in practice, lessons should belong to one module)
        module = lesson.module_set.first()
        if not module:
            return None, None

        # Get course from module
        course = get_course_from_module(module)
        return module, course

    except Exception as e:
        logger.error(f"Error getting course/module from lesson {getattr(lesson, 'id', 'unknown')}: {e}")
        return None, None
