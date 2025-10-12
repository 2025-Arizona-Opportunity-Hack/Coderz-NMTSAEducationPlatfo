"""
Course memory management utilities
Automatically sync course data to Supermemory for semantic search
"""
from typing import Dict, Any
from .supermemory_client import get_supermemory_client


def add_course_to_memory(course_data: Dict[str, Any]) -> bool:
    """
    Add or update course in Supermemory for semantic search
    
    Args:
        course_data: Dictionary containing course information
            - id: Course ID
            - title: Course title
            - description: Course description
            - tags: List of tags
            - modules: List of module info
            
    Returns:
        True if successful, False otherwise
    """
    supermemory = get_supermemory_client()
    
    if not supermemory:
        return False
    
    try:
        # Format course content for memory
        content = f"""
Course: {course_data.get('title', 'Untitled')}

Description: {course_data.get('description', 'No description')}

Tags: {', '.join(course_data.get('tags', []))}

Modules: {', '.join([m.get('title', '') for m in course_data.get('modules', [])])}

Type: Music Therapy Education
Category: {course_data.get('category', 'General')}
"""
        
        # Add to Supermemory with metadata
        result = supermemory.add_memory(
            content=content.strip(),
            metadata={
                'type': 'course',
                'course_id': str(course_data.get('id')),
                'title': course_data.get('title'),
                'is_paid': course_data.get('is_paid', False),
                'is_published': course_data.get('is_published', False),
                'tags': course_data.get('tags', [])
            }
        )
        
        return not result.get('error')
        
    except Exception as e:
        print(f"[Memory] Error adding course to memory: {e}")
        return False


def update_course_in_memory(course_id: int, course_data: Dict[str, Any]) -> bool:
    """
    Update course information in Supermemory
    
    Args:
        course_id: Course ID
        course_data: Updated course information
        
    Returns:
        True if successful, False otherwise
    """
    # For now, we'll just add it again (Supermemory handles duplicates)
    # In production, you might want to fetch and update the specific memory
    course_data['id'] = course_id
    return add_course_to_memory(course_data)


def remove_course_from_memory(course_id: int) -> bool:
    """
    Remove course from Supermemory (when deleted or unpublished)
    
    Args:
        course_id: Course ID to remove
        
    Returns:
        True if successful, False otherwise
    """
    # Note: Supermemory API doesn't have direct delete by metadata
    # You would need to search for the course first, then delete by document ID
    # For now, this is a placeholder
    return True
