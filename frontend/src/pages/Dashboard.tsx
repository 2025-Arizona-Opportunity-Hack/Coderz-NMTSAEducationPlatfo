import { useState, useEffect } from "react";
import { useTranslation } from "react-i18next";
import { Helmet } from "react-helmet-async";
import { Spinner } from "@heroui/spinner";
import { Tabs, Tab } from "@heroui/tabs";

import { useAuthStore } from "../store/useAuthStore";
import { dashboardService } from "../services/dashboard.service";
import {
  DashboardStats as StatsType,
  EnrollmentWithProgress,
  Certificate,
  ContinueLearningItem,
} from "../types/api";
import { DashboardStats } from "../components/dashboard/DashboardStats";
import { ContinueLearning } from "../components/dashboard/ContinueLearning";
import { EnrolledCourses } from "../components/dashboard/EnrolledCourses";
import { Certificates } from "../components/dashboard/Certificates";

export function Dashboard() {
  const { t } = useTranslation();
  const { profile } = useAuthStore();
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState<StatsType | null>(null);
  const [enrollments, setEnrollments] = useState<EnrollmentWithProgress[]>([]);
  const [continueItems, setContinueItems] = useState<ContinueLearningItem[]>(
    [],
  );
  const [certificates, setCertificates] = useState<Certificate[]>([]);
  const [error, setError] = useState<string | null>(null);

  // Pagination state
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [filter, setFilter] = useState<"all" | "in-progress" | "completed">(
    "all",
  );

  useEffect(() => {
    loadDashboardData();
  }, [currentPage, filter]);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      setError(null);

      const [
        statsData,
        enrollmentsData,
        continueData,
        certificatesData,
      ] = await Promise.all([
        dashboardService.getStats(),
        dashboardService.getEnrollments(
          currentPage,
          12,
          filter === "all" ? undefined : filter,
        ),
        dashboardService.getContinueLearning(),
        dashboardService.getCertificates(),
      ]);

      setStats(statsData);
      setEnrollments(enrollmentsData.data);
      setTotalPages(enrollmentsData.pagination.totalPages);
      setContinueItems(continueData);
      setCertificates(certificatesData);
    } catch (err: any) {
      setError(err.response?.data?.message || "Failed to load dashboard");
    } finally {
      setLoading(false);
    }
  };

  const handleDownloadCertificate = async (certificateId: string) => {
    try {
      await dashboardService.downloadCertificate(certificateId);
    } catch (err: any) {
      alert(err.response?.data?.message || "Failed to download certificate");
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-[60vh]">
        <Spinner size="lg" color="primary" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex justify-center items-center min-h-[60vh]">
        <div className="text-center">
          <p className="text-danger text-lg mb-4">{error}</p>
          <button
            onClick={loadDashboardData}
            className="px-4 py-2 bg-primary text-white rounded-lg hover:bg-primary-600"
          >
            {t('common.tryAgain')}
          </button>
        </div>
      </div>
    );
  }

  return (
    <>
      <Helmet>
        <title>{t('dashboard.title')} - {t('common.siteName')}</title>
        <meta name="description" content={t('dashboard.title')} />
        <meta name="robots" content="noindex, nofollow" />
      </Helmet>

      <div className="container mx-auto px-4 py-8 max-w-7xl">
        {/* Welcome Section */}
        <div className="mb-8">
          <h1 className="text-3xl md:text-4xl font-bold mb-2">
            {t("dashboard.welcome")},{" "}
            {profile?.fullName || profile?.email || "Student"}!
          </h1>
          <p className="text-default-600">{t("dashboard.continueLearning")}</p>
        </div>

        {/* Tabs Navigation */}
        <Tabs
          aria-label="Dashboard sections"
          color="primary"
          variant="underlined"
          classNames={{
            cursor: "w-full bg-primary",
            tab: "max-w-fit px-0 h-12",
            tabContent: "group-data-[selected=true]:text-primary",
            tabList:
              "gap-6 w-full relative rounded-none p-0 border-b border-divider",
          }}
        >
          {/* Overview Tab */}
          <Tab
            key="overview"
            title={
              <div className="flex items-center space-x-2">
                <span>{t("dashboard.overview")}</span>
              </div>
            }
          >
            <div className="py-8 space-y-8">
              {/* Stats Section */}
              {stats && <DashboardStats stats={stats} />}

              {/* Continue Learning Section */}
              <ContinueLearning items={continueItems} />
            </div>
          </Tab>

          {/* My Courses Tab */}
          <Tab
            key="courses"
            title={
              <div className="flex items-center space-x-2">
                <span>{t("dashboard.myCourses")}</span>
              </div>
            }
          >
            <div className="py-8">
              <EnrolledCourses
                currentPage={currentPage}
                enrollments={enrollments}
                totalPages={totalPages}
                onFilterChange={setFilter}
                onPageChange={setCurrentPage}
              />
            </div>
          </Tab>

          {/* My Certificates Tab */}
          <Tab
            key="certificates"
            title={
              <div className="flex items-center space-x-2">
                <span>{t("dashboard.myCertificates")}</span>
              </div>
            }
          >
            <div className="py-8">
              <Certificates
                certificates={certificates}
                onDownload={handleDownloadCertificate}
              />
            </div>
          </Tab>
        </Tabs>
      </div>
    </>
  );
}
