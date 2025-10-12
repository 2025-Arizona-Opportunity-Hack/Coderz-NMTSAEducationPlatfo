"""
Supermemory Client for NMTSA LMS
Provides memory-enhanced AI capabilities for chat and course recommendations
Uses the official Supermemory Python SDK with Memory Router for LLM integration
"""
import os
import logging
from typing import Optional, Dict, List, Any
from django.conf import settings

logger = logging.getLogger(__name__)

try:
    from supermemory import Supermemory
    SUPERMEMORY_AVAILABLE = True
except ImportError:
    SUPERMEMORY_AVAILABLE = False
    logger.warning("supermemory package not installed. Install with: pip install --pre supermemory")

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logger.warning("openai package required for Gemini integration. Install with: pip install openai")


# System prompt that restricts chatbot to NMTSA LMS domain
NMTSA_SYSTEM_PROMPT = """You are the NMTSA LMS Assistant, a helpful AI chatbot for the Neurologic Music Therapy Student Association Learning Management System (NMTSA LMS).

YOUR ROLE:
- Help users discover and learn about neurologic music therapy courses
- Answer questions about the NMTSA LMS platform features and functionality
- Provide information about course enrollment, pricing, and content
- Guide users through the platform navigation
- Answer frequently asked questions about the website

STRICT GUIDELINES:
1. ONLY discuss topics related to:
   - NMTSA LMS website and platform features
   - Available courses on neurologic music therapy
   - How to enroll, navigate, and use the platform
   - Teacher/student roles and verification process
   - Course content, modules, and lessons
   - Pricing and payment information
   
2. ALWAYS search your memory FIRST before answering questions about courses or platform features

3. If asked about topics OUTSIDE this domain:
   - Politely redirect: "I'm specifically designed to help with the NMTSA LMS platform and neurologic music therapy courses. For that topic, I recommend checking other resources. How can I help you with our learning platform?"

4. When discussing courses:
   - Provide accurate information from your memory
   - Mention course titles, descriptions, and what students will learn
   - Be specific about whether courses are free or paid
   - Guide users on how to enroll

5. Communication style:
   - Be friendly, clear, and professional
   - Use natural, conversational language
   - Ask clarifying questions if needed
   - Provide helpful next steps

REMEMBER: You represent NMTSA LMS. Stay on-topic and be helpful within your domain!"""


class SupermemoryClient:
    """
    Client for interacting with Supermemory API using official SDK
    Provides memory-enhanced chat using Google Gemini via Memory Router
    
    Uses Google Gemini (gemini-pro) for natural language generation with
    Supermemory's memory context for accurate, domain-specific responses.
    """
    
    def __init__(
        self, 
        api_key: Optional[str] = None, 
        gemini_api_key: Optional[str] = None
    ):
        """
        Initialize Supermemory client with Gemini Memory Router
        
        Args:
            api_key: Supermemory API key (defaults to env variable or Django settings)
            gemini_api_key: Google Gemini API key for Memory Router
        """
        if not SUPERMEMORY_AVAILABLE:
            raise ImportError("supermemory package not installed. Run: pip install --pre supermemory")
        
        if not OPENAI_AVAILABLE:
            raise ImportError("openai package required for Gemini integration. Run: pip install openai")
        
        # Get Supermemory API key
        self.supermemory_api_key = (
            api_key or 
            os.getenv("SUPERMEMORY_API_KEY") or 
            getattr(settings, 'SUPERMEMORY_API_KEY', None)
        )
        
        if not self.supermemory_api_key:
            raise ValueError("SUPERMEMORY_API_KEY must be set in environment or Django settings")
        
        # Get Gemini API key
        self.gemini_api_key = (
            gemini_api_key or
            os.getenv("GEMINI_API_KEY") or
            getattr(settings, 'GEMINI_API_KEY', None)
        )
        
        if not self.gemini_api_key:
            raise ValueError(
                "GEMINI_API_KEY must be set for chat functionality. "
                "Get free API key at: https://makersuite.google.com/app/apikey"
            )
        
        # Initialize Supermemory client for memory operations
        self.memory_client = Supermemory(api_key=self.supermemory_api_key)
        
        # Initialize Gemini client with Memory Router
        # Uses OpenAI-compatible API via Supermemory's Memory Router
        # Route: https://api.supermemory.ai/v3/https://generativelanguage.googleapis.com/v1beta
        self.chat_client = OpenAI(
            api_key=self.gemini_api_key,
            base_url="https://api.supermemory.ai/v3/https://generativelanguage.googleapis.com/v1beta",
            default_headers={
                "x-supermemory-api-key": self.supermemory_api_key,
                "x-sm-user-id": "nmtsa-lms-system"
            }
        )
        
        logger.info("Initialized Supermemory with Google Gemini (free tier available)")
    
    def search_memories(
        self, 
        query: str, 
        limit: int = 10, 
        container_tags: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search memories using semantic search via official SDK
        
        Args:
            query: Search query
            limit: Maximum number of results
            container_tags: Optional list of container tags to filter results
            
        Returns:
            List of memory objects with content, metadata, and score
        """
        try:
            # Build search parameters
            search_params = {
                "q": query,
                "limit": limit
            }
            
            if container_tags:
                search_params["container_tags"] = container_tags
            
            # Use SDK's search.execute method
            response = self.memory_client.search.execute(**search_params)
            
            # Convert response to list of dicts
            results = []
            if hasattr(response, 'results'):
                for memory in response.results:
                    # Convert to dict if it's a Pydantic model
                    if hasattr(memory, 'model_dump'):
                        memory_dict = memory.model_dump()
                    elif hasattr(memory, 'to_dict'):
                        memory_dict = memory.to_dict()
                    elif hasattr(memory, '__dict__'):
                        memory_dict = vars(memory)
                    else:
                        memory_dict = dict(memory)
                    
                    # Filter by relevance score (0.60 threshold)
                    score = memory_dict.get('score', 0)
                    if score > 0.60:
                        results.append(memory_dict)
            
            logger.info(f"Search for '{query}' returned {len(results)} relevant results")
            return results
                
        except Exception as e:
            logger.error(f"Error searching memories: {e}")
            return []
    
    def add_memory(
        self, 
        content: str, 
        metadata: Optional[Dict] = None, 
        container_tag: Optional[str] = None,
        custom_id: Optional[str] = None
    ) -> Optional[str]:
        """
        Add a new memory to Supermemory (with upsert support via custom_id)
        
        Using the same custom_id will UPDATE the existing memory instead of creating duplicates.
        This enables idempotent operations.
        
        Args:
            content: Memory content to store
            metadata: Optional metadata dict (strings, numbers, booleans only)
            container_tag: Optional tag to group related memories
            custom_id: Optional custom identifier for deduplication/upserts (RECOMMENDED)
            
        Returns:
            Memory ID if successful, None otherwise
        """
        try:
            # Build payload for SDK
            payload = {'content': content}
            
            if container_tag:
                payload['container_tag'] = container_tag
            
            if metadata:
                payload['metadata'] = metadata
            
            if custom_id:
                # Using custom_id enables upsert behavior
                payload['custom_id'] = custom_id
            
            # Use SDK's memories.add method (correct as per docs)
            response = self.memory_client.memories.add(**payload)
            
            # Return memory ID
            memory_id = None
            if hasattr(response, 'id'):
                memory_id = response.id
            elif hasattr(response, 'model_dump'):
                memory_id = response.model_dump().get('id')
            elif isinstance(response, dict):
                memory_id = response.get('id')
            
            if memory_id:
                logger.info(f"Added/updated memory with ID: {memory_id}")
            
            return memory_id
                
        except Exception as e:
            logger.error(f"Error adding memory: {e}")
            return None
    
    def chat_completion(
        self, 
        messages: List[Dict[str, str]], 
        user_id: Optional[str] = None,
        model: str = "gemini-2.5-flash-lite",
        temperature: float = 0.2
    ) -> Dict[str, Any]:
        """
        Generate chat completion using Google Gemini via Memory Router
        
        Memory Router automatically injects relevant memories from the conversation context.
        Uses Google Gemini with free tier (60 requests/minute).
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            user_id: Optional user identifier for memory context (default: system-wide)
            model: Gemini model to use (default: "gemini-pro")
                   Options: "gemini-pro", "gemini-1.5-pro", "gemini-1.5-flash"
            temperature: Creativity level 0-1 (default: 0.7)
            
        Returns:
            Dict with 'success' (bool), 'response' (str), and optional 'error' (str)
        """
        try:
            # Prepend system prompt for domain restriction
            enhanced_messages = [
                {"role": "system", "content": NMTSA_SYSTEM_PROMPT}
            ] + messages
            
            # Set user_id for memory context (optional but recommended)
            headers = {}
            if user_id:
                headers["x-sm-user-id"] = f"nmtsa-user-{user_id}"
            
            # Create chat completion via Memory Router with Gemini
            # Memory Router will automatically search and inject relevant memories
            response = self.chat_client.chat.completions.create(
                model=model,
                messages=enhanced_messages,
                temperature=temperature,
                max_tokens=500,  # Reasonable limit for chat responses
                extra_headers=headers if headers else None
            )
            
            # Extract response content
            assistant_message = response.choices[0].message.content
            
            logger.info(f"Chat completion successful with Gemini (user: {user_id or 'system'})")
            
            return {
                "success": True,
                "response": assistant_message,
                "provider": "gemini"
            }
            
        except Exception as e:
            logger.error(f"Error in Gemini chat completion: {e}")
            return {
                "success": False,
                "error": str(e),
                "response": "I'm sorry, I'm having trouble processing your request right now. Please try again."
            }
    
    def index_course(self, content: str, metadata: Dict[str, Any]) -> Optional[str]:
        """
        Index a course to Supermemory.

        Args:
            content: Searchable course content
            metadata: Course metadata (must include 'slug' key)

        Returns:
            Document ID if successful, None otherwise
        """
        if not metadata.get('slug'):
            logger.error("Cannot index course: missing slug in metadata")
            return None

        return self.add_memory(
            content=content,
            metadata=metadata,
            container_tag='nmtsa-courses',
            custom_id=metadata['slug']  # Use slug as unique ID
        )

    def index_module(self, content: str, metadata: Dict[str, Any]) -> Optional[str]:
        """
        Index a module to Supermemory.

        Args:
            content: Searchable module content
            metadata: Module metadata (must include 'slug' and 'course_slug' keys)

        Returns:
            Document ID if successful, None otherwise
        """
        if not metadata.get('slug'):
            logger.error("Cannot index module: missing slug in metadata")
            return None

        return self.add_memory(
            content=content,
            metadata=metadata,
            container_tag='nmtsa-modules',
            custom_id=metadata['slug']  # Use slug as unique ID
        )

    def index_lesson(self, content: str, metadata: Dict[str, Any]) -> Optional[str]:
        """
        Index a lesson to Supermemory.

        Args:
            content: Searchable lesson content
            metadata: Lesson metadata (must include 'slug', 'module_slug', and 'course_slug' keys)

        Returns:
            Document ID if successful, None otherwise
        """
        if not metadata.get('slug'):
            logger.error("Cannot index lesson: missing slug in metadata")
            return None

        return self.add_memory(
            content=content,
            metadata=metadata,
            container_tag='nmtsa-lessons',
            custom_id=metadata['slug']  # Use slug as unique ID
        )

    def search_by_type(
        self,
        query: str,
        search_type: str,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Search a specific entity type (course, module, or lesson).

        Args:
            query: Search query
            search_type: One of 'course', 'module', 'lesson'
            limit: Maximum number of results

        Returns:
            List of search results with content, metadata, and score
        """
        container_tag_map = {
            'course': 'nmtsa-courses',
            'module': 'nmtsa-modules',
            'lesson': 'nmtsa-lessons',
        }

        container_tag = container_tag_map.get(search_type)
        if not container_tag:
            logger.error(f"Invalid search_type: {search_type}")
            return []

        return self.search_memories(
            query=query,
            limit=limit,
            container_tags=[container_tag]  # Pass as list
        )

    def multi_tier_search(
        self,
        query: str,
        limit_per_tier: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Perform multi-tier search across courses, modules, and lessons.
        Returns aggregated results with weighted scoring.

        Args:
            query: Natural language search query
            limit_per_tier: Maximum results per search tier

        Returns:
            List of aggregated course results sorted by relevance
            [{"slug": "abc123", "score": 0.95, "match_type": "course"}, ...]
        """
        try:
            # Import here to avoid circular dependency
            from lms.search_aggregator import aggregate_search_results

            # Perform 3 parallel searches
            course_results = self.search_by_type(query, 'course', limit_per_tier)
            module_results = self.search_by_type(query, 'module', limit_per_tier)
            lesson_results = self.search_by_type(query, 'lesson', limit_per_tier)

            logger.info(
                f"Multi-tier search for '{query}': "
                f"{len(course_results)} courses, {len(module_results)} modules, "
                f"{len(lesson_results)} lessons"
            )

            # Aggregate and weight results
            aggregated = aggregate_search_results(
                course_results,
                module_results,
                lesson_results
            )

            return aggregated

        except Exception as e:
            logger.error(f"Error in multi_tier_search: {e}")
            return []

    def search_courses(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search courses using semantic search via Supermemory

        Args:
            query: Search query
            limit: Maximum number of results

        Returns:
            List of course objects with id, title, description, relevance_score
        """
        try:
            # Search memories with 'nmtsa-courses' container tag
            memories = self.search_memories(
                query=query,
                limit=limit,
                container_tags=['nmtsa-courses']  # Pass as list
            )

            # Extract course data from memories
            courses = []
            for memory in memories:
                metadata = memory.get('metadata', {})
                content = memory.get('content', '')
                score = memory.get('score', 0)

                if metadata and 'course_id' in metadata:
                    courses.append({
                        'id': metadata.get('course_id'),
                        'title': metadata.get('title', ''),
                        'description': content,
                        'relevance_score': score,
                        'is_paid': metadata.get('is_paid', False),
                        'is_published': metadata.get('is_published', False),
                        'tags': metadata.get('tags', [])
                    })

            logger.info(f"Found {len(courses)} courses for query: {query}")
            return courses

        except Exception as e:
            logger.error(f"Course search error: {e}")
            return []


# Singleton instance
_supermemory_client: Optional[SupermemoryClient] = None


def get_supermemory_client() -> Optional[SupermemoryClient]:
    """
    Get or create singleton Supermemory client instance with Google Gemini
    
    Returns:
        SupermemoryClient instance if configured and SDK available, None otherwise
    """
    global _supermemory_client
    
    if not SUPERMEMORY_AVAILABLE or not OPENAI_AVAILABLE:
        logger.warning("Supermemory or openai package not available")
        return None
    
    if _supermemory_client is None:
        try:
            _supermemory_client = SupermemoryClient()
            logger.info("Supermemory client initialized with Google Gemini")
        except (ValueError, ImportError) as e:
            logger.error(f"Supermemory not configured: {e}")
            return None
    
    return _supermemory_client
