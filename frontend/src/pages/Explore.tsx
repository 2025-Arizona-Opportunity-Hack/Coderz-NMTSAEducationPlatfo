import { useEffect, useState } from "react";
import { Button } from "@heroui/button";
import { Select, SelectItem } from "@heroui/select";
import { Pagination } from "@heroui/pagination";
import { Spinner } from "@heroui/spinner";
import { useTranslation } from "react-i18next";
import { Grid, List, SlidersHorizontal } from "lucide-react";
import { Helmet } from "react-helmet-async";

import { CourseCard } from "../components/course/CourseCard";
import { SearchBar } from "../components/course/SearchBar";
import { FilterPanel } from "../components/course/FilterPanel";
import { useCourseStore } from "../store/useCourseStore";
import { courseService } from "../services/course.service";

export function Explore() {
  const { t } = useTranslation();
  const [showFilters, setShowFilters] = useState(true);

  const {
    courses,
    categories,
    filters,
    sortBy,
    viewMode,
    pagination,
    isLoading,
    error,
    setCourses,
    setCategories,
    setFilter,
    clearFilters,
    setSortBy,
    setViewMode,
    setPage,
    setLoading,
    setError,
    getFilterParams,
  } = useCourseStore();

  // Fetch categories on mount
  useEffect(() => {
    const fetchCategories = async () => {
      try {
        const cats = await courseService.getCategories();

        setCategories(cats);
      } catch (err) {
        console.error("Failed to fetch categories:", err);
      }
    };

    fetchCategories();
  }, [setCategories]);

  // Fetch courses when filters or pagination change
  useEffect(() => {
    const fetchCourses = async () => {
      try {
        setLoading(true);
        const params = getFilterParams();
        const data = await courseService.getCourses(params);

        setCourses(data);
      } catch (err) {
        setError(
          err instanceof Error ? err.message : "Failed to fetch courses",
        );
      }
    };

    fetchCourses();
  }, [
    filters,
    sortBy,
    pagination.page,
    setCourses,
    setLoading,
    setError,
    getFilterParams,
  ]);

  const handleSearch = (query: string) => {
    setFilter("search", query);
  };

  const handleSortChange = (keys: any) => {
    const value = Array.from(keys)[0] as string;

    switch (value) {
      case "popularity":
        setSortBy("popularity", "desc");
        break;
      case "newest":
        setSortBy("newest", "desc");
        break;
      case "rating":
        setSortBy("rating", "desc");
        break;
      case "title":
        setSortBy("title", "asc");
        break;
    }
  };

  return (
    <>
      <Helmet>
        <title>
          {t("explore.pageTitle") || "Explore Courses - NMTSA Learn"}
        </title>
        <meta
          content={
            t("explore.pageDescription") ||
            "Discover and enroll in neurologic music therapy courses. Browse by category, difficulty, and rating."
          }
          name="description"
        />
        <meta
          content="courses, music therapy, learning, education"
          name="keywords"
        />
      </Helmet>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            {t("explore.title") || "Explore Courses"}
          </h1>
          <p className="text-gray-600">
            {t("explore.subtitle") ||
              "Discover courses that match your interests and goals"}
          </p>
        </div>

        {/* Search Bar */}
        <div className="mb-6">
          <SearchBar defaultValue={filters.search} onSearch={handleSearch} />
        </div>

        {/* Filters Toggle & Sort */}
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-6">
          <Button
            className="text-sm"
            startContent={<SlidersHorizontal className="w-4 h-4" />}
            variant="flat"
            onPress={() => setShowFilters(!showFilters)}
          >
            {showFilters
              ? t("explore.hideFilters") || "Hide Filters"
              : t("explore.showFilters") || "Show Filters"}
          </Button>

          <div className="flex items-center gap-4">
            {/* View Mode Toggle */}
            <div className="flex gap-2">
              <Button
                isIconOnly
                aria-label="Grid view"
                color={viewMode === "grid" ? "primary" : "default"}
                size="sm"
                variant={viewMode === "grid" ? "solid" : "flat"}
                onPress={() => setViewMode("grid")}
              >
                <Grid className="w-4 h-4" />
              </Button>
              <Button
                isIconOnly
                aria-label="List view"
                color={viewMode === "list" ? "primary" : "default"}
                size="sm"
                variant={viewMode === "list" ? "solid" : "flat"}
                onPress={() => setViewMode("list")}
              >
                <List className="w-4 h-4" />
              </Button>
            </div>

            {/* Sort Dropdown */}
            <Select
              aria-label={t("explore.sortBy") || "Sort by"}
              className="w-48"
              placeholder={t("explore.sortBy") || "Sort by"}
              selectedKeys={[sortBy]}
              size="sm"
              onSelectionChange={handleSortChange}
            >
              <SelectItem key="popularity">
                {t("explore.popularity") || "Popularity"}
              </SelectItem>
              <SelectItem key="newest">
                {t("explore.newest") || "Newest"}
              </SelectItem>
              <SelectItem key="rating">
                {t("explore.rating") || "Rating"}
              </SelectItem>
              <SelectItem key="title">
                {t("explore.title_sort") || "Title (A-Z)"}
              </SelectItem>
            </Select>
          </div>
        </div>

        {/* Main Content */}
        <div className="flex flex-col lg:flex-row gap-8">
          {/* Filters Sidebar */}
          {showFilters && (
            <aside className="w-full lg:w-80 flex-shrink-0">
              <FilterPanel
                categories={categories}
                filters={filters}
                onClearFilters={clearFilters}
                onFilterChange={(key, value) => setFilter(key as any, value)}
              />
            </aside>
          )}

          {/* Course Grid/List */}
          <div className="flex-1">
            {error && (
              <div
                className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-6"
                role="alert"
              >
                <p>{error}</p>
              </div>
            )}

            {isLoading ? (
              <div className="flex justify-center items-center min-h-[400px]">
                <Spinner
                  label={t("common.loading") || "Loading..."}
                  size="lg"
                />
              </div>
            ) : courses.length === 0 ? (
              <div className="text-center py-12">
                <p className="text-gray-500 text-lg">
                  {t("explore.noCourses") || "No courses found"}
                </p>
                <Button
                  className="mt-4"
                  color="primary"
                  variant="flat"
                  onPress={clearFilters}
                >
                  {t("explore.clearFilters") || "Clear Filters"}
                </Button>
              </div>
            ) : (
              <>
                <div
                  className={
                    viewMode === "grid"
                      ? "grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6"
                      : "space-y-4"
                  }
                >
                  {courses.map((course) => (
                    <CourseCard
                      key={course.id}
                      course={course}
                      viewMode={viewMode}
                    />
                  ))}
                </div>

                {/* Pagination */}
                {pagination.totalPages > 1 && (
                  <div className="flex justify-center mt-8">
                    <Pagination
                      isCompact
                      showControls
                      color="primary"
                      page={pagination.page}
                      total={pagination.totalPages}
                      onChange={setPage}
                    />
                  </div>
                )}
              </>
            )}
          </div>
        </div>
      </div>
    </>
  );
}
