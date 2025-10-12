"""
Django signal handlers for automatic Supermemory indexing
Ensures course content is synchronized to Supermemory for search
"""
import logging
import time
from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver

from teacher_dash.models import Course, Module, Lesson, BlogLesson
from lms.supermemory_client import get_supermemory_client
from lms.course_indexer import (
    build_course_document,
    build_module_document,
    build_lesson_document,
    get_course_from_module,
    get_course_and_module_from_lesson,
)

logger = logging.getLogger(__name__)

# Retry configuration
MAX_RETRIES = 3
RETRY_DELAY_SECONDS = 1  # Initial delay, will exponentially backoff


def index_with_retry(index_func, *args, **kwargs):
    """
    Execute an indexing function with exponential backoff retry.

    Args:
        index_func: Function to call (e.g., client.index_course)
        *args, **kwargs: Arguments to pass to index_func

    Returns:
        Document ID if successful, None otherwise
    """
    for attempt in range(MAX_RETRIES):
        try:
            result = index_func(*args, **kwargs)
            if result:
                return result
            else:
                logger.warning(f"Indexing returned None on attempt {attempt + 1}")

        except Exception as e:
            logger.error(f"Indexing error on attempt {attempt + 1}/{MAX_RETRIES}: {e}")

        # Exponential backoff before retry
        if attempt < MAX_RETRIES - 1:
            delay = RETRY_DELAY_SECONDS * (2 ** attempt)
            time.sleep(delay)

    logger.error(f"Failed to index after {MAX_RETRIES} attempts")
    return None


def index_course_to_supermemory(course):
    """
    Index a course to Supermemory with retry logic.

    Args:
        course: Course model instance

    Returns:
        bool: True if successful, False otherwise
    """
    client = get_supermemory_client()
    if not client:
        logger.warning("Supermemory client not available, skipping course indexing")
        return False

    try:
        # Only index published courses
        if not course.is_published:
            logger.debug(f"Skipping unpublished course: {course.slug}")
            return True

        content, metadata = build_course_document(course)
        result = index_with_retry(client.index_course, content, metadata)

        if result:
            logger.info(f"Successfully indexed course: {course.slug}")
            return True
        else:
            logger.error(f"Failed to index course: {course.slug}")
            return False

    except Exception as e:
        logger.error(f"Error indexing course {course.slug}: {e}")
        return False


def index_module_to_supermemory(module, course):
    """
    Index a module to Supermemory with retry logic.

    Args:
        module: Module model instance
        course: Parent Course model instance

    Returns:
        bool: True if successful, False otherwise
    """
    client = get_supermemory_client()
    if not client:
        logger.warning("Supermemory client not available, skipping module indexing")
        return False

    try:
        # Only index modules of published courses
        if not course or not course.is_published:
            logger.debug(f"Skipping module of unpublished course: {module.slug}")
            return True

        content, metadata = build_module_document(module, course)
        result = index_with_retry(client.index_module, content, metadata)

        if result:
            logger.info(f"Successfully indexed module: {module.slug}")
            return True
        else:
            logger.error(f"Failed to index module: {module.slug}")
            return False

    except Exception as e:
        logger.error(f"Error indexing module {module.slug}: {e}")
        return False


def index_lesson_to_supermemory(lesson, module, course):
    """
    Index a lesson to Supermemory with retry logic.

    Args:
        lesson: Lesson model instance
        module: Parent Module model instance
        course: Parent Course model instance

    Returns:
        bool: True if successful, False otherwise
    """
    client = get_supermemory_client()
    if not client:
        logger.warning("Supermemory client not available, skipping lesson indexing")
        return False

    try:
        # Only index lessons of published courses
        if not course or not course.is_published:
            logger.debug(f"Skipping lesson of unpublished course: {lesson.slug}")
            return True

        content, metadata = build_lesson_document(lesson, module, course)
        result = index_with_retry(client.index_lesson, content, metadata)

        if result:
            logger.info(f"Successfully indexed lesson: {lesson.slug}")
            return True
        else:
            logger.error(f"Failed to index lesson: {lesson.slug}")
            return False

    except Exception as e:
        logger.error(f"Error indexing lesson {lesson.slug}: {e}")
        return False


# ========== Signal Handlers ==========

@receiver(post_save, sender=Course)
def course_post_save(sender, instance, created, **kwargs):
    """
    Index course to Supermemory after save.
    Runs after transaction commits to ensure data consistency.
    """
    def index_on_commit():
        # Index the course
        index_course_to_supermemory(instance)

        # Also re-index all modules for this course
        for module in instance.modules.all():
            index_module_to_supermemory(module, instance)

            # Re-index all lessons for this module
            for lesson in module.lessons.all():
                index_lesson_to_supermemory(lesson, module, instance)

    # Execute indexing after transaction commits
    transaction.on_commit(index_on_commit)


@receiver(post_save, sender=Module)
def module_post_save(sender, instance, created, **kwargs):
    """
    Index module to Supermemory after save.
    Also re-indexes parent course to update module list.
    """
    def index_on_commit():
        # Get parent course
        course = get_course_from_module(instance)
        if not course:
            logger.warning(f"Module {instance.slug} has no parent course, skipping indexing")
            return

        # Index the module
        index_module_to_supermemory(instance, course)

        # Re-index parent course (to update module list)
        index_course_to_supermemory(course)

        # Re-index all lessons for this module
        for lesson in instance.lessons.all():
            index_lesson_to_supermemory(lesson, instance, course)

    transaction.on_commit(index_on_commit)


@receiver(post_save, sender=Lesson)
def lesson_post_save(sender, instance, created, **kwargs):
    """
    Index lesson to Supermemory after save.
    Also re-indexes parent module and course.
    """
    def index_on_commit():
        # Get parent module and course
        module, course = get_course_and_module_from_lesson(instance)
        if not module or not course:
            logger.warning(f"Lesson {instance.slug} has no parent module/course, skipping indexing")
            return

        # Index the lesson
        index_lesson_to_supermemory(instance, module, course)

        # Re-index parent module (to update lesson list)
        index_module_to_supermemory(module, course)

        # Re-index parent course (to update lesson count in modules)
        index_course_to_supermemory(course)

    transaction.on_commit(index_on_commit)


@receiver(post_save, sender=BlogLesson)
def blog_lesson_post_save(sender, instance, created, **kwargs):
    """
    Re-index parent lesson after BlogLesson content changes.
    This ensures blog content is searchable.
    """
    def index_on_commit():
        lesson = instance.lesson

        # Get parent module and course
        module, course = get_course_and_module_from_lesson(lesson)
        if not module or not course:
            logger.warning(f"BlogLesson for lesson {lesson.slug} has no parent module/course")
            return

        # Re-index the lesson (includes updated blog content)
        index_lesson_to_supermemory(lesson, module, course)

        # Re-index parent module
        index_module_to_supermemory(module, course)

        # Re-index parent course
        index_course_to_supermemory(course)

    transaction.on_commit(index_on_commit)
