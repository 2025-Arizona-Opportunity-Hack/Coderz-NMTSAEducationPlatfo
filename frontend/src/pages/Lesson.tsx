import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { Helmet } from "react-helmet-async";
import { useTranslation } from "react-i18next";
import { Spinner } from "@heroui/spinner";
import { Card, CardBody } from "@heroui/card";

import { LessonHeader } from "../components/lesson/LessonHeader";
import { VideoPlayer } from "../components/lesson/VideoPlayer";
import { MarkdownContent } from "../components/lesson/MarkdownContent";
import { LessonNavigation } from "../components/lesson/LessonNavigation";
import { NotesSidebar } from "../components/lesson/NotesSidebar";
import { ResourcesList } from "../components/lesson/ResourcesList";
import { lessonService } from "../services/lesson.service";
import type { LessonContent, Note } from "../types/api";

export function Lesson() {
  const { courseId, lessonId } = useParams<{
    courseId: string;
    lessonId: string;
  }>();
  const { t } = useTranslation();

  const [lesson, setLesson] = useState<LessonContent | null>(null);
  const [notes, setNotes] = useState<Note[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isMarkingComplete, setIsMarkingComplete] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [currentVideoTime, setCurrentVideoTime] = useState(0);

  useEffect(() => {
    if (!courseId || !lessonId) return;

    const fetchLesson = async () => {
      try {
        setIsLoading(true);
        const data = await lessonService.getLessonContent(courseId, lessonId);

        setLesson(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load lesson");
      } finally {
        setIsLoading(false);
      }
    };

    fetchLesson();
  }, [courseId, lessonId]);

  useEffect(() => {
    if (!courseId || !lessonId) return;

    const fetchNotes = async () => {
      try {
        const data = await lessonService.getNotes(courseId, lessonId);

        setNotes(data.data);
      } catch (err) {
        console.error("Failed to load notes:", err);
      }
    };

    fetchNotes();
  }, [courseId, lessonId]);

  const handleMarkComplete = async () => {
    if (!courseId || !lessonId || !lesson) return;

    try {
      setIsMarkingComplete(true);
      await lessonService.markLessonComplete(courseId, lessonId);
      setLesson({ ...lesson, isCompleted: true });
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to mark complete");
    } finally {
      setIsMarkingComplete(false);
    }
  };

  const handleVideoProgress = async (currentTime: number) => {
    setCurrentVideoTime(currentTime);

    // Update progress every 10 seconds
    if (courseId && lessonId && Math.floor(currentTime) % 10 === 0) {
      try {
        await lessonService.updateLessonProgress(courseId, lessonId, {
          lastPosition: currentTime,
          timeSpent: currentTime,
          lessonId,
          courseId,
          isCompleted: lesson?.isCompleted || false,
        });
      } catch (err) {
        console.error("Failed to update progress:", err);
      }
    }
  };

  const handleAddNote = async (content: string, timestamp?: number) => {
    if (!courseId || !lessonId) return;

    const newNote = await lessonService.createNote(
      courseId,
      lessonId,
      content,
      timestamp,
    );

    setNotes([newNote, ...notes]);
  };

  const handleUpdateNote = async (noteId: string, content: string) => {
    if (!courseId || !lessonId) return;

    const updatedNote = await lessonService.updateNote(
      courseId,
      lessonId,
      noteId,
      content,
    );

    setNotes(notes.map((n) => (n.id === noteId ? updatedNote : n)));
  };

  const handleDeleteNote = async (noteId: string) => {
    if (!courseId || !lessonId) return;

    await lessonService.deleteNote(courseId, lessonId, noteId);
    setNotes(notes.filter((n) => n.id !== noteId));
  };

  if (isLoading) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <Spinner label={t("common.loading")} size="lg" />
      </div>
    );
  }

  if (error || !lesson || !courseId) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <Card>
          <CardBody>
            <div className="text-center py-12">
              <p className="text-red-600 text-lg">
                {error || "Lesson not found"}
              </p>
            </div>
          </CardBody>
        </Card>
      </div>
    );
  }

  return (
    <>
      <Helmet>
        <title>{`${lesson.title} - NMTSA Learn`}</title>
        <meta content={lesson.description} name="description" />
      </Helmet>

      <div className="min-h-screen bg-gray-50">
        <LessonHeader isCompleted={lesson.isCompleted || false} lesson={lesson} />

        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* Main Content */}
            <div className="lg:col-span-2 space-y-6">
              {/* Video Player */}
              {lesson.type === "video" && lesson.videoUrl && (
                <VideoPlayer
                  videoUrl={lesson.videoUrl}
                  onComplete={handleMarkComplete}
                  onProgress={handleVideoProgress}
                  captions={lesson.captions}
                />
              )}

              {/* Reading Content */}
              {lesson.type === "reading" && lesson.content && (
                <Card>
                  <CardBody className="p-8">
                    <MarkdownContent content={lesson.content} />
                  </CardBody>
                </Card>
              )}

              {/* Resources */}
              {lesson.resources && lesson.resources.length > 0 && (
                <ResourcesList resources={lesson.resources} />
              )}
            </div>

            {/* Sidebar */}
            <div className="lg:col-span-1">
              <div className="sticky top-4">
                <Card>
                  <CardBody className="p-0 h-[600px]">
                    <NotesSidebar
                      currentTimestamp={
                        lesson.type === "video" ? currentVideoTime : undefined
                      }
                      notes={notes}
                      onAddNote={handleAddNote}
                      onDeleteNote={handleDeleteNote}
                      onUpdateNote={handleUpdateNote}
                    />
                  </CardBody>
                </Card>
              </div>
            </div>
          </div>
        </div>

        <LessonNavigation
          courseId={courseId}
          isCompleted={lesson.isCompleted || false}
          isMarkingComplete={isMarkingComplete}
          nextLesson={lesson.nextLesson}
          previousLesson={lesson.previousLesson}
          onMarkComplete={handleMarkComplete}
        />
      </div>
    </>
  );
}
