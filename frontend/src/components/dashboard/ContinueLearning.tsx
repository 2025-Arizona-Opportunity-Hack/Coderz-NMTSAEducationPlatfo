import type { ContinueLearningItem } from "../../types/api";

import { Card, CardBody, CardHeader } from "@heroui/card";
import { Button } from "@heroui/button";
import { Progress } from "@heroui/progress";
import { Chip } from "@heroui/chip";
import { useTranslation } from "react-i18next";
import { useNavigate } from "react-router-dom";
import { PlayCircle, Clock } from "lucide-react";

interface ContinueLearningProps {
  items: ContinueLearningItem[];
}

export function ContinueLearning({ items }: ContinueLearningProps) {
  const { t } = useTranslation();
  const navigate = useNavigate();

  if (items.length === 0) {
    return (
      <Card>
        <CardBody className="py-12">
          <p className="text-center text-gray-500">
            {t("dashboard.noContinueLearning")}
          </p>
        </CardBody>
      </Card>
    );
  }

  const formatDuration = (minutes: number) => {
    if (minutes < 60) return `${minutes}m`;

    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;

    return `${hours}h ${mins}m`;
  };

  return (
    <div className="space-y-4">
      <h2 className="text-2xl font-bold text-gray-900">
        {t("dashboard.continueLearning")}
      </h2>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {items.map((item) => (
          <Card
            key={item.enrollment.id}
            isPressable
            className="hover:shadow-lg transition-shadow"
            onPress={() =>
              navigate(
                `/courses/${item.enrollment.courseId}/lessons/${item.nextLesson.id}`,
              )
            }
          >
            <CardHeader className="pb-0">
              {item.enrollment.course.thumbnailUrl && (
                <img
                  alt={item.enrollment.course.title}
                  className="w-full h-40 object-cover rounded-t-lg"
                  src={item.enrollment.course.thumbnailUrl}
                />
              )}
            </CardHeader>
            <CardBody className="space-y-3">
              <div>
                <h3 className="font-semibold text-lg line-clamp-2">
                  {item.enrollment.course.title}
                </h3>
                <p className="text-sm text-gray-600 mt-1">
                  {t("dashboard.nextUp")}: {item.nextLesson.title}
                </p>
              </div>

              <div className="flex items-center gap-2">
                <Chip color="primary" size="sm" variant="flat">
                  {t(`course.lessonType.${item.nextLesson.type}`)}
                </Chip>
                <div className="flex items-center gap-1 text-sm text-gray-600">
                  <Clock className="w-4 h-4" />
                  <span>{formatDuration(item.nextLesson.duration)}</span>
                </div>
              </div>

              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm text-gray-600">
                    {t("dashboard.progress")}
                  </span>
                  <span className="text-sm font-semibold">
                    {item.enrollment.progress}%
                  </span>
                </div>
                <Progress
                  aria-label="Course progress"
                  color="primary"
                  size="sm"
                  value={item.enrollment.progress}
                />
              </div>

              <Button
                className="w-full"
                color="primary"
                startContent={<PlayCircle className="w-5 h-5" />}
              >
                {t("dashboard.continue")}
              </Button>
            </CardBody>
          </Card>
        ))}
      </div>
    </div>
  );
}
