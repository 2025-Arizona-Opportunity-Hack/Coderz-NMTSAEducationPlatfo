import { useState } from "react";
import { Card, CardBody, CardHeader } from "@heroui/card";
import { Button } from "@heroui/button";
import { Progress } from "@heroui/progress";
import { Chip } from "@heroui/chip";
import { Input } from "@heroui/input";
import { Select, SelectItem } from "@heroui/select";
import { Pagination } from "@heroui/pagination";
import { useTranslation } from "react-i18next";
import { useNavigate } from "react-router-dom";
import { Search, Clock, Award } from "lucide-react";

import type { EnrollmentWithProgress } from "../../types/api";

interface EnrolledCoursesProps {
  enrollments: EnrollmentWithProgress[];
  totalPages: number;
  currentPage: number;
  onPageChange: (page: number) => void;
  onFilterChange: (filter: "all" | "in-progress" | "completed") => void;
}

export function EnrolledCourses({
  enrollments,
  totalPages,
  currentPage,
  onPageChange,
  onFilterChange,
}: EnrolledCoursesProps) {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const [searchQuery, setSearchQuery] = useState("");
  const [filter, setFilter] = useState<"all" | "in-progress" | "completed">(
    "all",
  );

  const filteredEnrollments = enrollments.filter((enrollment) =>
    enrollment.course.title.toLowerCase().includes(searchQuery.toLowerCase()),
  );

  const handleFilterChange = (value: string) => {
    const newFilter = value as "all" | "in-progress" | "completed";

    setFilter(newFilter);
    onFilterChange(newFilter === "all" ? "all" : newFilter);
  };

  const formatDuration = (minutes: number) => {
    const hours = Math.floor(minutes / 60);

    return hours > 0 ? `${hours}h` : `${minutes}m`;
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row gap-4">
        <Input
          className="flex-1"
          placeholder={t("dashboard.searchCourses")}
          startContent={<Search className="w-4 h-4 text-gray-400" />}
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
        />
        <Select
          className="sm:w-48"
          label={t("dashboard.filterBy")}
          selectedKeys={[filter]}
          onChange={(e) => handleFilterChange(e.target.value)}
        >
          <SelectItem key="all">{t("dashboard.allCourses")}</SelectItem>
          <SelectItem key="in-progress">
            {t("dashboard.inProgress")}
          </SelectItem>
          <SelectItem key="completed">{t("dashboard.completed")}</SelectItem>
        </Select>
      </div>

      {filteredEnrollments.length === 0 ? (
        <Card>
          <CardBody className="py-12">
            <p className="text-center text-gray-500">
              {t("dashboard.noEnrollments")}
            </p>
          </CardBody>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredEnrollments.map((enrollment) => (
            <Card
              key={enrollment.id}
              className="hover:shadow-lg transition-shadow"
              isPressable
              onPress={() =>
                navigate(`/courses/${enrollment.course.id}`)
              }
            >
              <CardHeader className="pb-0">
                {enrollment.course.thumbnailUrl && (
                  <img
                    alt={enrollment.course.title}
                    className="w-full h-40 object-cover rounded-t-lg"
                    src={enrollment.course.thumbnailUrl}
                  />
                )}
              </CardHeader>
              <CardBody className="space-y-3">
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <Chip
                      color={
                        enrollment.progress === 100 ? "success" : "warning"
                      }
                      size="sm"
                      variant="flat"
                    >
                      {enrollment.progress === 100
                        ? t("course.completed")
                        : t("course.inProgress")}
                    </Chip>
                    {enrollment.course.credits && (
                      <div className="flex items-center gap-1 text-sm text-gray-600">
                        <Award className="w-4 h-4" />
                        <span>{enrollment.course.credits}</span>
                      </div>
                    )}
                  </div>
                  <h3 className="font-semibold text-lg line-clamp-2">
                    {enrollment.course.title}
                  </h3>
                  <p className="text-sm text-gray-600 mt-1">
                    {enrollment.course.category}
                  </p>
                </div>

                {enrollment.currentLesson && (
                  <p className="text-sm text-gray-600">
                    {t("dashboard.currentLesson")}:{" "}
                    {enrollment.currentLesson.title}
                  </p>
                )}

                <div className="flex items-center gap-2 text-sm text-gray-600">
                  <Clock className="w-4 h-4" />
                  <span>{formatDuration(enrollment.course.duration)}</span>
                  {enrollment.completedAt && (
                    <span className="text-green-600">
                      • {t("dashboard.completedOn")}{" "}
                      {new Date(enrollment.completedAt).toLocaleDateString()}
                    </span>
                  )}
                </div>

                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm text-gray-600">
                      {t("dashboard.progress")}
                    </span>
                    <span className="text-sm font-semibold">
                      {enrollment.progress}%
                    </span>
                  </div>
                  <Progress
                    aria-label="Course progress"
                    color={enrollment.progress === 100 ? "success" : "primary"}
                    size="sm"
                    value={enrollment.progress}
                  />
                </div>

                <Button
                  className="w-full"
                  color={enrollment.progress === 100 ? "success" : "primary"}
                  variant={enrollment.progress === 100 ? "flat" : "solid"}
                >
                  {enrollment.progress === 100
                    ? t("dashboard.viewCourse")
                    : t("dashboard.continue")}
                </Button>
              </CardBody>
            </Card>
          ))}
        </div>
      )}

      {totalPages > 1 && (
        <div className="flex justify-center mt-8">
          <Pagination
            total={totalPages}
            page={currentPage}
            onChange={onPageChange}
          />
        </div>
      )}
    </div>
  );
}
