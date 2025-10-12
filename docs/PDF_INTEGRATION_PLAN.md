# PDF Lesson Integration - Complete Implementation Plan

## Project Overview
Integrating PDF lessons into the NMTSA LMS to complement existing Video and Blog lesson types. This document provides a detailed, non-breaking implementation plan for the remaining work.

---

## ✅ COMPLETED PHASES (1 & 2)

### Phase 1: Database & Models ✅
- Applied `PDFLesson` migration
- Updated `Lesson.LESSON_TYPES` to include `'pdf'`
- Created `PDFLesson` model with `pdf_file` and `description` fields
- Model stores PDFs in `media/pdfs/` directory

### Phase 2: Backend Logic ✅
- Created `PDFLessonForm` with validation (PDF only, 50MB max)
- Updated `LessonForm` validation for PDF lesson duration requirements
- Updated teacher views:
  - `_get_lesson_forms()` - Returns 4 forms including PDF
  - `module_detail()` - Includes `pdf_form` in context
  - `lesson_create()` - Handles PDF lesson creation with proper cleanup
  - `lesson_edit()` - Handles PDF lesson editing
  - `course_preview()` - Prefetches PDF lessons
  - `lesson_preview()` - Returns PDF data in API
- Created `serve_pdf()` endpoint for serving PDFs with inline disposition

---

## 🔄 REMAINING PHASES (3-6)

## Phase 3: Teacher Frontend Templates

### 3.1 Update `lesson_form.html` Template
**File:** `nmtsa_lms/teacher_dash/templates/teacher_dash/lesson_form.html`

**Changes Required:**
1. **Add PDF Fieldset** (after blog fieldset, before form actions)
   ```django-html
   <fieldset data-lesson-fieldset="pdf">
       <legend>PDF Lesson</legend>
       {{ pdf_form.non_field_errors }}
       {% for field in pdf_form %}
       <div class="form-field{% if field.errors %} has-error{% endif %}">
           <label for="{{ field.id_for_label }}">{{ field.label }}</label>
           {{ field }}
           {% if field.help_text %}<small class="help-text">{{ field.help_text }}</small>{% endif %}
           {% for error in field.errors %}<small class="error-text">{{ error }}</small>{% endfor %}
       </div>
       {% endfor %}
   </fieldset>
   ```

2. **Update JavaScript for PDF Toggling** (in `{% block extra_js %}`)
   ```javascript
   // Add PDF fieldset collection
   const pdfFieldset = document.querySelector('[data-lesson-fieldset="pdf"]');
   
   // Collect PDF inputs for toggling
   const pdfInputs = pdfFieldset ? Array.from(pdfFieldset.querySelectorAll('input, select, textarea')) : [];
   
   // Update initialRequired/initialDisabled maps
   videoInputs.concat(blogInputs).concat(pdfInputs).forEach(el => {
       initialRequired.set(el, !!el.required);
       initialDisabled.set(el, !!el.disabled);
   });
   
   // Update toggleLessonFields function
   function toggleLessonFields() {
       const value = typeSelect ? typeSelect.value : '';
       if (!typeSelect) return;
   
       // Video fieldset toggle (existing)
       if (videoFieldset) {
           const showVideo = value === 'video';
           videoFieldset.style.display = showVideo ? 'flex' : 'none';
           videoFieldset.setAttribute('aria-hidden', showVideo ? 'false' : 'true');
           videoInputs.forEach(el => {
               el.disabled = !showVideo ? true : (initialDisabled.get(el) || false);
               el.required = showVideo ? (initialRequired.get(el) || false) : false;
           });
       }
   
       // Blog fieldset toggle (existing)
       if (blogFieldset) {
           const showBlog = value === 'blog';
           blogFieldset.style.display = showBlog ? 'flex' : 'none';
           blogFieldset.setAttribute('aria-hidden', showBlog ? 'false' : 'true');
           blogInputs.forEach(el => {
               el.disabled = !showBlog ? true : (initialDisabled.get(el) || false);
               el.required = showBlog ? (initialRequired.get(el) || false) : false;
           });
       }
   
       // PDF fieldset toggle (NEW)
       if (pdfFieldset) {
           const showPdf = value === 'pdf';
           pdfFieldset.style.display = showPdf ? 'flex' : 'none';
           pdfFieldset.setAttribute('aria-hidden', showPdf ? 'false' : 'true');
           pdfInputs.forEach(el => {
               el.disabled = !showPdf ? true : (initialDisabled.get(el) || false);
               el.required = showPdf ? (initialRequired.get(el) || false) : false;
           });
       }
   
       // Duration field toggle (UPDATE)
       if (durationFieldWrapper) {
           const showDuration = value === 'blog' || value === 'pdf'; // Include PDF
           durationFieldWrapper.style.display = showDuration ? 'flex' : 'none';
           if (durationInput) {
               durationInput.disabled = !showDuration;
               durationInput.required = showDuration;
           }
       }
   }
   ```

**Risk Level:** Low
- Non-breaking: Only adds new UI elements, doesn't modify existing ones
- Validation: Backend already validates PDF lessons, frontend just needs to display form

---

### 3.2 Update `module_detail.html` Template
**File:** `nmtsa_lms/teacher_dash/templates/teacher_dash/module_detail.html`

**Changes Required:**
1. **Add PDF Icon in Lesson List** (update lesson type icon logic)
   ```django-html
   <!-- Find the lesson type display section and add PDF case -->
   {% if lesson.lesson_type == 'video' %}
       <svg><!-- video icon --></svg>
   {% elif lesson.lesson_type == 'blog' %}
       <svg><!-- blog icon --></svg>
   {% elif lesson.lesson_type == 'pdf' %}
       <svg width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
           <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
           <polyline points="14 2 14 8 20 8"/>
           <line x1="12" y1="18" x2="12" y2="12"/>
           <line x1="9" y1="15" x2="15" y2="15"/>
       </svg>
   {% endif %}
   ```

2. **Update Lesson Type Badge** (if exists)
   ```django-html
   {% if lesson.lesson_type == 'pdf' %}
       <span class="badge badge-purple">PDF</span>
   {% endif %}
   ```

**Risk Level:** Low
- Non-breaking: Only adds display logic for new lesson type
- No existing functionality affected

---

## Phase 4: Student Views & Templates

### 4.1 Update Student Views
**File:** `nmtsa_lms/student_dash/views.py`

**Changes Required in `lesson_view()` function:**
```python
@student_required
@onboarding_complete_required
def lesson_view(request, course_slug, module_slug, lesson_slug):
    """View a specific lesson"""
    session_user = request.session.get('user')
    user_id = session_user.get('user_id')
    user = User.objects.get(id=user_id)

    course = _get_course_by_slug_or_404(course_slug)
    enrollment = get_object_or_404(Enrollment, user=user, course=course)
    module = _get_module_by_slug_or_404(course, module_slug)
    current_lesson = _get_lesson_by_slug_or_404(module, lesson_slug)

    # Load video progress for video lessons
    video_progress = None
    if current_lesson.lesson_type == 'video':
        try:
            video_obj = VideoLesson.objects.get(lesson=current_lesson)
            video_progress = VideoProgress.objects.filter(
                enrollment=enrollment,
                lesson=current_lesson
            ).first()
        except VideoLesson.DoesNotExist:
            video_obj = None
        cast(Any, current_lesson).video = video_obj
    elif current_lesson.lesson_type == 'blog':
        try:
            blog_obj = BlogLesson.objects.get(lesson=current_lesson)
        except BlogLesson.DoesNotExist:
            blog_obj = None
        cast(Any, current_lesson).blog = blog_obj
    # ADD THIS BLOCK FOR PDF LESSONS
    elif current_lesson.lesson_type == 'pdf':
        try:
            from teacher_dash.models import PDFLesson  # Import at top of file
            pdf_obj = PDFLesson.objects.get(lesson=current_lesson)
        except PDFLesson.DoesNotExist:
            pdf_obj = None
        cast(Any, current_lesson).pdf = pdf_obj

    # ... rest of function remains unchanged
```

**Import Addition at Top of File:**
```python
from teacher_dash.models import Course, Module, Lesson, VideoLesson, BlogLesson, PDFLesson  # Add PDFLesson
```

**Risk Level:** Low
- Non-breaking: Only adds new conditional branch
- Follows existing pattern for video/blog lessons
- No changes to existing video/blog logic

---

### 4.2 Update `learning.html` Template
**File:** `nmtsa_lms/nmtsa_lms/templates/student_dash/learning.html`

**Changes Required:**

1. **Update Sidebar Lesson Icons** (around line 60-80)
   ```django-html
   <!-- Lesson Status Icon -->
   <div style="width: 24px; height: 24px; flex-shrink: 0;">
       {% if lesson.id in completed_lesson_ids %}
       <svg width="24" height="24" fill="none" stroke="#66BB6A" stroke-width="2" viewBox="0 0 24 24">
           <circle cx="12" cy="12" r="10"/>
           <path d="m9 12 2 2 4-4"/>
       </svg>
       {% elif lesson.lesson_type == 'video' %}
       <svg width="24" height="24" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
           <circle cx="12" cy="12" r="10"/>
           <polygon points="10 8 16 12 10 16 10 8"/>
       </svg>
       {% elif lesson.lesson_type == 'pdf' %}
       <!-- ADD THIS PDF ICON -->
       <svg width="24" height="24" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
           <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
           <polyline points="14 2 14 8 20 8"/>
           <line x1="12" y1="18" x2="12" y2="12"/>
           <line x1="9" y1="15" x2="15" y2="15"/>
       </svg>
       {% else %}
       <!-- Blog icon (existing) -->
       <svg>...</svg>
       {% endif %}
   </div>
   ```

2. **Update Lesson Header Type Display** (around line 120)
   ```django-html
   <div style="color: var(--text-secondary); font-size: calc(0.875rem * var(--font-scale)); margin-bottom: 4px;">
       {% if current_lesson.lesson_type == 'video' %}
           Video Lesson
       {% elif current_lesson.lesson_type == 'pdf' %}
           PDF Document
       {% else %}
           Article
       {% endif %}
   </div>
   ```

3. **Add PDF Viewer Section** (after blog section, before closing lesson-content div)
   ```django-html
   {% elif current_lesson.lesson_type == 'pdf' %}
       <!-- PDF Lesson -->
       {% if current_lesson.pdf %}
       <div style="max-width: 1200px; margin: 0 auto;">
           <!-- PDF Description (if available) -->
           {% if current_lesson.pdf.description %}
           <div style="background: var(--bg-card); border-radius: var(--radius-lg); border: 1px solid var(--border-color); padding: var(--spacing-xl); margin-bottom: var(--spacing-xl);">
               <h3 style="margin-bottom: var(--spacing-md); font-size: calc(1.25rem * var(--font-scale));">About this Document</h3>
               <div style="color: var(--text-primary); line-height: 1.8;">
                   {{ current_lesson.pdf.description|safe }}
               </div>
           </div>
           {% endif %}

           <!-- PDF Viewer Embed -->
           <div style="background: var(--bg-card); border-radius: var(--radius-lg); border: 1px solid var(--border-color); overflow: hidden;">
               <iframe 
                   src="{% url 'serve_pdf' current_lesson.pdf.pdf_file.name %}"
                   style="width: 100%; height: 800px; border: none; display: block;"
                   title="{{ current_lesson.title }}"
                   type="application/pdf">
                   <p style="padding: var(--spacing-xl); text-align: center;">
                       Your browser doesn't support PDF viewing. 
                       <a href="{% url 'serve_pdf' current_lesson.pdf.pdf_file.name %}" 
                          download="{{ current_lesson.title }}.pdf"
                          style="color: var(--primary); text-decoration: underline;">
                           Download the PDF
                       </a>
                   </p>
               </iframe>
           </div>

           <!-- Download Button -->
           <div style="margin-top: var(--spacing-lg); text-align: center;">
               <a href="{% url 'serve_pdf' current_lesson.pdf.pdf_file.name %}" 
                  download="{{ current_lesson.title }}.pdf"
                  style="display: inline-flex; align-items: center; gap: var(--spacing-sm); padding: var(--spacing-md) var(--spacing-xl); background: var(--primary); color: white; border-radius: var(--radius-md); text-decoration: none; font-weight: 600; transition: opacity 0.2s;">
                   <svg width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                       <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                       <polyline points="7 10 12 15 17 10"/>
                       <line x1="12" y1="15" x2="12" y2="3"/>
                   </svg>
                   Download PDF
               </a>
           </div>
       </div>
       {% else %}
       <div style="text-align: center; padding: var(--spacing-2xl); color: var(--text-muted);">
           <p>PDF document not available for this lesson.</p>
       </div>
       {% endif %}
   {% endif %}
   ```

**Risk Level:** Low
- Non-breaking: Only adds new conditional blocks
- Existing video/blog display logic unchanged
- Graceful fallback if PDF not found

---

## Phase 5: Supermemory Integration (AI Search Enhancement)

### 5.1 Install PDF Processing Library
**Command:**
```bash
pip install PyPDF2
# OR for better text extraction:
pip install pypdf
```

**Add to Requirements:**
```txt
# Add to nmtsa_lms/requirements.txt
PyPDF2>=3.0.0
```

**Risk Level:** Low
- External dependency, no code changes required
- Only used in background processing

---

### 5.2 Create PDF Text Extraction Utility
**File:** `nmtsa_lms/lms/pdf_extractor.py` (NEW FILE)

```python
"""
PDF Text Extraction Utility
Extracts searchable text from PDF files for Supermemory indexing
"""
import logging
from pathlib import Path
from typing import Optional

try:
    from PyPDF2 import PdfReader
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False
    logging.warning("PyPDF2 not installed. PDF text extraction disabled.")

logger = logging.getLogger(__name__)


def extract_text_from_pdf(pdf_path: str, max_pages: int = 50) -> Optional[str]:
    """
    Extract text content from a PDF file.
    
    Args:
        pdf_path: Absolute path to PDF file
        max_pages: Maximum number of pages to extract (default 50 to avoid memory issues)
        
    Returns:
        Extracted text as string, or None if extraction fails
    """
    if not PDF_AVAILABLE:
        logger.warning("PyPDF2 not available, skipping PDF text extraction")
        return None
    
    try:
        if not Path(pdf_path).exists():
            logger.error(f"PDF file not found: {pdf_path}")
            return None
        
        reader = PdfReader(pdf_path)
        num_pages = len(reader.pages)
        
        # Limit pages to avoid memory issues with large PDFs
        pages_to_extract = min(num_pages, max_pages)
        
        text_parts = []
        for page_num in range(pages_to_extract):
            try:
                page = reader.pages[page_num]
                text = page.extract_text()
                if text and text.strip():
                    text_parts.append(text.strip())
            except Exception as e:
                logger.warning(f"Error extracting text from page {page_num}: {e}")
                continue
        
        if not text_parts:
            logger.warning(f"No text extracted from PDF: {pdf_path}")
            return None
        
        full_text = "\n\n".join(text_parts)
        
        # Limit total text length to avoid overwhelming Supermemory
        max_chars = 10000  # 10k characters ~= 2500 words
        if len(full_text) > max_chars:
            full_text = full_text[:max_chars] + "..."
            logger.info(f"Truncated PDF text to {max_chars} characters")
        
        return full_text
        
    except Exception as e:
        logger.error(f"Error extracting PDF text: {e}")
        return None


def get_pdf_summary(pdf_path: str) -> str:
    """
    Get a brief summary of PDF content for indexing.
    
    Args:
        pdf_path: Absolute path to PDF file
        
    Returns:
        First few paragraphs or empty string if extraction fails
    """
    full_text = extract_text_from_pdf(pdf_path, max_pages=3)  # Only first 3 pages
    
    if not full_text:
        return ""
    
    # Get first 500 characters as summary
    summary = full_text[:500].strip()
    if len(full_text) > 500:
        # Find last complete sentence
        last_period = summary.rfind('.')
        if last_period > 100:  # Ensure reasonable length
            summary = summary[:last_period + 1]
        else:
            summary += "..."
    
    return summary
```

**Risk Level:** Low
- Self-contained utility, no dependencies on existing code
- Graceful fallback if PyPDF2 not installed
- Error handling prevents crashes

---

### 5.3 Update Course Indexer for PDF Content
**File:** `nmtsa_lms/lms/course_indexer.py`

**Changes Required in `build_lesson_document()` function:**

```python
def build_lesson_document(lesson, module, course) -> Tuple[str, Dict[str, Any]]:
    """
    Build a searchable document for a lesson.

    For BlogLesson: includes full blog content
    For VideoLesson: includes only title and tags (NO transcript)
    For PDFLesson: includes PDF text excerpt for semantic search (NEW)

    Args:
        lesson: Lesson model instance
        module: Parent Module model instance
        course: Parent Course model instance

    Returns:
        Tuple of (content, metadata)
    """
    try:
        from django.conf import settings
        import os
        
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
                pass

        # ADD THIS BLOCK FOR PDF LESSONS
        # Add PDF content excerpt if it's a PDF lesson
        elif lesson.lesson_type == 'pdf':
            try:
                from .pdf_extractor import get_pdf_summary
                pdf = lesson.pdf
                
                if pdf and pdf.pdf_file:
                    # Get PDF file path
                    pdf_path = os.path.join(settings.MEDIA_ROOT, pdf.pdf_file.name)
                    
                    # Extract summary
                    pdf_summary = get_pdf_summary(pdf_path)
                    if pdf_summary:
                        content_parts.append(f"Document Excerpt: {pdf_summary}")
                    
                    # Add description if available
                    if pdf.description:
                        content_parts.append(f"Description: {pdf.description}")
            except Exception as e:
                logger.warning(f"Could not extract PDF content for lesson {lesson.id}: {e}")
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
```

**Risk Level:** Low
- Only adds new conditional block for PDF lessons
- Existing blog/video logic unchanged
- Exception handling prevents crashes
- Graceful degradation if PDF extraction fails

---

### 5.4 Add Signal Handler for Automatic Indexing
**File:** `nmtsa_lms/teacher_dash/signals.py`

**Check if this file exists and update it, or reference location if signals are elsewhere:**

```python
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import PDFLesson
from lms.course_memory import add_lesson_to_memory
from lms.course_indexer import build_lesson_document, get_course_and_module_from_lesson
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=PDFLesson)
def index_pdf_lesson_on_save(sender, instance, created, **kwargs):
    """
    Automatically index PDF lesson in Supermemory when created/updated
    """
    try:
        lesson = instance.lesson
        module, course = get_course_and_module_from_lesson(lesson)
        
        if not module or not course:
            logger.warning(f"Could not find course/module for PDF lesson {lesson.id}")
            return
        
        # Only index published courses
        if not course.is_published or not course.admin_approved:
            logger.info(f"Skipping indexing for unpublished PDF lesson {lesson.id}")
            return
        
        # Build and add to memory
        content, metadata = build_lesson_document(lesson, module, course)
        
        from lms.supermemory_client import get_supermemory_client
        supermemory = get_supermemory_client()
        
        if supermemory:
            supermemory.add_memory(
                content=content,
                metadata=metadata,
                container_tag='nmtsa-lessons',
                custom_id=f"lesson-{lesson.id}"
            )
            logger.info(f"Successfully indexed PDF lesson {lesson.id}")
        
    except Exception as e:
        logger.error(f"Error indexing PDF lesson: {e}")
```

**Ensure signals are imported in `teacher_dash/apps.py`:**
```python
from django.apps import AppConfig


class TeacherDashConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'teacher_dash'

    def ready(self):
        import teacher_dash.signals  # Ensure signals are loaded
```

**Risk Level:** Low
- Automatic background process
- Doesn't affect user-facing functionality
- Graceful failure if Supermemory unavailable

---

## Phase 6: URL Configuration

### 6.1 Add PDF Serving URL Pattern
**File:** `nmtsa_lms/teacher_dash/urls.py`

**Add this line after the `serve_video` URL pattern (around line 38):**

```python
urlpatterns = [
    # ... existing patterns ...
    path("videos/<path:video_path>", views.serve_video, name="serve_video"),
    # ADD THIS LINE:
    path("pdfs/<path:pdf_path>", views.serve_pdf, name="serve_pdf"),
    path("courses/<slug:course_slug>/analytics/", views.course_analytics, name="teacher_course_analytics"),
    # ... rest of patterns ...
]
```

**Risk Level:** Low
- Simple URL pattern addition
- Doesn't conflict with existing routes
- Backend function already implemented

---

## 📋 IMPLEMENTATION CHECKLIST

Use this checklist to track progress:

### Phase 3: Teacher Frontend
- [ ] 3.1: Update `lesson_form.html` - Add PDF fieldset
- [ ] 3.2: Update `lesson_form.html` - Update JavaScript for PDF toggling
- [ ] 3.3: Update `module_detail.html` - Add PDF icon
- [ ] 3.4: Test lesson creation with all three types (video, blog, PDF)
- [ ] 3.5: Test lesson editing with PDF files
- [ ] 3.6: Verify duration field shows for blog AND PDF

### Phase 4: Student Views
- [ ] 4.1: Update `student_dash/views.py` - Add PDFLesson import
- [ ] 4.2: Update `lesson_view()` - Add PDF lesson loading
- [ ] 4.3: Update `learning.html` - Add PDF icon in sidebar
- [ ] 4.4: Update `learning.html` - Add PDF header type display
- [ ] 4.5: Update `learning.html` - Add PDF viewer section
- [ ] 4.6: Test PDF viewing in student interface
- [ ] 4.7: Test PDF download functionality
- [ ] 4.8: Verify mark as complete works for PDFs

### Phase 5: Supermemory Integration
- [ ] 5.1: Install PyPDF2 library (`pip install PyPDF2`)
- [ ] 5.2: Add PyPDF2 to `requirements.txt`
- [ ] 5.3: Create `lms/pdf_extractor.py` file
- [ ] 5.4: Test PDF text extraction utility
- [ ] 5.5: Update `lms/course_indexer.py` - Add PDF block
- [ ] 5.6: Update `teacher_dash/signals.py` - Add PDF signal
- [ ] 5.7: Ensure signals imported in `apps.py`
- [ ] 5.8: Test Supermemory indexing with new PDF lesson
- [ ] 5.9: Test semantic search finds PDF lessons

### Phase 6: URL Configuration
- [ ] 6.1: Add PDF URL pattern to `teacher_dash/urls.py`
- [ ] 6.2: Test PDF serving endpoint directly
- [ ] 6.3: Verify PDF inline viewing works

### Final Testing
- [ ] Create a test course with all three lesson types
- [ ] Verify course preview shows PDFs correctly
- [ ] Verify student can enroll and view PDFs
- [ ] Test PDF download on multiple browsers
- [ ] Verify progress tracking works for PDFs
- [ ] Test mobile responsiveness of PDF viewer
- [ ] Verify Supermemory semantic search includes PDFs
- [ ] Test file size validation (50MB limit)
- [ ] Test file type validation (.pdf only)
- [ ] Verify course submission/approval workflow with PDFs

---

## 🔒 NON-BREAKING GUARANTEES

### Existing Functionality Preserved
✅ **Video Lessons**: No changes to video upload, serving, or progress tracking
✅ **Blog Lessons**: No changes to blog content or image handling
✅ **Course Management**: All existing teacher workflows unchanged
✅ **Student Progress**: Existing progress calculation unaffected
✅ **Authentication**: No changes to auth flows
✅ **Supermemory**: Graceful fallback if PDF extraction fails
✅ **URL Routing**: New PDF routes don't conflict with existing routes

### Safety Features
- **Backward Compatibility**: All existing database records work as-is
- **Graceful Degradation**: PDF features fail silently if dependencies missing
- **Validation**: Backend prevents invalid PDF uploads (50MB, .pdf only)
- **Security**: PDF serving uses same security checks as video serving
- **Memory Safety**: PDF text extraction limited to prevent memory issues

---

## 🧪 TESTING STRATEGY

### Unit Testing Checklist
```python
# Test cases to create/verify

# PDF Form Validation
- test_pdf_form_valid_file()
- test_pdf_form_invalid_extension()
- test_pdf_form_file_too_large()

# PDF Extraction
- test_extract_text_from_valid_pdf()
- test_extract_text_from_corrupt_pdf()
- test_extract_text_truncation()

# Student View
- test_pdf_lesson_view_authenticated()
- test_pdf_lesson_progress_tracking()

# Supermemory Integration
- test_pdf_lesson_indexing()
- test_semantic_search_finds_pdf()
```

### Manual Testing Checklist
1. **Teacher Workflow**
   - Create course → Add module → Create PDF lesson
   - Upload valid PDF (< 50MB)
   - Try uploading > 50MB (should fail)
   - Try uploading .docx (should fail)
   - Edit PDF lesson (replace file)
   - Preview PDF in course preview

2. **Student Workflow**
   - Enroll in course with PDF
   - Navigate to PDF lesson
   - View PDF in browser
   - Download PDF
   - Mark PDF lesson complete
   - Check progress percentage updates

3. **Cross-Browser Testing**
   - Chrome: PDF inline viewing
   - Firefox: PDF inline viewing
   - Safari: PDF inline viewing
   - Edge: PDF inline viewing
   - Mobile Safari: PDF viewing/download
   - Mobile Chrome: PDF viewing/download

---

## 📊 ESTIMATED EFFORT

| Phase | Estimated Time | Complexity |
|-------|---------------|------------|
| Phase 3.1-3.2: Teacher Templates | 2-3 hours | Medium |
| Phase 4: Student Views | 2-3 hours | Medium |
| Phase 5: Supermemory | 3-4 hours | Medium-High |
| Phase 6: URL Config | 15 minutes | Low |
| Testing & QA | 2-3 hours | Medium |
| **Total** | **10-14 hours** | **Medium** |

---

## 🚀 DEPLOYMENT NOTES

### Pre-Deployment Checklist
- [ ] Run migrations (already applied)
- [ ] Install PyPDF2 on production server
- [ ] Create `media/pdfs/` directory with write permissions
- [ ] Test PDF upload in staging environment
- [ ] Verify Supermemory API key configured
- [ ] Test PDF serving over HTTPS
- [ ] Check Content Security Policy allows PDF iframes

### Production Environment Variables
```bash
# Ensure these are set
MEDIA_ROOT=/path/to/media
MEDIA_URL=/media/
SUPERMEMORY_API_KEY=your_key_here
```

### nginx Configuration (if applicable)
```nginx
# Ensure PDF files served with correct MIME type
location /media/pdfs/ {
    alias /path/to/media/pdfs/;
    add_header Content-Type application/pdf;
    add_header Content-Disposition inline;
}
```

---

## 🆘 TROUBLESHOOTING GUIDE

### Common Issues & Solutions

**Issue**: PDF doesn't display in browser iframe
- **Solution**: Check browser's PDF viewer settings, try download link instead

**Issue**: File upload fails silently
- **Solution**: Check `media/pdfs/` directory permissions (775 or 755)

**Issue**: Supermemory indexing fails
- **Solution**: Check PyPDF2 installed, verify PDF is not corrupted

**Issue**: PDF text extraction times out
- **Solution**: Reduce `max_pages` parameter in `extract_text_from_pdf()`

**Issue**: Progress tracking doesn't work for PDFs
- **Solution**: Verify `mark_lesson_complete` view handles all lesson types

---

## 📚 REFERENCES

### Key Files Modified/Created
- `teacher_dash/models.py` - PDFLesson model (existing)
- `teacher_dash/forms.py` - PDFLessonForm (existing)
- `teacher_dash/views.py` - serve_pdf() (existing)
- `teacher_dash/templates/teacher_dash/lesson_form.html` - **TO UPDATE**
- `teacher_dash/templates/teacher_dash/module_detail.html` - **TO UPDATE**
- `student_dash/views.py` - lesson_view() - **TO UPDATE**
- `nmtsa_lms/templates/student_dash/learning.html` - **TO UPDATE**
- `lms/pdf_extractor.py` - **TO CREATE**
- `lms/course_indexer.py` - **TO UPDATE**
- `teacher_dash/signals.py` - **TO UPDATE**
- `teacher_dash/urls.py` - **TO UPDATE**

### Django Resources
- FileField Documentation: https://docs.djangoproject.com/en/stable/ref/models/fields/#filefield
- File Uploads: https://docs.djangoproject.com/en/stable/topics/http/file-uploads/
- Signals: https://docs.djangoproject.com/en/stable/topics/signals/

### External Libraries
- PyPDF2: https://pypdf2.readthedocs.io/
- Supermemory SDK: (check internal docs)

---

## ✅ SUCCESS CRITERIA

Implementation is complete when:
1. ✅ Teachers can create/edit PDF lessons via form
2. ✅ PDF file validation works (size, type)
3. ✅ Students can view PDFs inline in browser
4. ✅ Students can download PDFs
5. ✅ PDF lessons tracked in progress calculation
6. ✅ PDF content indexed in Supermemory
7. ✅ Semantic search returns relevant PDF lessons
8. ✅ All existing features (video, blog) still work
9. ✅ No console errors or Python exceptions
10. ✅ Mobile-responsive PDF viewing

---

## 📞 SUPPORT

If you encounter issues:
1. Check this document's Troubleshooting section
2. Review error logs in Django console
3. Verify all checklist items completed
4. Test in isolation (create minimal test case)
5. Check browser console for JavaScript errors

---

**Document Version**: 1.0  
**Last Updated**: 2025-10-12  
**Author**: GitHub Copilot  
**Status**: Ready for Implementation
