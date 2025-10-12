import type { CourseDetail } from "../../types/api";

import { useState } from "react";
import { Button } from "@heroui/button";
import { Chip } from "@heroui/chip";
import { Progress } from "@heroui/progress";
import { useTranslation } from "react-i18next";
import {
  Clock,
  Award,
  Star,
  Users,
  BookOpen,
  CheckCircle,
  DollarSign,
} from "lucide-react";

import { PaymentButton } from "../payment/PaymentButton";

interface CourseHeroProps {
  course: CourseDetail;
  onEnroll?: () => void;
  onContinue?: () => void;
  onPaymentSuccess?: () => void;
  isEnrolling?: boolean;
}

export function CourseHero({
  course,
  onEnroll,
  onContinue,
  onPaymentSuccess,
  isEnrolling,
}: CourseHeroProps) {
  const { t } = useTranslation();
  const [paymentError, setPaymentError] = useState<string | null>(null);
  const [showPayment, setShowPayment] = useState(false);

  const difficultyColors = {
    beginner: "success",
    intermediate: "warning",
    advanced: "danger",
  } as const;

  const formatDuration = (minutes: number) => {
    const hours = Math.floor(minutes / 60);

    return hours > 0 ? `${hours} ${t("common.hours")}` : `${minutes} min`;
  };

  return (
    <div className="relative bg-gradient-to-br from-blue-600 to-purple-700 text-white">
      <div className="absolute inset-0 bg-black/20" />
      <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Main Content */}
          <div className="lg:col-span-2">
            {/* Breadcrumb */}
            <div className="flex items-center gap-2 text-sm mb-4 opacity-90">
              <span>{course.category}</span>
              <span>/</span>
              <Chip
                color={difficultyColors[course.difficulty]}
                size="sm"
                variant="flat"
              >
                {t(`common.${course.difficulty}`)}
              </Chip>
            </div>

            {/* Title */}
            <h1 className="text-4xl font-bold mb-4">{course.title}</h1>

            {/* Description */}
            <p className="text-lg opacity-90 mb-6">{course.description}</p>

            {/* Stats */}
            <div className="flex flex-wrap items-center gap-4 mb-6">
              {course.averageRating && (
                <div className="flex items-center gap-2">
                  <Star className="w-5 h-5 fill-yellow-400 text-yellow-400" />
                  <span className="font-semibold">
                    {course.averageRating.toFixed(1)}
                  </span>
                  {course.totalReviews && (
                    <span className="opacity-75">
                      ({course.totalReviews} {t("course.reviews")})
                    </span>
                  )}
                </div>
              )}
              {course.enrollmentCount && (
                <div className="flex items-center gap-2">
                  <Users className="w-5 h-5" />
                  <span>
                    {course.enrollmentCount.toLocaleString()}{" "}
                    {t("course.students")}
                  </span>
                </div>
              )}
              <div className="flex items-center gap-2">
                <Clock className="w-5 h-5" />
                <span>{formatDuration(course.duration)}</span>
              </div>
              <div className="flex items-center gap-2">
                <Award className="w-5 h-5" />
                <span>
                  {course.credits} {t("course.credits")}
                </span>
              </div>
              {course.modules && (
                <div className="flex items-center gap-2">
                  <BookOpen className="w-5 h-5" />
                  <span>
                    {course.modules.length} {t("course.modules")}
                  </span>
                </div>
              )}
            </div>

            {/* Instructor */}
            <div className="flex items-center gap-3">
              <img
                alt={course.instructor.fullName}
                className="w-12 h-12 rounded-full border-2 border-white/50"
                src={
                  course.instructor.avatarUrl ||
                  `https://ui-avatars.com/api/?name=${encodeURIComponent(course.instructor.fullName)}`
                }
              />
              <div>
                <p className="text-sm opacity-75">{t("course.instructor")}</p>
                <p className="font-semibold">{course.instructor.fullName}</p>
              </div>
            </div>
          </div>

          {/* Enrollment Card */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-lg p-6 shadow-xl text-gray-900">
              {course.thumbnailUrl && (
                <img
                  alt={course.title}
                  className="w-full h-48 object-cover rounded-lg mb-4"
                  src={course.thumbnailUrl}
                />
              )}

              {course.isEnrolled ? (
                <>
                  <div className="mb-4">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm font-medium">
                        {t("course.yourProgress")}
                      </span>
                      <span className="text-sm font-semibold">
                        {course.progress || 0}%
                      </span>
                    </div>
                    <Progress
                      aria-label="Course progress"
                      color="primary"
                      size="md"
                      value={course.progress || 0}
                    />
                  </div>
                  <Button
                    className="w-full"
                    color="primary"
                    size="lg"
                    startContent={<CheckCircle className="w-5 h-5" />}
                    onPress={onContinue}
                  >
                    {t("course.continueLearning")}
                  </Button>
                </>
              ) : (
                <>
                  <div className="mb-4">
                    {course.isPaid && course.price ? (
                      <>
                        <div className="flex items-baseline gap-2 mb-1">
                          <div className="text-3xl font-bold text-primary">
                            ${course.price}
                          </div>
                          <DollarSign className="w-5 h-5 text-primary" />
                        </div>
                        <p className="text-sm text-gray-600">
                          {t("course.oneTimePayment")}
                        </p>
                      </>
                    ) : (
                      <>
                        <div className="text-3xl font-bold text-primary mb-1">
                          {t("course.free")}
                        </div>
                        <p className="text-sm text-gray-600">
                          {t("course.fullAccess")}
                        </p>
                      </>
                    )}
                  </div>

                  {course.isPaid && course.price ? (
                    showPayment ? (
                      <div className="space-y-4">
                        {paymentError && (
                          <div className="p-3 bg-red-50 border border-red-200 rounded-lg text-red-600 text-sm">
                            {paymentError}
                          </div>
                        )}
                        <PaymentButton
                          amount={course.price}
                          courseId={course.id}
                          onError={(error) => setPaymentError(error)}
                          onSuccess={() => {
                            setPaymentError(null);
                            onPaymentSuccess?.();
                          }}
                        />
                        <Button
                          className="w-full"
                          color="default"
                          size="sm"
                          variant="flat"
                          onPress={() => setShowPayment(false)}
                        >
                          {t("common.cancel")}
                        </Button>
                      </div>
                    ) : (
                      <Button
                        className="w-full"
                        color="primary"
                        size="lg"
                        startContent={<DollarSign className="w-5 h-5" />}
                        onPress={() => setShowPayment(true)}
                      >
                        {t("course.buyNow")}
                      </Button>
                    )
                  ) : (
                    <>
                      <Button
                        className="w-full"
                        color="primary"
                        isLoading={isEnrolling}
                        size="lg"
                        onPress={onEnroll}
                      >
                        {t("course.enrollNow")}
                      </Button>
                      <p className="text-xs text-center text-gray-500 mt-3">
                        {t("course.enrollmentNote")}
                      </p>
                    </>
                  )}
                </>
              )}

              {/* Course Includes */}
              <div className="mt-6 pt-6 border-t border-gray-200">
                <h3 className="font-semibold mb-3">{t("course.includes")}:</h3>
                <ul className="space-y-2 text-sm text-gray-700">
                  <li className="flex items-center gap-2">
                    <CheckCircle className="w-4 h-4 text-green-500" />
                    {t("course.lifetimeAccess")}
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckCircle className="w-4 h-4 text-green-500" />
                    {t("course.certificate")}
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckCircle className="w-4 h-4 text-green-500" />
                    {t("course.mobileAccess")}
                  </li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
