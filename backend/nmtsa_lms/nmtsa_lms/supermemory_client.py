"""
Supermemory Client for NMTSA LMS
Provides memory-enhanced AI capabilities for chat and course recommendations
"""
import os
from typing import Optional

try:
    from supermemory import Supermemory
    SUPERMEMORY_AVAILABLE = True
except ImportError:
    SUPERMEMORY_AVAILABLE = False
    Supermemory = None


# Singleton instance
_supermemory_client = None


def get_supermemory_client() -> Optional[Supermemory]:
    """
    Get or create Supermemory client instance
    
    Returns:
        Supermemory client if configured, None otherwise
    """
    global _supermemory_client
    
    if _supermemory_client is None:
        api_key = os.getenv("SUPERMEMORY_API_KEY")
        
        if not api_key or not SUPERMEMORY_AVAILABLE:
            return None
        
        try:
            base_url = os.getenv("SUPERMEMORY_BASE_URL", "https://api.supermemory.ai/")
            _supermemory_client = Supermemory(
                api_key=api_key,
                base_url=base_url
            )
        except Exception:
            _supermemory_client = None
    
    return _supermemory_client
