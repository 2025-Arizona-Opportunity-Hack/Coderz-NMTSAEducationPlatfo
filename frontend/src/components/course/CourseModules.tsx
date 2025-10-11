import type { Module } from "../../types/api";

import { Accordion, AccordionItem } from "@heroui/accordion";
import { Chip } from "@heroui/chip";
import { useTranslation } from "react-i18next";
import { PlayCircle, FileText, CheckCircle, Lock, Clock } from "lucide-react";
import { Link } from "react-router-dom";

interface CourseModulesProps {
  modules: Module[];
  courseId: string;
  isEnrolled?: boolean;
}

export function CourseModules({
  modules,
  courseId,
  isEnrolled,
}: CourseModulesProps) {
  const { t } = useTranslation();

  const getLessonIcon = (type: string) => {
    switch (type) {
      case "video":
        return <PlayCircle className="w-5 h-5" />;
      case "reading":
        return <FileText className="w-5 h-5" />;
      default:
        return <FileText className="w-5 h-5" />;
    }
  };

  const formatDuration = (minutes: number) => {
    if (minutes < 60) return `${minutes} min`;

    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;

    return mins > 0 ? `${hours}h ${mins}m` : `${hours}h`;
  };

  return (
    <div className="w-full">
      <h2 className="text-2xl font-bold mb-4">{t("course.curriculum")}</h2>
      <Accordion
        className="gap-2"
        itemClasses={{
          base: "border border-gray-200 rounded-lg",
          title: "font-semibold text-lg",
          trigger: "px-6 py-4",
          content: "px-6 pb-4",
        }}
        variant="bordered"
      >
        {modules.map((module, index) => {
          const totalLessons = module.lessons.length;
          const completedLessons = module.lessons.filter(
            (l) => l.isCompleted,
          ).length;
          const moduleProgress =
            totalLessons > 0 ? (completedLessons / totalLessons) * 100 : 0;

          return (
            <AccordionItem
              key={module.id}
              aria-label={module.title}
              startContent={
                <div className="flex items-center gap-3">
                  <div className="flex-shrink-0 w-10 h-10 rounded-full bg-blue-100 flex items-center justify-center font-semibold text-blue-600">
                    {index + 1}
                  </div>
                </div>
              }
              subtitle={
                <div className="flex items-center gap-4 mt-2 text-sm">
                  <span className="text-gray-600">
                    {totalLessons} {t("course.lessons")}
                  </span>
                  {isEnrolled && (
                    <Chip color="primary" size="sm" variant="flat">
                      {Math.round(moduleProgress)}% {t("common.complete")}
                    </Chip>
                  )}
                </div>
              }
              title={module.title}
            >
              <div className="space-y-2">
                {module.lessons.map((lesson, lessonIndex) => {
                  const isLocked = !isEnrolled && lessonIndex > 0;
                  const content = (
                    <div
                      className={`flex items-center justify-between p-3 rounded-lg hover:bg-gray-50 transition-colors ${
                        isLocked
                          ? "opacity-60"
                          : "cursor-pointer hover:shadow-sm"
                      }`}
                    >
                      <div className="flex items-center gap-3 flex-1">
                        <div className="text-gray-400">
                          {lesson.isCompleted ? (
                            <CheckCircle className="w-5 h-5 text-green-500" />
                          ) : isLocked ? (
                            <Lock className="w-5 h-5" />
                          ) : (
                            getLessonIcon(lesson.type)
                          )}
                        </div>
                        <div className="flex-1">
                          <h4 className="font-medium text-gray-900">
                            {lesson.title}
                          </h4>
                          {lesson.description && (
                            <p className="text-sm text-gray-600 mt-1">
                              {lesson.description}
                            </p>
                          )}
                        </div>
                      </div>
                      <div className="flex items-center gap-3">
                        {lesson.type && (
                          <Chip size="sm" variant="flat">
                            {t(`course.lessonType.${lesson.type}`)}
                          </Chip>
                        )}
                        <div className="flex items-center gap-1 text-sm text-gray-500">
                          <Clock className="w-4 h-4" />
                          <span>{formatDuration(lesson.duration)}</span>
                        </div>
                      </div>
                    </div>
                  );

                  return isLocked ? (
                    <div key={lesson.id}>{content}</div>
                  ) : (
                    <Link
                      key={lesson.id}
                      to={`/courses/${courseId}/lessons/${lesson.id}`}
                    >
                      {content}
                    </Link>
                  );
                })}
              </div>
            </AccordionItem>
          );
        })}
      </Accordion>

      {!isEnrolled && modules.length > 0 && (
        <div className="mt-4 p-4 bg-blue-50 border border-blue-200 rounded-lg">
          <p className="text-sm text-blue-800">
            <Lock className="w-4 h-4 inline mr-1" />
            {t("course.enrollToAccess")}
          </p>
        </div>
      )}
    </div>
  );
}
