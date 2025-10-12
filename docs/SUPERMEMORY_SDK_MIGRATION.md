# Supermemory SDK Migration Guide

## Overview
The NMTSA LMS now uses the **official Supermemory Python SDK** instead of direct API calls. This provides better type safety, error handling, and automatic retries.

## What Changed

### Before (Direct API calls with requests)
```python
import requests

response = requests.post(
    f"{base_url}/v3/search",
    headers={"Authorization": f"Bearer {api_key}"},
    json={"query": query, "limit": limit}
)
```

### After (Official SDK)
```python
from supermemory import Supermemory

client = Supermemory(api_key=api_key)
response = client.search.execute(q=query, limit=limit)
```

## Installation

### 1. Install the SDK
```bash
pip install --pre supermemory
```

The `--pre` flag is required because the SDK is currently in pre-release.

### 2. Update Dependencies
If using `uv` or `pip`:
```bash
cd nmtsa_lms
uv sync  # or: pip install -r requirements.txt
```

The `supermemory` package is already added to `pyproject.toml`.

## SDK Features Used

### 1. **Search Memories**
```python
from supermemory import Supermemory

client = Supermemory(api_key=os.environ.get("SUPERMEMORY_API_KEY"))

# Search across all memories
response = client.search.execute(
    q="autism music therapy",
    limit=10
)

# Search within a specific container (recommended)
response = client.search.execute(
    q="beginner courses",
    limit=10,
    container_tag="nmtsa-courses"
)

# Access results
for memory in response.results:
    print(memory.content)
    print(memory.metadata)
    print(memory.score)  # Relevance score
```

### 2. **Add Documents/Memories**
```python
# Add a document (will be chunked into memories automatically)
response = client.documents.create(
    content="Neurologic Music Therapy is...",
    containerTag="nmtsa-courses",  # Group related memories
    metadata={
        "course_id": 123,
        "title": "NMT Fundamentals",
        "is_published": True
    },
    customId="course_123"  # For deduplication/updates
)

print(response.id)  # Document ID
print(response.status)  # "queued" | "processing" | "done"
```

### 3. **Deduplication with Custom IDs**
```python
# First time - creates new document
client.documents.create(
    content="Course content v1",
    customId="course_123"
)

# Second time - updates existing document
client.documents.create(
    content="Course content v2",
    customId="course_123"  # Same ID = upsert
)
```

### 4. **Error Handling**
```python
import supermemory
from supermemory import Supermemory

client = Supermemory()

try:
    response = client.search.execute(q="test")
except supermemory.AuthenticationError as e:
    print("Invalid API key")
except supermemory.RateLimitError as e:
    print("Rate limit exceeded - back off")
except supermemory.APIConnectionError as e:
    print("Network error")
    print(e.__cause__)  # Underlying exception
except supermemory.APIStatusError as e:
    print(f"API error: {e.status_code}")
    print(e.response)
```

## Updated Files

### 1. `lms/supermemory_client.py`
- **Old**: Used `requests` library for direct API calls
- **New**: Uses official `Supermemory` SDK
- **Key Changes**:
  - Import: `from supermemory import Supermemory`
  - Client initialization: `self.client = Supermemory(api_key=api_key)`
  - Search: `self.client.search.execute(q=query, limit=limit, container_tag=tag)`
  - Add memory: `self.client.documents.create(content=content, ...)`
  - Better error handling with SDK exceptions

### 2. `lms/course_memory.py`
- No changes required - uses `SupermemoryClient` wrapper
- Works seamlessly with SDK changes

### 3. Environment Variables
- **Removed**: `SUPERMEMORY_BASE_URL` (SDK handles this)
- **Removed**: `SUPERMEMORY_PROJECT_ID` (not needed with SDK)
- **Kept**: `SUPERMEMORY_API_KEY` (required)

## Configuration

### `.env` File
```bash
# Required
SUPERMEMORY_API_KEY=your-api-key-here

# Optional (for production chat)
OPENAI_API_KEY=your-openai-key-here
```

### Django Settings
The SDK automatically reads `SUPERMEMORY_API_KEY` from:
1. Environment variables (recommended)
2. Django settings (`settings.SUPERMEMORY_API_KEY`)
3. Direct parameter (`Supermemory(api_key="...")`)

## Container Tags (Best Practice)

### What are Container Tags?
Container tags group related memories in a "space" for faster queries.

### Why Use Single Tags?
- **Faster queries**: Single tag = O(1) lookup
- **Better context**: Memories in same space can reference each other
- **Simpler filtering**: `container_tag="nmtsa-courses"` vs `containerTags=["tag1", "tag2", "tag3"]`

### Recommended Tags for NMTSA LMS
```python
# Course content
container_tag="nmtsa-courses"

# User conversations
container_tag=f"user_{user_id}_chats"

# Support documentation
container_tag="nmtsa-docs"

# Teacher resources
container_tag="nmtsa-teacher-resources"
```

## SDK Methods Reference

### Search
```python
client.search.execute(
    q: str,                      # Required: search query
    limit: int = 10,             # Max results
    container_tag: str = None    # Filter by tag
)
```

### Add Document
```python
client.documents.create(
    content: str,                # Required: document content
    containerTag: str = None,    # Recommended: single tag
    metadata: dict = None,       # Strings, numbers, booleans only
    customId: str = None         # For deduplication/updates
)
```

### Response Objects
```python
# SearchResponse
response.results                 # List of Memory objects
for memory in response.results:
    memory.content               # Memory content
    memory.metadata              # Metadata dict
    memory.score                 # Relevance score
    memory.to_dict()             # Convert to dict
    memory.to_json()             # Convert to JSON

# DocumentResponse
response.id                      # Document ID
response.status                  # "queued" | "processing" | "done"
```

## Testing

### Verify SDK Installation
```python
python -c "import supermemory; print(supermemory.__version__)"
```

### Test Search
```python
from lms.supermemory_client import get_supermemory_client

client = get_supermemory_client()
if client:
    memories = client.search_memories("test query", limit=5)
    print(f"Found {len(memories)} memories")
else:
    print("Supermemory not configured")
```

### Test in Django Shell
```bash
cd nmtsa_lms
python manage.py shell
```

```python
from lms.supermemory_client import get_supermemory_client

client = get_supermemory_client()
print(f"Client: {client}")

# Add test memory
doc_id = client.add_memory(
    content="Test memory content",
    container_tag="test",
    metadata={"type": "test"}
)
print(f"Document ID: {doc_id}")

# Search
results = client.search_memories("test", limit=5, container_tag="test")
print(f"Found {len(results)} results")
```

## Troubleshooting

### ImportError: No module named 'supermemory'
```bash
pip install --pre supermemory
```

### AuthenticationError: Invalid API key
1. Check `.env` file has `SUPERMEMORY_API_KEY=...`
2. Get new key from https://console.supermemory.ai/
3. Restart Django server after updating `.env`

### SDK Not Found (SUPERMEMORY_AVAILABLE = False)
```python
# In lms/supermemory_client.py - check this:
try:
    from supermemory import Supermemory
    SUPERMEMORY_AVAILABLE = True
except ImportError:
    SUPERMEMORY_AVAILABLE = False
    print("Run: pip install --pre supermemory")
```

### Rate Limiting
The SDK automatically retries with exponential backoff. Configure:
```python
client = Supermemory(
    api_key=api_key,
    max_retries=5,      # Default: 2
    timeout=30.0        # Default: 60 seconds
)
```

## Migration Checklist

- [x] Install supermemory SDK (`pip install --pre supermemory`)
- [x] Update `lms/supermemory_client.py` to use SDK
- [x] Update `pyproject.toml` dependencies
- [x] Create `.env.example` with SDK-only variables
- [x] Update documentation (this file)
- [ ] Test search functionality
- [ ] Test add memory functionality
- [ ] Test course search
- [ ] Test chat with memory context
- [ ] Run in production

## Resources

- **SDK Documentation**: https://supermemory.ai/docs/memory-api/sdks/python
- **API Console**: https://console.supermemory.ai/
- **GitHub**: https://github.com/supermemoryai/python-sdk
- **Support**: https://discord.gg/supermemory (check docs for link)

## Next Steps

1. **Install SDK**: `pip install --pre supermemory`
2. **Configure API Key**: Add to `.env` file
3. **Run Migrations**: `python manage.py migrate`
4. **Test Chat**: Open app and try the chat interface
5. **Index Courses**: Run course memory sync (see `CHAT_CHECKLIST.md`)

---

**Note**: The SDK is in pre-release but production-ready. The `--pre` flag will be removed once v1.0 is released.
