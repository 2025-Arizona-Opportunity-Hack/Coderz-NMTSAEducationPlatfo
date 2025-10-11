import { Card, CardBody, CardHeader } from "@heroui/card";
import { Button } from "@heroui/button";
import { useTranslation } from "react-i18next";
import { Download, Award, Calendar } from "lucide-react";

import type { Certificate as CertificateType } from "../../types/api";

interface CertificatesProps {
  certificates: CertificateType[];
  onDownload: (certificateId: string) => Promise<void>;
}

export function Certificates({
  certificates,
  onDownload,
}: CertificatesProps) {
  const { t } = useTranslation();

  if (certificates.length === 0) {
    return (
      <Card>
        <CardBody className="py-12">
          <div className="text-center">
            <Award className="w-16 h-16 text-gray-300 mx-auto mb-4" />
            <p className="text-gray-500">{t("dashboard.noCertificates")}</p>
            <p className="text-sm text-gray-400 mt-2">
              {t("dashboard.completeCourses")}
            </p>
          </div>
        </CardBody>
      </Card>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {certificates.map((certificate) => (
        <Card
          key={certificate.id}
          className="hover:shadow-lg transition-shadow"
        >
          <CardHeader className="pb-0">
            <div className="w-full h-40 bg-gradient-to-br from-blue-600 to-purple-700 rounded-t-lg flex items-center justify-center">
              <Award className="w-20 h-20 text-white opacity-80" />
            </div>
          </CardHeader>
          <CardBody className="space-y-4">
            <div>
              <h3 className="font-semibold text-lg line-clamp-2">
                {certificate.course.title}
              </h3>
              <p className="text-sm text-gray-600 mt-1">
                {t("dashboard.instructor")}: {certificate.course.instructor}
              </p>
            </div>

            <div className="flex items-center gap-2 text-sm text-gray-600">
              <Calendar className="w-4 h-4" />
              <span>
                {t("dashboard.completed")}:{" "}
                {new Date(certificate.completedAt).toLocaleDateString()}
              </span>
            </div>

            <Button
              className="w-full"
              color="primary"
              startContent={<Download className="w-4 h-4" />}
              variant="flat"
              onPress={() => onDownload(certificate.id)}
            >
              {t("dashboard.downloadCertificate")}
            </Button>
          </CardBody>
        </Card>
      ))}
    </div>
  );
}
