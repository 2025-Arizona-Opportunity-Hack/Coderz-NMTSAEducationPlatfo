import { Helmet } from "react-helmet-async";
import { AlertTriangle, RefreshCw, Home } from "lucide-react";
import { Button } from "@heroui/button";
import { Link } from "react-router-dom";

export function ServerError() {
  const handleRefresh = () => {
    window.location.reload();
  };

  return (
    <>
      <Helmet>
        <title>500 - Server Error | NMTSA Learn</title>
        <meta
          content="An unexpected error occurred on our server"
          name="description"
        />
      </Helmet>

      <div className="min-h-[70vh] flex items-center justify-center px-4">
        <div className="text-center max-w-2xl">
          {/* Error Icon */}
          <div className="mb-8 flex justify-center">
            <div className="bg-red-100 rounded-full p-6">
              <AlertTriangle className="w-24 h-24 text-red-600" />
            </div>
          </div>

          {/* Error Message */}
          <h1 className="text-4xl md:text-5xl font-bold text-gray-900 mb-4">
            500
          </h1>
          <h2 className="text-2xl md:text-3xl font-semibold text-gray-800 mb-4">
            Internal Server Error
          </h2>
          <p className="text-lg text-gray-600 mb-8">
            Something went wrong on our end. We&apos;re working to fix the
            issue. Please try again in a few moments.
          </p>

          {/* Action Buttons */}
          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
            <Button
              color="primary"
              size="lg"
              startContent={<RefreshCw className="w-5 h-5" />}
              variant="solid"
              onPress={handleRefresh}
            >
              Try Again
            </Button>

            <Button
              as={Link}
              color="default"
              size="lg"
              startContent={<Home className="w-5 h-5" />}
              to="/"
              variant="bordered"
            >
              Go Home
            </Button>
          </div>

          {/* Additional Information */}
          <div className="mt-12 pt-8 border-t border-gray-200">
            <p className="text-sm text-gray-500 mb-4">
              If the problem persists, please contact our support team:
            </p>
            <div className="flex flex-col gap-2 text-sm text-gray-600">
              <p>
                <strong>Email:</strong>{" "}
                <a
                  className="text-blue-600 hover:underline"
                  href="mailto:support@nmtsalearn.org"
                >
                  support@nmtsalearn.org
                </a>
              </p>
              <p>
                <strong>Phone:</strong> (555) 123-4567
              </p>
            </div>
          </div>

          {/* Error Code */}
          <div className="mt-8">
            <p className="text-xs text-gray-400">
              Error Code: 500 | Server Error
            </p>
          </div>
        </div>
      </div>
    </>
  );
}
