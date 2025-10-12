"""
Supermemory Client for NMTSA LMS
Provides memory-enhanced AI capabilities for chat and course recommendations
Uses the official Supermemory Python SDK
"""
import os
from typing import Optional, Dict, List, Any
from django.conf import settings

try:
    from supermemory import Supermemory
    SUPERMEMORY_AVAILABLE = True
except ImportError:
    SUPERMEMORY_AVAILABLE = False
    print("Warning: supermemory package not installed. Install with: pip install --pre supermemory")


class SupermemoryClient:
    """
    Client for interacting with Supermemory API using official SDK
    Provides methods for chat completion, memory management, and semantic search
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Supermemory client
        
        Args:
            api_key: Supermemory API key (defaults to env variable or Django settings)
        """
        if not SUPERMEMORY_AVAILABLE:
            raise ImportError("supermemory package not installed. Run: pip install --pre supermemory")
        
        # Try multiple sources for API key
        self.api_key = (
            api_key or 
            os.getenv("SUPERMEMORY_API_KEY") or 
            getattr(settings, 'SUPERMEMORY_API_KEY', None)
        )
        
        if not self.api_key:
            raise ValueError("SUPERMEMORY_API_KEY must be set in environment or Django settings")
        
        # Initialize the official SDK client
        self.client = Supermemory(api_key=self.api_key)
    
    def search_memories(
        self, 
        query: str, 
        limit: int = 10, 
        container_tag: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Search memories using semantic search via official SDK
        
        Args:
            query: Search query
            limit: Maximum number of results
            container_tag: Optional container tag to filter results
            
        Returns:
            List of memory objects with content and metadata
        """
        try:
            # Use SDK's search.execute method
            response = self.client.search.execute(
                q=query,
                limit=limit,
                container_tag=container_tag
            )
            
            # Convert response to list of dicts
            results = []
            if hasattr(response, 'results'):
                for memory in response.results:
                    # Handle both object and dict responses
                    if hasattr(memory, 'to_dict'):
                        results.append(memory.to_dict())
                    elif hasattr(memory, '__dict__'):
                        results.append(vars(memory))
                    else:
                        results.append(memory)
            
            return results
                
        except Exception as e:
            print(f"Error searching memories: {e}")
            return []
    
    def add_memory(
        self, 
        content: str, 
        metadata: Optional[Dict] = None, 
        container_tag: Optional[str] = None,
        custom_id: Optional[str] = None
    ) -> Optional[str]:
        """
        Add a new document to Supermemory (will be chunked into memories)
        
        Args:
            content: Document content to store
            metadata: Optional metadata dict (strings, numbers, booleans only)
            container_tag: Optional tag to group related memories (recommended: single tag)
            custom_id: Optional custom identifier for deduplication/updates
            
        Returns:
            Document ID if successful, None otherwise
        """
        try:
            # Build payload for SDK
            payload = {'content': content}
            
            if container_tag:
                payload['containerTag'] = container_tag
            
            if metadata:
                payload['metadata'] = metadata
            
            if custom_id:
                payload['customId'] = custom_id
            
            # Use SDK's documents endpoint (method name may vary - adjust if needed)
            if hasattr(self.client, 'documents') and hasattr(self.client.documents, 'create'):
                response = self.client.documents.create(**payload)
            else:
                # Fallback: use memories.add if documents.create doesn't exist
                response = self.client.memories.add(**payload)
            
            # Return document ID
            if hasattr(response, 'id'):
                return response.id
            elif isinstance(response, dict) and 'id' in response:
                return response['id']
            
            return None
                
        except Exception as e:
            print(f"Error adding memory: {e}")
            return None
    
    def chat_completion(
        self, 
        messages: List[Dict[str, str]], 
        use_memory: bool = True,
        container_tag: Optional[str] = None
    ) -> Optional[str]:
        """
        Generate chat completion with optional memory context
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            use_memory: Whether to use memory context (default: True)
            container_tag: Optional container tag to filter memory search
            
        Returns:
            AI response text, or None if error
        """
        try:
            # Extract the user's last message for context retrieval
            user_message = next(
                (msg['content'] for msg in reversed(messages) if msg['role'] == 'user'),
                ""
            )
            
            # Search for relevant memories if enabled
            enhanced_messages = messages.copy()
            if use_memory and user_message:
                memories = self.search_memories(user_message, limit=5, container_tag=container_tag)
                
                if memories:
                    # Extract content from memory results
                    context_parts = []
                    for memory in memories[:3]:  # Limit to top 3
                        content = memory.get('content', '')
                        if content:
                            context_parts.append(content)
                    
                    if context_parts:
                        context = "\n".join(context_parts)
                        
                        # Add system message with memory context
                        enhanced_messages.insert(0, {
                            'role': 'system',
                            'content': f'You are a helpful AI assistant for the NMTSA LMS platform, specializing in neurologic music therapy education. Use the following relevant context from memory to provide accurate answers:\n\n{context}'
                        })
            
            # TODO: Integrate with actual LLM API (OpenAI, Anthropic, etc.)
            # For now, return a helpful mock response
            # Example integration:
            # import openai
            # response = openai.ChatCompletion.create(
            #     model="gpt-4",
            #     messages=enhanced_messages
            # )
            # return response.choices[0].message.content
            
            return "I'm an AI assistant for the NMTSA LMS platform, powered by Supermemory. I can help you find courses, answer questions about neurologic music therapy education, and assist with the learning platform. How can I help you today?"
            
        except Exception as e:
            print(f"Error in chat completion: {e}")
            return None
    
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
                container_tag='nmtsa-courses'
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
            
            return courses
                
        except Exception as e:
            print(f"Course search error: {e}")
            return []


# Singleton instance
_supermemory_client: Optional[SupermemoryClient] = None


def get_supermemory_client() -> Optional[SupermemoryClient]:
    """
    Get or create singleton Supermemory client instance
    
    Returns:
        SupermemoryClient instance if configured and SDK available, None otherwise
    """
    global _supermemory_client
    
    if not SUPERMEMORY_AVAILABLE:
        return None
    
    if _supermemory_client is None:
        try:
            _supermemory_client = SupermemoryClient()
        except (ValueError, ImportError) as e:
            print(f"Supermemory not configured: {e}")
            return None
    
    return _supermemory_client
