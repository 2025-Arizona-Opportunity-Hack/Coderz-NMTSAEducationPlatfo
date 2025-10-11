import {
  Modal,
  ModalContent,
  ModalHeader,
  ModalBody,
  ModalFooter,
} from "@heroui/modal";
import { Button } from "@heroui/button";
import { Chip } from "@heroui/chip";
import { Avatar } from "@heroui/avatar";
import { Divider } from "@heroui/divider";
import { useTranslation } from "react-i18next";
import {
  Clock,
  CheckCircle,
  XCircle,
  AlertCircle,
  FileText,
  Calendar,
  Download,
  User,
} from "lucide-react";

import type { Application } from "../../types/api";

interface ApplicationDetailsProps {
  application: Application | null;
  isOpen: boolean;
  onClose: () => void;
}

export function ApplicationDetails({
  application,
  isOpen,
  onClose,
}: ApplicationDetailsProps) {
  const { t } = useTranslation();

  if (!application) return null;

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
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  return (
    <Modal
      isOpen={isOpen}
      scrollBehavior="inside"
      size="3xl"
      onClose={onClose}
    >
      <ModalContent>
        <ModalHeader className="flex flex-col gap-1">
          {t("applications.details.title")}
        </ModalHeader>
        <ModalBody>
          <div className="space-y-6">
            {/* Course Info */}
            <div className="flex gap-4">
              <img
                alt={application.course.title}
                className="object-cover rounded-lg"
                height={100}
                src={
                  application.course.thumbnailUrl ||
                  "https://via.placeholder.com/100x100"
                }
                width={100}
              />
              <div className="flex-1">
                <h3 className="text-xl font-semibold mb-2">
                  {application.course.title}
                </h3>
                <div className="flex items-center gap-2 mb-3">
                  <Avatar
                    className="w-6 h-6"
                    name={application.course.instructor.fullName}
                    size="sm"
                    src={application.course.instructor.avatarUrl}
                  />
                  <span className="text-sm text-default-600">
                    {application.course.instructor.fullName}
                  </span>
                </div>
                <Chip
                  color={statusConfig.color}
                  size="md"
                  startContent={<StatusIcon className="w-4 h-4" />}
                  variant="flat"
                >
                  {statusConfig.label}
                </Chip>
              </div>
            </div>

            <Divider />

            {/* Timeline */}
            <div className="space-y-4">
              <h4 className="font-semibold text-lg">
                {t("applications.details.timeline")}
              </h4>

              <div className="space-y-3">
                {/* Submitted */}
                <div className="flex items-start gap-3">
                  <div className="w-8 h-8 rounded-full bg-primary-100 flex items-center justify-center flex-shrink-0">
                    <Calendar className="w-4 h-4 text-primary" />
                  </div>
                  <div>
                    <p className="font-medium">
                      {t("applications.details.submitted")}
                    </p>
                    <p className="text-sm text-default-600">
                      {formatDate(application.submittedAt)}
                    </p>
                  </div>
                </div>

                {/* Reviewed */}
                {application.reviewedAt && (
                  <div className="flex items-start gap-3">
                    <div
                      className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${
                        application.status === "approved"
                          ? "bg-success-100"
                          : "bg-danger-100"
                      }`}
                    >
                      {application.status === "approved" ? (
                        <CheckCircle
                          className={`w-4 h-4 ${
                            application.status === "approved"
                              ? "text-success"
                              : "text-danger"
                          }`}
                        />
                      ) : (
                        <XCircle className="w-4 h-4 text-danger" />
                      )}
                    </div>
                    <div>
                      <p className="font-medium">
                        {t("applications.details.reviewed")}
                      </p>
                      <p className="text-sm text-default-600">
                        {formatDate(application.reviewedAt)}
                      </p>
                      {application.reviewedBy && (
                        <p className="text-xs text-default-500 flex items-center gap-1 mt-1">
                          <User className="w-3 h-3" />
                          {t("applications.details.reviewedBy")}:{" "}
                          {application.reviewedBy}
                        </p>
                      )}
                    </div>
                  </div>
                )}
              </div>
            </div>

            <Divider />

            {/* Motivation Statement */}
            <div className="space-y-2">
              <h4 className="font-semibold text-lg">
                {t("applications.details.motivation")}
              </h4>
              <p className="text-default-600 whitespace-pre-wrap">
                {application.motivationStatement}
              </p>
            </div>

            {/* Review Feedback */}
            {application.reviewFeedback && (
              <>
                <Divider />
                <div className="space-y-2">
                  <h4 className="font-semibold text-lg">
                    {t("applications.details.feedback")}
                  </h4>
                  <div
                    className={`p-4 rounded-lg ${
                      application.status === "approved"
                        ? "bg-success-50"
                        : "bg-danger-50"
                    }`}
                  >
                    <p
                      className={`${
                        application.status === "approved"
                          ? "text-success-700"
                          : "text-danger-700"
                      }`}
                    >
                      {application.reviewFeedback}
                    </p>
                  </div>
                </div>
              </>
            )}

            {/* Documents */}
            {application.documents && application.documents.length > 0 && (
              <>
                <Divider />
                <div className="space-y-3">
                  <h4 className="font-semibold text-lg">
                    {t("applications.details.documents")}
                  </h4>
                  <div className="space-y-2">
                    {application.documents.map((doc) => (
                      <div
                        key={doc.id}
                        className="flex items-center justify-between p-3 bg-default-100 rounded-lg"
                      >
                        <div className="flex items-center gap-3">
                          <FileText className="w-5 h-5 text-default-600" />
                          <div>
                            <p className="font-medium">{doc.name}</p>
                            <p className="text-xs text-default-500">
                              {t("applications.details.uploaded")}:{" "}
                              {formatDate(doc.uploadedAt)}
                            </p>
                          </div>
                        </div>
                        <Button
                          as="a"
                          color="primary"
                          download
                          href={doc.url}
                          size="sm"
                          startContent={<Download className="w-4 h-4" />}
                          variant="flat"
                        >
                          {t("common.download")}
                        </Button>
                      </div>
                    ))}
                  </div>
                </div>
              </>
            )}

            {/* Prerequisites Confirmation */}
            <Divider />
            <div className="flex items-center gap-2">
              <CheckCircle className="w-5 h-5 text-success" />
              <span className="text-sm">
                {t("applications.details.prerequisitesConfirmed")}
              </span>
            </div>
          </div>
        </ModalBody>
        <ModalFooter>
          <Button color="primary" onPress={onClose}>
            {t("common.close")}
          </Button>
        </ModalFooter>
      </ModalContent>
    </Modal>
  );
}
