import { Helmet } from "react-helmet-async";
import { Link } from "react-router-dom";
import { Home, Search, ArrowLeft } from "lucide-react";
import { Button } from "@heroui/button";

export function NotFound() {
  return (
    <>
      <Helmet>
        <title>404 - Page Not Found | NMTSA Learn</title>
        <meta
          content="The page you're looking for doesn't exist"
          name="description"
        />
      </Helmet>

      <div className="min-h-[70vh] flex items-center justify-center px-4">
        <div className="text-center max-w-2xl">
          {/* 404 Illustration */}
          <div className="mb-8">
            <h1 className="text-[150px] md:text-[200px] font-bold text-blue-100 leading-none">
              404
            </h1>
          </div>

          {/* Error Message */}
          <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
            Page Not Found
          </h2>
          <p className="text-lg text-gray-600 mb-8">
            Oops! The page you&apos;re looking for doesn&apos;t exist. It might
            have been moved or deleted.
          </p>

          {/* Action Buttons */}
          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
            <Button
              as={Link}
              color="primary"
              size="lg"
              startContent={<ArrowLeft className="w-5 h-5" />}
              to="/"
              variant="solid"
            >
              Go Home
            </Button>

            <Button
              as={Link}
              color="default"
              size="lg"
              startContent={<Search className="w-5 h-5" />}
              to="/explore"
              variant="bordered"
            >
              Explore Courses
            </Button>
          </div>

          {/* Helpful Links */}
          <div className="mt-12 pt-8 border-t border-gray-200">
            <p className="text-sm text-gray-500 mb-4">
              Here are some helpful links instead:
            </p>
            <div className="flex flex-wrap gap-4 justify-center text-sm">
              <Link
                className="text-blue-600 hover:text-blue-700 hover:underline"
                to="/"
              >
                <Home className="w-4 h-4 inline-block mr-1" />
                Home
              </Link>
              <Link
                className="text-blue-600 hover:text-blue-700 hover:underline"
                to="/explore"
              >
                Browse Courses
              </Link>
              <Link
                className="text-blue-600 hover:text-blue-700 hover:underline"
                to="/dashboard"
              >
                Dashboard
              </Link>
              <Link
                className="text-blue-600 hover:text-blue-700 hover:underline"
                to="/forum"
              >
                Community Forum
              </Link>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}
