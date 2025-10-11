import { useTranslation } from "react-i18next";
import { Link } from "react-router-dom";
import { BookOpen, Users, Award } from "lucide-react";

export function Home() {
  const { t } = useTranslation();

  return (
    <div className="bg-white">
      <section className="bg-gradient-to-r from-blue-600 to-blue-800 text-white py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h1 className="text-4xl md:text-5xl font-bold mb-6">
            {t("common.welcome")}
          </h1>
          <p className="text-xl md:text-2xl mb-8 text-blue-100">
            Your gateway to quality education and professional development
          </p>
          <div className="flex gap-4 justify-center">
            <Link
              className="px-8 py-3 bg-white text-blue-600 font-semibold rounded-lg hover:bg-blue-50 focus:outline-none focus:ring-2 focus:ring-white focus:ring-offset-2 focus:ring-offset-blue-600"
              to="/explore"
            >
              Explore Courses
            </Link>
            <Link
              className="px-8 py-3 bg-blue-700 text-white font-semibold rounded-lg hover:bg-blue-800 focus:outline-none focus:ring-2 focus:ring-white focus:ring-offset-2 focus:ring-offset-blue-600"
              to="/register"
            >
              Get Started
            </Link>
          </div>
        </div>
      </section>

      <section className="py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="text-center p-6">
              <div className="inline-flex items-center justify-center w-16 h-16 bg-blue-100 text-blue-600 rounded-full mb-4">
                <BookOpen aria-hidden="true" className="h-8 w-8" />
              </div>
              <h3 className="text-xl font-bold mb-3">Quality Content</h3>
              <p className="text-gray-600">
                Access curated courses designed by industry experts
              </p>
            </div>

            <div className="text-center p-6">
              <div className="inline-flex items-center justify-center w-16 h-16 bg-blue-100 text-blue-600 rounded-full mb-4">
                <Users aria-hidden="true" className="h-8 w-8" />
              </div>
              <h3 className="text-xl font-bold mb-3">Community</h3>
              <p className="text-gray-600">
                Join a vibrant community of learners and instructors
              </p>
            </div>

            <div className="text-center p-6">
              <div className="inline-flex items-center justify-center w-16 h-16 bg-blue-100 text-blue-600 rounded-full mb-4">
                <Award aria-hidden="true" className="h-8 w-8" />
              </div>
              <h3 className="text-xl font-bold mb-3">Certificates</h3>
              <p className="text-gray-600">
                Earn recognized certificates upon course completion
              </p>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
