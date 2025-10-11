import { Button } from "@heroui/button";
import { Select, SelectItem } from "@heroui/select";
import { Slider } from "@heroui/slider";
import { useTranslation } from "react-i18next";
import { X, SlidersHorizontal } from "lucide-react";

interface FilterPanelProps {
  categories: string[];
  filters: {
    category: string;
    difficulty: "" | "beginner" | "intermediate" | "advanced";
    minCredits: number;
    maxCredits: number;
    minDuration: number;
    maxDuration: number;
    minRating: number;
  };
  onFilterChange: (key: string, value: string | number) => void;
  onClearFilters: () => void;
}

export function FilterPanel({
  categories,
  filters,
  onFilterChange,
  onClearFilters,
}: FilterPanelProps) {
  const { t } = useTranslation();

  const hasActiveFilters =
    filters.category ||
    filters.difficulty ||
    filters.minCredits > 0 ||
    filters.maxCredits < 100 ||
    filters.minDuration > 0 ||
    filters.maxDuration < 1000 ||
    filters.minRating > 0;

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <SlidersHorizontal className="w-5 h-5 text-gray-700" />
          <h2 className="text-lg font-semibold text-gray-900">
            {t("explore.filters") || "Filters"}
          </h2>
        </div>
        {hasActiveFilters && (
          <Button
            className="text-sm"
            color="danger"
            size="sm"
            startContent={<X className="w-4 h-4" />}
            variant="flat"
            onPress={onClearFilters}
          >
            {t("common.clearAll") || "Clear All"}
          </Button>
        )}
      </div>

      {/* Category Filter */}
      <div>
        <label
          className="block text-sm font-medium text-gray-700 mb-2"
          htmlFor="category-filter"
        >
          {t("explore.category") || "Category"}
        </label>
        <Select
          aria-label={t("explore.selectCategory") || "Select category"}
          id="category-filter"
          placeholder={t("explore.allCategories") || "All Categories"}
          selectedKeys={filters.category ? [filters.category] : []}
          onSelectionChange={(keys) => {
            const value = Array.from(keys)[0] as string;

            onFilterChange("category", value || "");
          }}
        >
          {categories.map((category) => (
            <SelectItem key={category}>{category}</SelectItem>
          ))}
        </Select>
      </div>

      {/* Difficulty Filter */}
      <div>
        <label
          className="block text-sm font-medium text-gray-700 mb-2"
          htmlFor="difficulty-filter"
        >
          {t("explore.difficulty") || "Difficulty"}
        </label>
        <Select
          aria-label={t("explore.selectDifficulty") || "Select difficulty"}
          id="difficulty-filter"
          placeholder={t("explore.allLevels") || "All Levels"}
          selectedKeys={filters.difficulty ? [filters.difficulty] : []}
          onSelectionChange={(keys) => {
            const value = Array.from(keys)[0] as string;

            onFilterChange("difficulty", value || "");
          }}
        >
          <SelectItem key="beginner">
            {t("common.beginner") || "Beginner"}
          </SelectItem>
          <SelectItem key="intermediate">
            {t("common.intermediate") || "Intermediate"}
          </SelectItem>
          <SelectItem key="advanced">
            {t("common.advanced") || "Advanced"}
          </SelectItem>
        </Select>
      </div>

      {/* Credits Range */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          {t("explore.credits") || "Credits"}
        </label>
        <Slider
          aria-label={t("explore.creditsRange") || "Credits range"}
          className="max-w-md"
          formatOptions={{ style: "decimal" }}
          maxValue={100}
          minValue={0}
          step={5}
          value={[filters.minCredits, filters.maxCredits]}
          onChange={(value) => {
            const [min, max] = value as number[];

            onFilterChange("minCredits", min);
            onFilterChange("maxCredits", max);
          }}
        />
        <div className="flex justify-between text-xs text-gray-500 mt-1">
          <span>{filters.minCredits}</span>
          <span>{filters.maxCredits}</span>
        </div>
      </div>

      {/* Duration Range */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          {t("explore.duration") || "Duration (hours)"}
        </label>
        <Slider
          aria-label={t("explore.durationRange") || "Duration range"}
          className="max-w-md"
          formatOptions={{ style: "decimal" }}
          maxValue={100}
          minValue={0}
          step={5}
          value={[
            Math.floor(filters.minDuration / 60),
            Math.floor(filters.maxDuration / 60),
          ]}
          onChange={(value) => {
            const [min, max] = value as number[];

            onFilterChange("minDuration", min * 60);
            onFilterChange("maxDuration", max * 60);
          }}
        />
        <div className="flex justify-between text-xs text-gray-500 mt-1">
          <span>{Math.floor(filters.minDuration / 60)}h</span>
          <span>{Math.floor(filters.maxDuration / 60)}h</span>
        </div>
      </div>

      {/* Rating Filter */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          {t("explore.minimumRating") || "Minimum Rating"}
        </label>
        <Slider
          aria-label={t("explore.minimumRating") || "Minimum rating"}
          className="max-w-md"
          formatOptions={{ style: "decimal" }}
          marks={[
            { value: 0, label: "All" },
            { value: 3, label: "3+" },
            { value: 4, label: "4+" },
            { value: 5, label: "5" },
          ]}
          maxValue={5}
          minValue={0}
          step={0.5}
          value={filters.minRating}
          onChange={(value) => {
            onFilterChange("minRating", value as number);
          }}
        />
      </div>
    </div>
  );
}
