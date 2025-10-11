import { useTranslation } from "react-i18next";
import { Link } from "react-router-dom";

export function Footer() {
  const { t } = useTranslation();

  return (
    <footer className="bg-gray-900 text-gray-300 mt-auto" role="contentinfo">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div>
            <h3 className="text-white font-bold text-lg mb-4">NMTSA Learn</h3>
            <p className="text-sm text-gray-400">
              Empowering learners through accessible, high-quality education.
            </p>
          </div>

          <div>
            <h4 className="text-white font-semibold mb-4">Quick Links</h4>
            <nav aria-label="Footer navigation">
              <ul className="space-y-2">
                <li>
                  <Link
                    className="text-sm hover:text-white focus:outline-none focus:ring-2 focus:ring-blue-400 rounded-md px-1"
                    to="/about"
                  >
                    {t("footer.about")}
                  </Link>
                </li>
                <li>
                  <Link
                    className="text-sm hover:text-white focus:outline-none focus:ring-2 focus:ring-blue-400 rounded-md px-1"
                    to="/contact"
                  >
                    {t("footer.contact")}
                  </Link>
                </li>
              </ul>
            </nav>
          </div>

          <div>
            <h4 className="text-white font-semibold mb-4">Legal</h4>
            <nav aria-label="Legal links">
              <ul className="space-y-2">
                <li>
                  <Link
                    className="text-sm hover:text-white focus:outline-none focus:ring-2 focus:ring-blue-400 rounded-md px-1"
                    to="/privacy"
                  >
                    {t("footer.privacy")}
                  </Link>
                </li>
                <li>
                  <Link
                    className="text-sm hover:text-white focus:outline-none focus:ring-2 focus:ring-blue-400 rounded-md px-1"
                    to="/terms"
                  >
                    {t("footer.terms")}
                  </Link>
                </li>
              </ul>
            </nav>
          </div>
        </div>

        <div className="border-t border-gray-800 mt-8 pt-8 text-center">
          <p className="text-sm text-gray-400">{t("footer.copyright")}</p>
        </div>
      </div>
    </footer>
  );
}
