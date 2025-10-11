import type { Course, Enrollment } from "../../types/api";

import { Link } from "react-router-dom";
import { Card, CardBody, CardFooter, CardHeader } from "@heroui/card";
import { Avatar } from "@heroui/avatar";
import { Chip } from "@heroui/chip";
import { Progress } from "@heroui/progress";
import { Clock, Award, Star, Users } from "lucide-react";

interface CourseCardProps {
  course: Course;
  enrollment?: Enrollment;
  viewMode?: "grid" | "list";
}

export function CourseCard({
  course,
  enrollment,
  viewMode = "grid",
}: CourseCardProps) {
  const difficultyColors = {
    beginner: "success",
    intermediate: "warning",
    advanced: "danger",
  } as const;

  const formatDuration = (minutes: number) => {
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;

    return hours > 0 ? `${hours}h ${mins}m` : `${mins}m`;
  };

  if (viewMode === "list") {
    return (
      <Card
        isPressable
        as={Link}
        className="w-full hover:shadow-lg transition-shadow"
        to={`/courses/${course.id}`}
      >
        <CardBody className="flex flex-row gap-4 p-4">
          <div className="flex-shrink-0 w-48 h-32 bg-gray-200 rounded-lg overflow-hidden">
            {course.thumbnailUrl ? (
              <img
                alt={course.title}
                className="w-full h-full object-cover"
                src={course.thumbnailUrl}
              />
            ) : (
              <div className="w-full h-full flex items-center justify-center bg-gradient-to-br from-blue-400 to-purple-500">
                <Award className="w-12 h-12 text-white" />
              </div>
            )}
          </div>

          <div className="flex-1 flex flex-col justify-between">
            <div>
              <div className="flex items-start justify-between gap-4 mb-2">
                <h3 className="text-lg font-semibold text-gray-900 line-clamp-1">
                  {course.title}
                </h3>
                {course.rating && (
                  <div className="flex items-center gap-1 flex-shrink-0">
                    <Star className="w-4 h-4 fill-yellow-400 text-yellow-400" />
                    <span className="text-sm font-medium">{course.rating}</span>
                  </div>
                )}
              </div>

              <p className="text-sm text-gray-600 line-clamp-2 mb-3">
                {course.description}
              </p>

              <div className="flex items-center gap-2 mb-2">
                {course.instructor && (
                  <div className="flex items-center gap-2">
                    <Avatar
                      className="w-6 h-6"
                      name={course.instructor.fullName}
                      size="sm"
                      src={course.instructor.avatarUrl}
                    />
                    <span className="text-sm text-gray-700">
                      {course.instructor.fullName}
                    </span>
                  </div>
                )}
              </div>
            </div>

            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4 text-sm text-gray-600">
                <Chip
                  color={difficultyColors[course.difficulty]}
                  size="sm"
                  variant="flat"
                >
                  {course.difficulty}
                </Chip>
                <div className="flex items-center gap-1">
                  <Clock className="w-4 h-4" />
                  <span>{formatDuration(course.duration)}</span>
                </div>
                <div className="flex items-center gap-1">
                  <Award className="w-4 h-4" />
                  <span>{course.credits} credits</span>
                </div>
                {course.enrollmentCount && (
                  <div className="flex items-center gap-1">
                    <Users className="w-4 h-4" />
                    <span>{course.enrollmentCount}</span>
                  </div>
                )}
              </div>
            </div>

            {enrollment && (
              <div className="mt-3">
                <Progress
                  aria-label="Course progress"
                  className="max-w-md"
                  color="primary"
                  size="sm"
                  value={enrollment.progress}
                />
                <span className="text-xs text-gray-500 mt-1">
                  {enrollment.progress}% complete
                </span>
              </div>
            )}
          </div>
        </CardBody>
      </Card>
    );
  }

  // Grid view
  return (
    <Card
      isPressable
      as={Link}
      className="w-full hover:shadow-lg transition-shadow"
      to={`/courses/${course.id}`}
    >
      <CardHeader className="p-0">
        <div className="relative w-full h-48 bg-gray-200 overflow-hidden">
          {course.thumbnailUrl ? (
            <img
              alt={course.title}
              className="w-full h-full object-cover"
              src={course.thumbnailUrl}
            />
          ) : (
            <div className="w-full h-full flex items-center justify-center bg-gradient-to-br from-blue-400 to-purple-500">
              <Award className="w-16 h-16 text-white" />
            </div>
          )}
          <Chip
            className="absolute top-2 right-2"
            color={difficultyColors[course.difficulty]}
            size="sm"
            variant="solid"
          >
            {course.difficulty}
          </Chip>
          {course.rating && (
            <div className="absolute top-2 left-2 bg-white/90 backdrop-blur-sm px-2 py-1 rounded-full flex items-center gap-1">
              <Star className="w-4 h-4 fill-yellow-400 text-yellow-400" />
              <span className="text-sm font-medium">{course.rating}</span>
            </div>
          )}
        </div>
      </CardHeader>

      <CardBody className="px-4 py-3">
        <h3 className="text-lg font-semibold text-gray-900 mb-2 line-clamp-2">
          {course.title}
        </h3>

        <p className="text-sm text-gray-600 mb-3 line-clamp-2">
          {course.description}
        </p>

        {course.instructor && (
          <div className="flex items-center gap-2 mb-3">
            <Avatar
              className="w-6 h-6"
              name={course.instructor.fullName}
              size="sm"
              src={course.instructor.avatarUrl}
            />
            <span className="text-sm text-gray-700">
              {course.instructor.fullName}
            </span>
          </div>
        )}

        {enrollment && (
          <div className="mb-3">
            <Progress
              aria-label="Course progress"
              color="primary"
              size="sm"
              value={enrollment.progress}
            />
            <span className="text-xs text-gray-500 mt-1">
              {enrollment.progress}% complete
            </span>
          </div>
        )}
      </CardBody>

      <CardFooter className="px-4 py-3 pt-0 flex items-center justify-between border-t">
        <div className="flex items-center gap-3 text-sm text-gray-600">
          <div className="flex items-center gap-1">
            <Clock className="w-4 h-4" />
            <span>{formatDuration(course.duration)}</span>
          </div>
          <div className="flex items-center gap-1">
            <Award className="w-4 h-4" />
            <span>{course.credits}</span>
          </div>
        </div>
        {course.enrollmentCount && (
          <div className="flex items-center gap-1 text-sm text-gray-600">
            <Users className="w-4 h-4" />
            <span>{course.enrollmentCount}</span>
          </div>
        )}
      </CardFooter>
    </Card>
  );
}
