import { Chip } from "@heroui/chip";
import { useTranslation } from "react-i18next";
import { Clock, CheckCircle, Video, BookOpen, FileQuestion, ClipboardList } from "lucide-react";

import type { LessonContent } from "../../types/api";

interface LessonHeaderProps {
  lesson: LessonContent;
  isCompleted: boolean;
}

export function LessonHeader({ lesson, isCompleted }: LessonHeaderProps) {
  const { t } = useTranslation();

  const lessonTypeIcons = {
    video: Video,
    reading: BookOpen,
    quiz: FileQuestion,
    assignment: ClipboardList,
  };

  const lessonTypeColors = {
    video: "primary",
    reading: "success",
    quiz: "warning",
    assignment: "danger",
  } as const;

  const Icon = lessonTypeIcons[lesson.type];

  const formatDuration = (minutes: number) => {
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;

    if (hours > 0) {
      return `${hours}h ${mins}m`;
    }

    return `${mins}m`;
  };

  return (
    <div className="bg-white border-b border-gray-200 py-6">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <div className="flex items-center gap-3 mb-3">
              <Chip
                color={lessonTypeColors[lesson.type]}
                startContent={<Icon className="w-4 h-4" />}
                variant="flat"
              >
                {t(`course.lessonType.${lesson.type}`)}
              </Chip>
              {isCompleted && (
                <Chip
                  color="success"
                  startContent={<CheckCircle className="w-4 h-4" />}
                  variant="flat"
                >
                  {t("course.completed")}
                </Chip>
              )}
              <div className="flex items-center gap-1 text-sm text-gray-600">
                <Clock className="w-4 h-4" />
                <span>{formatDuration(lesson.duration)}</span>
              </div>
            </div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">
              {lesson.title}
            </h1>
            {lesson.description && (
              <p className="text-gray-600 text-lg">{lesson.description}</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
