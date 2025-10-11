import { Button } from "@heroui/button";
import { Progress } from "@heroui/progress";
import { useTranslation } from "react-i18next";
import { ChevronLeft, ChevronRight, CheckCircle } from "lucide-react";
import { useNavigate } from "react-router-dom";

interface LessonNavigationProps {
  courseId: string;
  previousLesson?: { id: string; title: string };
  nextLesson?: { id: string; title: string };
  isCompleted: boolean;
  onMarkComplete?: () => void;
  isMarkingComplete?: boolean;
  progress?: number;
}

export function LessonNavigation({
  courseId,
  previousLesson,
  nextLesson,
  isCompleted,
  onMarkComplete,
  isMarkingComplete,
  progress = 0,
}: LessonNavigationProps) {
  const { t } = useTranslation();
  const navigate = useNavigate();

  return (
    <div className="bg-white border-t border-gray-200 py-6">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Progress Bar */}
        {progress > 0 && (
          <div className="mb-6">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium text-gray-700">
                {t("lesson.courseProgress")}
              </span>
              <span className="text-sm font-semibold text-gray-900">
                {progress}%
              </span>
            </div>
            <Progress
              aria-label="Course progress"
              color="primary"
              size="md"
              value={progress}
            />
          </div>
        )}

        {/* Navigation Buttons */}
        <div className="flex items-center justify-between">
          <div>
            {previousLesson && (
              <Button
                startContent={<ChevronLeft className="w-5 h-5" />}
                variant="flat"
                onPress={() =>
                  navigate(`/courses/${courseId}/lessons/${previousLesson.id}`)
                }
              >
                {t("lesson.previousLesson")}
              </Button>
            )}
          </div>

          <div className="flex items-center gap-3">
            {!isCompleted && (
              <Button
                color="success"
                isLoading={isMarkingComplete}
                startContent={<CheckCircle className="w-5 h-5" />}
                onPress={onMarkComplete}
              >
                {t("lesson.markComplete")}
              </Button>
            )}

            {nextLesson && (
              <Button
                color="primary"
                endContent={<ChevronRight className="w-5 h-5" />}
                onPress={() =>
                  navigate(`/courses/${courseId}/lessons/${nextLesson.id}`)
                }
              >
                {t("lesson.nextLesson")}
              </Button>
            )}

            {!nextLesson && isCompleted && (
              <Button
                color="primary"
                onPress={() => navigate(`/courses/${courseId}`)}
              >
                {t("lesson.backToCourse")}
              </Button>
            )}
          </div>
        </div>

        {/* Lesson Titles */}
        <div className="flex items-center justify-between mt-4 text-sm text-gray-600">
          <div className="flex-1">
            {previousLesson && (
              <p className="truncate">{previousLesson.title}</p>
            )}
          </div>
          <div className="flex-1 text-right">
            {nextLesson && <p className="truncate">{nextLesson.title}</p>}
          </div>
        </div>
      </div>
    </div>
  );
}
