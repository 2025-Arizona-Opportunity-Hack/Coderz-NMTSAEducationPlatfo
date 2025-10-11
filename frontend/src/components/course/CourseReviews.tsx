import type { Review } from "../../types/api";

import { Avatar } from "@heroui/avatar";
import { Chip } from "@heroui/chip";
import { Pagination } from "@heroui/pagination";
import { useTranslation } from "react-i18next";
import { Star } from "lucide-react";

interface CourseReviewsProps {
  reviews: Review[];
  averageRating?: number;
  totalReviews?: number;
  currentPage: number;
  totalPages: number;
  onPageChange: (page: number) => void;
}

export function CourseReviews({
  reviews,
  averageRating,
  totalReviews,
  currentPage,
  totalPages,
  onPageChange,
}: CourseReviewsProps) {
  const { t } = useTranslation();

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);

    return date.toLocaleDateString(undefined, {
      year: "numeric",
      month: "long",
      day: "numeric",
    });
  };

  return (
    <div className="w-full">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold">{t("course.studentReviews")}</h2>
        {averageRating && totalReviews && (
          <div className="flex items-center gap-2">
            <Star className="w-6 h-6 fill-yellow-400 text-yellow-400" />
            <span className="text-2xl font-bold">
              {averageRating.toFixed(1)}
            </span>
            <span className="text-gray-600">
              ({totalReviews} {t("course.reviews")})
            </span>
          </div>
        )}
      </div>

      {reviews.length === 0 ? (
        <div className="text-center py-8 text-gray-500">
          {t("course.noReviews")}
        </div>
      ) : (
        <>
          <div className="space-y-6">
            {reviews.map((review) => (
              <div
                key={review.id}
                className="border-b border-gray-200 pb-6 last:border-0"
              >
                <div className="flex items-start gap-4">
                  <Avatar
                    name={review.user.fullName}
                    size="md"
                    src={review.user.avatarUrl}
                  />
                  <div className="flex-1">
                    <div className="flex items-center justify-between mb-2">
                      <div>
                        <h4 className="font-semibold text-gray-900">
                          {review.user.fullName}
                        </h4>
                        <p className="text-sm text-gray-500">
                          {formatDate(review.createdAt)}
                        </p>
                      </div>
                      <Chip
                        startContent={
                          <Star className="w-3 h-3 fill-yellow-400" />
                        }
                        variant="flat"
                      >
                        {review.rating.toFixed(1)}
                      </Chip>
                    </div>
                    <p className="text-gray-700 leading-relaxed">
                      {review.comment}
                    </p>
                  </div>
                </div>
              </div>
            ))}
          </div>

          {totalPages > 1 && (
            <div className="flex justify-center mt-8">
              <Pagination
                isCompact
                showControls
                color="primary"
                page={currentPage}
                total={totalPages}
                onChange={onPageChange}
              />
            </div>
          )}
        </>
      )}
    </div>
  );
}
