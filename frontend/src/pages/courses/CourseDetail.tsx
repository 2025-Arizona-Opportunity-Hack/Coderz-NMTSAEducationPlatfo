import type { CourseDetail as CourseDetailType, Review } from "../../types/api";

import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { Helmet } from "react-helmet-async";
import { useTranslation } from "react-i18next";
import { Spinner } from "@heroui/spinner";
import { Card, CardBody } from "@heroui/card";
import { Tabs, Tab } from "@heroui/tabs";

import { CourseHero } from "../../components/course/CourseHero";
import { InstructorCard } from "../../components/course/InstructorCard";
import { CourseModules } from "../../components/course/CourseModules";
import { CourseReviews } from "../../components/course/CourseReviews";
import { courseService } from "../../services/course.service";
import { useAuthStore } from "../../store/useAuthStore";

export function CourseDetail() {
  const { id } = useParams<{ id: string }>();
  const { t } = useTranslation();
  const navigate = useNavigate();
  const { isAuthenticated } = useAuthStore();

  const [course, setCourse] = useState<CourseDetailType | null>(null);
  const [reviews, setReviews] = useState<Review[]>([]);
  const [reviewsPage, setReviewsPage] = useState(1);
  const [reviewsTotalPages, setReviewsTotalPages] = useState(1);
  const [isLoading, setIsLoading] = useState(true);
  const [isEnrolling, setIsEnrolling] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!id) return;

    const fetchCourse = async () => {
      try {
        setIsLoading(true);
        const data = await courseService.getCourseDetail(id);

        setCourse(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load course");
      } finally {
        setIsLoading(false);
      }
    };

    fetchCourse();
  }, [id]);

  useEffect(() => {
    if (!id) return;

    const fetchReviews = async () => {
      try {
        const data = await courseService.getCourseReviews(id, reviewsPage);

        setReviews(data.data);
        setReviewsTotalPages(data.pagination.totalPages);
      } catch (err) {
        console.error("Failed to load reviews:", err);
      }
    };

    fetchReviews();
  }, [id, reviewsPage]);

  const handleEnroll = async () => {
    if (!isAuthenticated) {
      navigate("/login", { state: { from: `/courses/${id}` } });

      return;
    }

    if (!id) return;

    try {
      setIsEnrolling(true);
      await courseService.enrollInCourse(id);

      // Refresh course data
      const updatedCourse = await courseService.getCourseDetail(id);

      setCourse(updatedCourse);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to enroll");
    } finally {
      setIsEnrolling(false);
    }
  };

  const handlePaymentSuccess = async () => {
    // Refresh course data after successful payment
    if (!id) return;

    try {
      const updatedCourse = await courseService.getCourseDetail(id);

      setCourse(updatedCourse);
    } catch (err) {
      console.error("Failed to refresh course data:", err);
    }
  };

  const handleContinue = () => {
    if (course?.modules && course.modules.length > 0) {
      const firstLesson = course.modules[0].lessons[0];

      if (firstLesson) {
        navigate(`/courses/${id}/lessons/${firstLesson.id}`);
      }
    }
  };

  if (isLoading) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <Spinner label={t("common.loading")} size="lg" />
      </div>
    );
  }

  if (error || !course) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <Card>
          <CardBody>
            <div className="text-center py-12">
              <p className="text-red-600 text-lg">
                {error || t("course.notFound")}
              </p>
            </div>
          </CardBody>
        </Card>
      </div>
    );
  }

  // Generate Schema.org JSON-LD
  const courseSchema = {
    "@context": "https://schema.org",
    "@type": "Course",
    name: course.title,
    description: course.description,
    provider: {
      "@type": "Organization",
      name: "NMTSA Learn",
      sameAs: window.location.origin,
    },
    instructor: {
      "@type": "Person",
      name: course.instructor.fullName,
      ...(course.instructor.bio && { description: course.instructor.bio }),
    },
    ...(course.averageRating && {
      aggregateRating: {
        "@type": "AggregateRating",
        ratingValue: course.averageRating,
        reviewCount: course.totalReviews || 0,
        bestRating: 5,
        worstRating: 1,
      },
    }),
    ...(course.thumbnailUrl && { image: course.thumbnailUrl }),
    offers: {
      "@type": "Offer",
      price: "0",
      priceCurrency: "USD",
      availability: "https://schema.org/InStock",
    },
  };

  return (
    <>
      <Helmet>
        <title>{`${course.title} - NMTSA Learn`}</title>
        <meta content={course.description} name="description" />
        <meta
          content={`${course.category}, ${course.difficulty}, online course, music therapy`}
          name="keywords"
        />
        {/* Open Graph */}
        <meta content={course.title} property="og:title" />
        <meta content={course.description} property="og:description" />
        {course.thumbnailUrl && (
          <meta content={course.thumbnailUrl} property="og:image" />
        )}
        {/* Schema.org */}
        <script type="application/ld+json">
          {JSON.stringify(courseSchema)}
        </script>
      </Helmet>

      <div className="min-h-screen bg-gray-50">
        <CourseHero
          course={course}
          isEnrolling={isEnrolling}
          onContinue={handleContinue}
          onEnroll={handleEnroll}
          onPaymentSuccess={handlePaymentSuccess}
        />

        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            <div className="lg:col-span-2">
              <Tabs
                aria-label="Course content tabs"
                classNames={{
                  tabList: "w-full",
                  tab: "h-12",
                }}
              >
                <Tab key="overview" title={t("course.overview")}>
                  <Card>
                    <CardBody className="p-6">
                      <h2 className="text-2xl font-bold mb-4">
                        {t("course.aboutCourse")}
                      </h2>
                      <div className="prose max-w-none">
                        <p className="text-gray-700 leading-relaxed mb-6">
                          {course.longDescription || course.description}
                        </p>

                        {course.learningObjectives &&
                          course.learningObjectives.length > 0 && (
                            <div className="mb-6">
                              <h3 className="text-lg font-semibold mb-3">
                                {t("course.whatYouWillLearn")}
                              </h3>
                              <ul className="space-y-2">
                                {course.learningObjectives.map((obj, idx) => (
                                  <li
                                    key={idx}
                                    className="flex items-start gap-2"
                                  >
                                    <span className="text-green-500 mt-1">
                                      ✓
                                    </span>
                                    <span>{obj}</span>
                                  </li>
                                ))}
                              </ul>
                            </div>
                          )}

                        {course.prerequisites &&
                          course.prerequisites.length > 0 && (
                            <div>
                              <h3 className="text-lg font-semibold mb-3">
                                {t("course.prerequisites")}
                              </h3>
                              <ul className="list-disc list-inside space-y-1 text-gray-700">
                                {course.prerequisites.map((prereq, idx) => (
                                  <li key={idx}>{prereq}</li>
                                ))}
                              </ul>
                            </div>
                          )}
                      </div>
                    </CardBody>
                  </Card>
                </Tab>

                <Tab key="curriculum" title={t("course.curriculum")}>
                  <Card>
                    <CardBody className="p-6">
                      {course.modules && course.modules.length > 0 ? (
                        <CourseModules
                          courseId={course.id}
                          isEnrolled={course.isEnrolled}
                          modules={course.modules}
                        />
                      ) : (
                        <p className="text-gray-500 text-center py-8">
                          {t("course.noCurriculum")}
                        </p>
                      )}
                    </CardBody>
                  </Card>
                </Tab>

                <Tab key="reviews" title={t("course.reviews")}>
                  <Card>
                    <CardBody className="p-6">
                      <CourseReviews
                        averageRating={course.averageRating}
                        currentPage={reviewsPage}
                        reviews={reviews}
                        totalPages={reviewsTotalPages}
                        totalReviews={course.totalReviews}
                        onPageChange={setReviewsPage}
                      />
                    </CardBody>
                  </Card>
                </Tab>
              </Tabs>
            </div>

            <div className="lg:col-span-1">
              <InstructorCard instructor={course.instructor} />
            </div>
          </div>
        </div>
      </div>
    </>
  );
}
