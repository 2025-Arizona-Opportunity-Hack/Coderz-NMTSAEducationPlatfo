import type { Certificate as CertificateType } from "../../types/api";

import { Card, CardBody, CardHeader } from "@heroui/card";
import { Button } from "@heroui/button";
import { useTranslation } from "react-i18next";
import { Download, Award, Calendar, Share2, ExternalLink } from "lucide-react";
import {
  Dropdown,
  DropdownTrigger,
  DropdownMenu,
  DropdownItem,
} from "@heroui/dropdown";

interface CertificatesProps {
  certificates: CertificateType[];
  onDownload: (certificateId: string) => Promise<void>;
}

export function Certificates({ certificates, onDownload }: CertificatesProps) {
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

            <div className="flex gap-2">
              <Button
                className="flex-1"
                color="primary"
                startContent={<Download className="w-4 h-4" />}
                variant="flat"
                onPress={() => onDownload(certificate.id)}
              >
                {t("common.download")}
              </Button>

              <Dropdown>
                <DropdownTrigger>
                  <Button
                    isIconOnly
                    aria-label="Share certificate"
                    color="default"
                    variant="flat"
                  >
                    <Share2 className="w-4 h-4" />
                  </Button>
                </DropdownTrigger>
                <DropdownMenu aria-label="Share options">
                  <DropdownItem
                    key="linkedin"
                    startContent={<ExternalLink className="w-4 h-4" />}
                    onPress={() => {
                      const url = `https://www.linkedin.com/profile/add?startTask=CERTIFICATION_NAME&name=${encodeURIComponent(certificate.course.title)}&organizationId=&issueYear=${new Date(certificate.completedAt).getFullYear()}&issueMonth=${new Date(certificate.completedAt).getMonth() + 1}&certUrl=${encodeURIComponent(window.location.origin + "/certificates/" + certificate.id)}&certId=${certificate.id}`;

                      window.open(url, "_blank", "noopener,noreferrer");
                    }}
                  >
                    Share on LinkedIn
                  </DropdownItem>
                  <DropdownItem
                    key="twitter"
                    startContent={<ExternalLink className="w-4 h-4" />}
                    onPress={() => {
                      const text = `I just earned a certificate in ${certificate.course.title} from NMTSA Learn! 🎓`;
                      const url = `https://twitter.com/intent/tweet?text=${encodeURIComponent(text)}&url=${encodeURIComponent(window.location.origin + "/certificates/" + certificate.id)}`;

                      window.open(url, "_blank", "noopener,noreferrer");
                    }}
                  >
                    Share on Twitter
                  </DropdownItem>
                  <DropdownItem
                    key="copy"
                    onPress={() => {
                      navigator.clipboard.writeText(
                        `${window.location.origin}/certificates/${certificate.id}`,
                      );
                    }}
                  >
                    Copy Link
                  </DropdownItem>
                </DropdownMenu>
              </Dropdown>
            </div>
          </CardBody>
        </Card>
      ))}
    </div>
  );
}
