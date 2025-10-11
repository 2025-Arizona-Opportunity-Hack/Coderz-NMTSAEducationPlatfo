import { useState, useEffect } from "react";
import { Input } from "@heroui/input";
import { Button } from "@heroui/button";
import { Search, X } from "lucide-react";
import { useTranslation } from "react-i18next";

interface SearchBarProps {
  onSearch: (query: string) => void;
  placeholder?: string;
  defaultValue?: string;
  debounceMs?: number;
}

export function SearchBar({
  onSearch,
  placeholder,
  defaultValue = "",
  debounceMs = 500,
}: SearchBarProps) {
  const { t } = useTranslation();
  const [query, setQuery] = useState(defaultValue);

  useEffect(() => {
    const timer = setTimeout(() => {
      onSearch(query);
    }, debounceMs);

    return () => clearTimeout(timer);
  }, [query, debounceMs, onSearch]);

  const handleClear = () => {
    setQuery("");
    onSearch("");
  };

  return (
    <div className="relative w-full">
      <Input
        aria-label={t("explore.search") || "Search courses"}
        className="w-full"
        classNames={{
          input: "text-base",
          inputWrapper: "h-12",
        }}
        endContent={
          query ? (
            <Button
              isIconOnly
              aria-label={t("common.clear") || "Clear search"}
              className="min-w-unit-8 w-8 h-8"
              radius="full"
              size="sm"
              variant="light"
              onPress={handleClear}
            >
              <X className="w-4 h-4" />
            </Button>
          ) : null
        }
        placeholder={
          placeholder ||
          t("explore.searchPlaceholder") ||
          "Search for courses..."
        }
        size="lg"
        startContent={<Search className="w-5 h-5 text-gray-400" />}
        type="search"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        onKeyDown={(e) => {
          if (e.key === "Escape") {
            handleClear();
          }
        }}
      />
    </div>
  );
}
