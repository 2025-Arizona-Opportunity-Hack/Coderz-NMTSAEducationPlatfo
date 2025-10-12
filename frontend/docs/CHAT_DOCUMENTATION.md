# Chat Interface Documentation

## Overview

A complete, modular chat interface for the NMTSA LMS application, built with React and integrated with Django backend APIs. The chat system provides real-time messaging capabilities without any GenAI features.

## Features

- ✅ **Real-time messaging** via backend API polling
- ✅ **Typing indicators** showing when users are composing messages
- ✅ **Message history** with pagination
- ✅ **Conversation management** (create, delete)
- ✅ **Toggle visibility** with floating button
- ✅ **Unread message counter** badge
- ✅ **Error handling** with user-friendly messages
- ✅ **Performance optimized** with debouncing and efficient rendering
- ✅ **Fully accessible** with ARIA labels and keyboard navigation
- ✅ **Responsive design** works on all screen sizes
- ✅ **Security** with XSS prevention and input validation

## Architecture

### Frontend Structure

```
frontend/src/
├── components/
│   └── chat/
│       └── Chat.tsx          # Main chat component (single file)
├── services/
│   └── chat.service.ts       # API service layer
└── types/
    └── api.ts               # TypeScript interfaces (chat types added)
```

### Backend Structure

```
backend/nmtsa_lms/
└── student_dash/
    ├── chat_views.py        # Django API views
    └── chat_urls.py         # URL routing
```

## Frontend Components

The entire chat interface is modularized within a single file (`Chat.tsx`) for easy maintenance and integration:

### 1. **Chat Toggle Button**

- Floating action button in the bottom-right corner
- Shows unread message count badge
- Accessible with tooltip

### 2. **Chat Window**

- Main container with header, messages, and input
- Animated entrance/exit with Framer Motion
- Minimizable/maximizable
- Fixed dimensions (380px × 600px)

### 3. **Chat Header**

- Shows conversation participant info
- Controls: minimize, close, delete conversation
- Role badge (student, instructor, admin)

### 4. **Message List**

- Scrollable message history
- Auto-scroll to bottom on new messages
- Loading state with spinner
- Empty state message

### 5. **Chat Message**

- Individual message bubble
- Sender avatar and name
- Timestamp with human-readable format
- Different styling for own vs. other messages

### 6. **Typing Indicator**

- Animated dots when someone is typing
- Shows below message list
- Automatically hidden when not typing

### 7. **Chat Input**

- Text input with send button
- Enter to send, Shift+Enter for new line
- Real-time typing status updates
- Validation with error messages
- Character limit (1000 chars)

### 8. **Utility Functions**

- `formatTimestamp()`: Human-readable time (e.g., "5m ago")
- `validateMessage()`: Input validation
- `sanitizeMessage()`: XSS prevention
- `formatMessageContent()`: Line break formatting
- `debounce()`: Typing indicator optimization

## Backend API Endpoints

All endpoints require authentication (`IsAuthenticated` permission).

### Base URL

```
http://localhost:8000/api/v1/chat/
```

### Endpoints

#### 1. Get Conversations

```http
GET /api/v1/chat/conversations?page=1&limit=20
```

**Response:**

```json
{
  "data": [
    {
      "id": "uuid",
      "participantIds": ["user1", "user2"],
      "participants": [...],
      "lastMessage": {...},
      "unreadCount": 2,
      "updatedAt": "2025-10-11T10:00:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 5,
    "totalPages": 1
  }
}
```

#### 2. Get Messages

```http
GET /api/v1/chat/conversations/{conversationId}/messages?page=1&limit=50
```

**Response:**

```json
{
  "data": [
    {
      "id": "uuid",
      "content": "Hello!",
      "senderId": "user1",
      "sender": {...},
      "recipientId": "user2",
      "conversationId": "conv1",
      "isRead": true,
      "timestamp": "2025-10-11T10:00:00Z",
      "createdAt": "2025-10-11T10:00:00Z"
    }
  ],
  "pagination": {...}
}
```

#### 3. Send Message

```http
POST /api/v1/chat/messages
Content-Type: application/json

{
  "content": "Hello, how are you?",
  "conversationId": "uuid"
}
```

**Response:**

```json
{
  "data": {
    "id": "uuid",
    "content": "Hello, how are you?",
    "senderId": "user1",
    "sender": {...},
    "timestamp": "2025-10-11T10:00:00Z",
    ...
  }
}
```

#### 4. Mark as Read

```http
POST /api/v1/chat/messages/read
Content-Type: application/json

{
  "messageIds": ["uuid1", "uuid2"]
}
```

#### 5. Get Typing Status

```http
GET /api/v1/chat/conversations/{conversationId}/typing
```

**Response:**

```json
{
  "data": [
    {
      "userId": "user2",
      "conversationId": "conv1",
      "isTyping": true,
      "timestamp": "2025-10-11T10:00:00Z"
    }
  ]
}
```

#### 6. Update Typing Status

```http
POST /api/v1/chat/conversations/{conversationId}/typing
Content-Type: application/json

{
  "isTyping": true
}
```

#### 7. Create Conversation

```http
POST /api/v1/chat/conversations
Content-Type: application/json

{
  "participantId": "user2"
}
```

#### 8. Delete Conversation

```http
DELETE /api/v1/chat/conversations/{conversationId}
```

#### 9. Get Unread Count

```http
GET /api/v1/chat/unread-count
```

**Response:**

```json
{
  "data": {
    "count": 5
  }
}
```

## Usage

### Integration

The chat component is automatically integrated into the main layout:

```tsx
// src/components/layout/Layout.tsx
import { Chat } from "../chat/Chat";

export function Layout() {
  return (
    <div className="min-h-screen flex flex-col">
      <Navbar />
      <main>
        <Outlet />
      </main>
      <Footer />
      <Chat /> {/* Automatically available on all pages */}
    </div>
  );
}
```

### Custom Integration

If you need to use the chat component elsewhere:

```tsx
import { Chat } from "./components/chat/Chat";

function MyPage() {
  return (
    <div>
      <h1>My Page</h1>
      <Chat />
    </div>
  );
}
```

## State Management

The chat component uses React hooks for local state management:

- `useState` for UI state (open, minimized, loading, etc.)
- `useRef` for DOM references (scroll container, polling interval)
- `useCallback` for memoized functions
- `useEffect` for side effects (polling, data fetching)

Authentication state is managed globally via Zustand (`useAuthStore`).

## Performance Optimizations

1. **Debounced Typing Indicators**: 500ms debounce to reduce API calls
2. **Polling Optimization**: 3-second interval, stops when minimized/closed
3. **Efficient Rendering**: AnimatePresence for smooth transitions
4. **Memoized Callbacks**: useCallback to prevent unnecessary re-renders
5. **Conditional Polling**: Only polls for active conversation
6. **Smart Scrolling**: Only scrolls on new messages

## Security Features

1. **XSS Prevention**: All user content is sanitized before rendering
2. **Input Validation**: Maximum length (1000 chars) and required field checks
3. **Authentication Required**: All API endpoints require valid JWT token
4. **CSRF Protection**: Django REST framework built-in protection
5. **Content Sanitization**: HTML entities escaped

## Error Handling

- Network errors display user-friendly messages
- Failed API calls show error banner
- Validation errors appear inline
- Automatic retry on timeout
- Graceful degradation on API failures

## Accessibility

- ✅ **ARIA labels** on all interactive elements
- ✅ **Keyboard navigation** fully supported
- ✅ **Focus management** proper focus states
- ✅ **Screen reader friendly** semantic HTML
- ✅ **Color contrast** WCAG AA compliant
- ✅ **Tooltips** for icon buttons

## Styling

The chat interface uses:

- **HeroUI components** (Button, Input, Avatar, Spinner, Tooltip)
- **Tailwind CSS** for utility classes
- **Framer Motion** for animations
- **Lucide React** for icons

Colors follow the application's design system with support for dark mode.

## Future Enhancements

Potential features for future development:

- [ ] WebSocket support for true real-time messaging
- [ ] Message attachments (images, files)
- [ ] Message reactions (emoji)
- [ ] Group chat support
- [ ] Message search
- [ ] Push notifications
- [ ] Voice messages
- [ ] Message threading/replies
- [ ] Online/offline status indicators
- [ ] Read receipts
- [ ] Message editing/deletion
- [ ] Rich text formatting (markdown)

## Testing

### Manual Testing Checklist

- [ ] Open chat window
- [ ] Send a message
- [ ] Receive messages
- [ ] Typing indicator appears
- [ ] Messages load on scroll
- [ ] Minimize/maximize works
- [ ] Close and reopen
- [ ] Delete conversation
- [ ] Unread count updates
- [ ] Error handling works
- [ ] Mobile responsive
- [ ] Keyboard navigation
- [ ] Screen reader friendly

### Mock Data

The backend currently returns mock data. To test:

1. Start the backend server:

   ```bash
   cd backend/nmtsa_lms
   python manage.py runserver
   ```

2. Start the frontend:

   ```bash
   cd frontend
   pnpm dev
   ```

3. Login as a user
4. Click the chat button in the bottom-right corner
5. The chat will show mock conversations and messages

## Troubleshooting

### Chat button doesn't appear

- Make sure you're logged in (chat only shows for authenticated users)
- Check browser console for errors

### Messages not loading

- Verify backend is running on `http://localhost:8000`
- Check API endpoint configuration in `.env`
- Verify CORS settings in Django

### Typing indicator not working

- This feature requires polling to be active
- Check network tab for API calls every 3 seconds

### Styling issues

- Ensure Tailwind CSS is properly configured
- Verify HeroUI components are imported correctly

## Contributing

When contributing to the chat feature:

1. Keep all chat logic in `Chat.tsx` (single-file architecture)
2. Update `chat.service.ts` for new API calls
3. Add new types to `api.ts`
4. Update backend views in `chat_views.py`
5. Test thoroughly on mobile and desktop
6. Ensure accessibility standards are met
7. Update this documentation

## License

Part of the NMTSA LMS project. See main project LICENSE file.
