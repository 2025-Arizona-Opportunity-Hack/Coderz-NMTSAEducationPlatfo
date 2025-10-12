"""
Multi-tier search result aggregation for Supermemory
Combines course, module, and lesson search results with priority weighting
"""
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

# Priority weighting for different match types
COURSE_WEIGHT = 1.0   # Highest priority
MODULE_WEIGHT = 0.8   # Medium priority
LESSON_WEIGHT = 0.6   # Lowest priority


def aggregate_search_results(
    course_results: List[Dict[str, Any]],
    module_results: List[Dict[str, Any]],
    lesson_results: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """
    Aggregates multi-tier search results with priority weighting.

    Priority order: course > module > lesson
    - Course matches get score × 1.0
    - Module matches get score × 0.8 and mapped to parent course
    - Lesson matches get score × 0.6 and mapped to parent course

    For each course_slug, we keep the HIGHEST weighted score across all match types.

    Args:
        course_results: List of course search results from Supermemory
            [{"content": "...", "metadata": {"slug": "abc123", ...}, "score": 0.95}, ...]
        module_results: List of module search results
        lesson_results: List of lesson search results

    Returns:
        List of aggregated results sorted by score (descending)
        [{"slug": "abc123", "score": 0.95, "match_type": "course"}, ...]
    """
    try:
        # Dictionary to store best score for each course slug
        # Format: {course_slug: {"score": weighted_score, "match_type": "course|module|lesson"}}
        course_scores: Dict[str, Dict[str, Any]] = {}

        # Process course matches (highest priority)
        for result in course_results:
            try:
                metadata = result.get("metadata", {})
                slug = metadata.get("slug")
                score = result.get("score", 0)

                if not slug:
                    continue

                weighted_score = score * COURSE_WEIGHT

                # Update if this is the best score for this course
                if slug not in course_scores or weighted_score > course_scores[slug]["score"]:
                    course_scores[slug] = {
                        "score": weighted_score,
                        "match_type": "course",
                        "original_score": score,
                    }

            except Exception as e:
                logger.warning(f"Error processing course result: {e}")
                continue

        # Process module matches (medium priority)
        for result in module_results:
            try:
                metadata = result.get("metadata", {})
                course_slug = metadata.get("course_slug")
                score = result.get("score", 0)

                if not course_slug:
                    continue

                weighted_score = score * MODULE_WEIGHT

                # Update if this is the best score for this course
                if course_slug not in course_scores or weighted_score > course_scores[course_slug]["score"]:
                    course_scores[course_slug] = {
                        "score": weighted_score,
                        "match_type": "module",
                        "original_score": score,
                        "module_slug": metadata.get("slug"),
                    }

            except Exception as e:
                logger.warning(f"Error processing module result: {e}")
                continue

        # Process lesson matches (lowest priority)
        for result in lesson_results:
            try:
                metadata = result.get("metadata", {})
                course_slug = metadata.get("course_slug")
                score = result.get("score", 0)

                if not course_slug:
                    continue

                weighted_score = score * LESSON_WEIGHT

                # Update if this is the best score for this course
                if course_slug not in course_scores or weighted_score > course_scores[course_slug]["score"]:
                    course_scores[course_slug] = {
                        "score": weighted_score,
                        "match_type": "lesson",
                        "original_score": score,
                        "lesson_slug": metadata.get("slug"),
                        "module_slug": metadata.get("module_slug"),
                    }

            except Exception as e:
                logger.warning(f"Error processing lesson result: {e}")
                continue

        # Convert to list and sort by score (descending)
        results = [
            {"slug": slug, **data}
            for slug, data in course_scores.items()
        ]
        results.sort(key=lambda x: x["score"], reverse=True)

        logger.info(
            f"Aggregated {len(results)} course results from "
            f"{len(course_results)} courses, {len(module_results)} modules, "
            f"{len(lesson_results)} lessons"
        )

        return results

    except Exception as e:
        logger.error(f"Error aggregating search results: {e}")
        return []


def extract_course_slugs(aggregated_results: List[Dict[str, Any]]) -> List[str]:
    """
    Extract just the course slugs from aggregated results.

    Args:
        aggregated_results: Output from aggregate_search_results()

    Returns:
        List of course slugs in order of relevance
    """
    return [result["slug"] for result in aggregated_results]
