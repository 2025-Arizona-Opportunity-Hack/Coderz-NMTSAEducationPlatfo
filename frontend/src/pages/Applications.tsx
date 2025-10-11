import { useState, useEffect } from "react";
import { useTranslation } from "react-i18next";
import { Helmet } from "react-helmet-async";
import { Tabs, Tab } from "@heroui/tabs";
import { Button } from "@heroui/button";
import { Spinner } from "@heroui/spinner";
import { Pagination } from "@heroui/pagination";
import { useDisclosure } from "@heroui/use-disclosure";
import { Plus, FileCheck } from "lucide-react";

import { applicationsService } from "../services/applications.service";
import type { Application, ApplicationStatus } from "../types/api";
import { ApplicationCard } from "../components/applications/ApplicationCard";
import { ApplicationForm } from "../components/applications/ApplicationForm";
import { ApplicationDetails } from "../components/applications/ApplicationDetails";

export function Applications() {
  const { t } = useTranslation();
  const [loading, setLoading] = useState(true);
  const [applications, setApplications] = useState<Application[]>([]);
  const [totalPages, setTotalPages] = useState(1);
  const [currentPage, setCurrentPage] = useState(1);
  const [filter, setFilter] = useState<ApplicationStatus | "all">("all");
  const [selectedApplication, setSelectedApplication] =
    useState<Application | null>(null);
  const [eligibleCourses, setEligibleCourses] = useState<any[]>([]);
  const [error, setError] = useState<string | null>(null);

  const formDisclosure = useDisclosure();
  const detailsDisclosure = useDisclosure();

  useEffect(() => {
    loadApplications();
  }, [currentPage, filter]);

  useEffect(() => {
    loadEligibleCourses();
  }, []);

  const loadApplications = async () => {
    try {
      setLoading(true);
      setError(null);

      const statusFilter =
        filter === "all" ? undefined : (filter as ApplicationStatus);
      const response = await applicationsService.getApplications(
        currentPage,
        12,
        statusFilter,
      );

      setApplications(response.data);
      setTotalPages(response.pagination.totalPages);
    } catch (err: any) {
      setError(err.response?.data?.message || "Failed to load applications");
    } finally {
      setLoading(false);
    }
  };

  const loadEligibleCourses = async () => {
    try {
      const courses = await applicationsService.getEligibleCourses();

      setEligibleCourses(courses);
    } catch (err) {
      console.error("Failed to load eligible courses:", err);
    }
  };

  const handleCreateApplication = async (data: {
    courseId: string;
    motivationStatement: string;
    prerequisitesConfirmed: boolean;
    documents?: File[];
  }) => {
    await applicationsService.createApplication(data);
    await loadApplications();
    formDisclosure.onClose();
  };

  const handleCancelApplication = async (applicationId: string) => {
    if (
      !window.confirm(t("applications.confirmCancel"))
    ) {
      return;
    }

    try {
      await applicationsService.cancelApplication(applicationId);
      await loadApplications();
    } catch (err: any) {
      alert(err.response?.data?.message || "Failed to cancel application");
    }
  };

  const handleViewDetails = (application: Application) => {
    setSelectedApplication(application);
    detailsDisclosure.onOpen();
  };

  const handleFilterChange = (key: string) => {
    setFilter(key as ApplicationStatus | "all");
    setCurrentPage(1);
  };

  if (loading && applications.length === 0) {
    return (
      <div className="flex justify-center items-center min-h-[60vh]">
        <Spinner color="primary" size="lg" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex justify-center items-center min-h-[60vh]">
        <div className="text-center">
          <p className="text-danger text-lg mb-4">{error}</p>
          <Button color="primary" onPress={loadApplications}>
            {t("common.tryAgain")}
          </Button>
        </div>
      </div>
    );
  }

  return (
    <>
      <Helmet>
        <title>
          {t("applications.title")} - {t("common.siteName")}
        </title>
        <meta content={t("applications.description")} name="description" />
        <meta content="noindex, nofollow" name="robots" />
      </Helmet>

      <div className="container mx-auto px-4 py-8 max-w-7xl">
        {/* Header */}
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-3xl md:text-4xl font-bold mb-2">
              {t("applications.title")}
            </h1>
            <p className="text-default-600">{t("applications.subtitle")}</p>
          </div>
          <Button
            color="primary"
            size="lg"
            startContent={<Plus className="w-5 h-5" />}
            onPress={formDisclosure.onOpen}
          >
            {t("applications.newApplication")}
          </Button>
        </div>

        {/* Tabs */}
        <Tabs
          aria-label="Application filters"
          color="primary"
          selectedKey={filter}
          variant="underlined"
          onSelectionChange={(key) => handleFilterChange(key as string)}
        >
          <Tab
            key="all"
            title={
              <div className="flex items-center gap-2">
                <span>{t("applications.tabs.all")}</span>
              </div>
            }
          />
          <Tab
            key="pending"
            title={
              <div className="flex items-center gap-2">
                <span>{t("applications.tabs.pending")}</span>
              </div>
            }
          />
          <Tab
            key="under_review"
            title={
              <div className="flex items-center gap-2">
                <span>{t("applications.tabs.underReview")}</span>
              </div>
            }
          />
          <Tab
            key="approved"
            title={
              <div className="flex items-center gap-2">
                <span>{t("applications.tabs.approved")}</span>
              </div>
            }
          />
          <Tab
            key="rejected"
            title={
              <div className="flex items-center gap-2">
                <span>{t("applications.tabs.rejected")}</span>
              </div>
            }
          />
        </Tabs>

        {/* Applications Grid */}
        <div className="mt-8">
          {loading ? (
            <div className="flex justify-center py-12">
              <Spinner color="primary" size="lg" />
            </div>
          ) : applications.length === 0 ? (
            <div className="text-center py-12">
              <FileCheck className="w-16 h-16 text-default-300 mx-auto mb-4" />
              <h3 className="text-xl font-semibold mb-2">
                {t("applications.noApplications")}
              </h3>
              <p className="text-default-600 mb-4">
                {t("applications.noApplicationsDescription")}
              </p>
              <Button
                color="primary"
                startContent={<Plus className="w-5 h-5" />}
                onPress={formDisclosure.onOpen}
              >
                {t("applications.newApplication")}
              </Button>
            </div>
          ) : (
            <>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {applications.map((application) => (
                  <ApplicationCard
                    key={application.id}
                    application={application}
                    onCancel={handleCancelApplication}
                    onViewDetails={handleViewDetails}
                  />
                ))}
              </div>

              {/* Pagination */}
              {totalPages > 1 && (
                <div className="flex justify-center mt-8">
                  <Pagination
                    color="primary"
                    page={currentPage}
                    showControls
                    total={totalPages}
                    onChange={setCurrentPage}
                  />
                </div>
              )}
            </>
          )}
        </div>
      </div>

      {/* Application Form Modal */}
      <ApplicationForm
        eligibleCourses={eligibleCourses}
        isOpen={formDisclosure.isOpen}
        onClose={formDisclosure.onClose}
        onSubmit={handleCreateApplication}
      />

      {/* Application Details Modal */}
      <ApplicationDetails
        application={selectedApplication}
        isOpen={detailsDisclosure.isOpen}
        onClose={detailsDisclosure.onClose}
      />
    </>
  );
}
