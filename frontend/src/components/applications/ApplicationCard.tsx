import { Card, CardBody, CardFooter, CardHeader } from "@heroui/card";
import { Button } from "@heroui/button";
import { Chip } from "@heroui/chip";
import { Avatar } from "@heroui/avatar";
import { useTranslation } from "react-i18next";
import {
  Clock,
  CheckCircle,
  XCircle,
  AlertCircle,
  FileText,
  Calendar,
} from "lucide-react";

import type { Application } from "../../types/api";

interface ApplicationCardProps {
  application: Application;
  onViewDetails: (application: Application) => void;
  onCancel?: (applicationId: string) => void;
}

export function ApplicationCard({
  application,
  onViewDetails,
  onCancel,
}: ApplicationCardProps) {
  const { t } = useTranslation();

  const getStatusConfig = (status: Application["status"]) => {
    switch (status) {
      case "pending":
        return {
          color: "warning" as const,
          icon: Clock,
          label: t("applications.status.pending"),
        };
      case "under_review":
        return {
          color: "primary" as const,
          icon: AlertCircle,
          label: t("applications.status.underReview"),
        };
      case "approved":
        return {
          color: "success" as const,
          icon: CheckCircle,
          label: t("applications.status.approved"),
        };
      case "rejected":
        return {
          color: "danger" as const,
          icon: XCircle,
          label: t("applications.status.rejected"),
        };
      case "cancelled":
        return {
          color: "default" as const,
          icon: XCircle,
          label: t("applications.status.cancelled"),
        };
    }
  };

  const statusConfig = getStatusConfig(application.status);
  const StatusIcon = statusConfig.icon;

  const formatDate = (date: string) => {
    return new Date(date).toLocaleDateString(undefined, {
      day: "numeric",
      month: "long",
      year: "numeric",
    });
  };

  return (
    <Card className="w-full">
      <CardHeader className="flex gap-3">
        <img
          alt={application.course.title}
          className="object-cover rounded-lg"
          height={80}
          src={
            application.course.thumbnailUrl ||
            "https://via.placeholder.com/80x80"
          }
          width={80}
        />
        <div className="flex flex-col flex-1">
          <h3 className="text-lg font-semibold">{application.course.title}</h3>
          <div className="flex items-center gap-2 mt-1">
            <Avatar
              className="w-6 h-6"
              name={application.course.instructor.fullName}
              size="sm"
              src={application.course.instructor.avatarUrl}
            />
            <p className="text-sm text-default-600">
              {application.course.instructor.fullName}
            </p>
          </div>
        </div>
        <Chip
          color={statusConfig.color}
          size="sm"
          startContent={<StatusIcon className="w-4 h-4" />}
          variant="flat"
        >
          {statusConfig.label}
        </Chip>
      </CardHeader>

      <CardBody className="py-4">
        <div className="space-y-3">
          {/* Submission Date */}
          <div className="flex items-center gap-2 text-sm">
            <Calendar className="w-4 h-4 text-default-400" />
            <span className="text-default-600">
              {t("applications.submittedOn")}:{" "}
              <span className="font-medium">
                {formatDate(application.submittedAt)}
              </span>
            </span>
          </div>

          {/* Review Date (if reviewed) */}
          {application.reviewedAt && (
            <div className="flex items-center gap-2 text-sm">
              <FileText className="w-4 h-4 text-default-400" />
              <span className="text-default-600">
                {t("applications.reviewedOn")}:{" "}
                <span className="font-medium">
                  {formatDate(application.reviewedAt)}
                </span>
              </span>
            </div>
          )}

          {/* Motivation Statement Preview */}
          <div className="text-sm">
            <p className="text-default-600 font-medium mb-1">
              {t("applications.motivation")}:
            </p>
            <p className="text-default-500 line-clamp-2">
              {application.motivationStatement}
            </p>
          </div>

          {/* Documents Count */}
          {application.documents && application.documents.length > 0 && (
            <div className="flex items-center gap-2 text-sm text-default-600">
              <FileText className="w-4 h-4" />
              <span>
                {application.documents.length}{" "}
                {t("applications.documentsAttached")}
              </span>
            </div>
          )}
        </div>
      </CardBody>

      <CardFooter className="gap-2">
        <Button
          color="primary"
          size="sm"
          variant="flat"
          onPress={() => onViewDetails(application)}
        >
          {t("applications.viewDetails")}
        </Button>
        {application.status === "pending" && onCancel && (
          <Button
            color="danger"
            size="sm"
            variant="light"
            onPress={() => onCancel(application.id)}
          >
            {t("applications.cancel")}
          </Button>
        )}
      </CardFooter>
    </Card>
  );
}
