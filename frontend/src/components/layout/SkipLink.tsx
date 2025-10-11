import { useTranslation } from "react-i18next";

export function SkipLink() {
  const { t } = useTranslation();

  return (
    <a
      className="sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-4 focus:z-50 focus:px-4 focus:py-2 focus:bg-blue-600 focus:text-white focus:rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
      href="#main-content"
    >
      {t("nav.skipToContent")}
    </a>
  );
}
