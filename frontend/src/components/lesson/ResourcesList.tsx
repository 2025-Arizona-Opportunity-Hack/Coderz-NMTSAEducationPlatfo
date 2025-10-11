import { Card, CardBody, CardHeader } from "@heroui/card";
import { Button } from "@heroui/button";
import { useTranslation } from "react-i18next";
import { Download, FileText, FileArchive, FileImage } from "lucide-react";

import type { Resource } from "../../types/api";

interface ResourcesListProps {
  resources: Resource[];
}

export function ResourcesList({ resources }: ResourcesListProps) {
  const { t } = useTranslation();

  const getFileIcon = (type: string) => {
    if (type.includes("pdf") || type.includes("doc")) return FileText;
    if (type.includes("zip") || type.includes("rar")) return FileArchive;
    if (type.includes("image") || type.includes("png") || type.includes("jpg"))
      return FileImage;

    return FileText;
  };

  const formatFileSize = (bytes?: number) => {
    if (!bytes) return "";

    const kb = bytes / 1024;

    if (kb < 1024) return `${kb.toFixed(1)} KB`;

    return `${(kb / 1024).toFixed(1)} MB`;
  };

  if (resources.length === 0) {
    return (
      <Card>
        <CardBody>
          <p className="text-center text-gray-500 py-8">
            {t("lesson.noResources")}
          </p>
        </CardBody>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <h3 className="text-lg font-semibold">{t("lesson.resources")}</h3>
      </CardHeader>
      <CardBody>
        <div className="space-y-3">
          {resources.map((resource) => {
            const Icon = getFileIcon(resource.type);

            return (
              <div
                key={resource.id}
                className="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
              >
                <div className="flex items-center gap-3 flex-1">
                  <Icon className="w-5 h-5 text-gray-600" />
                  <div className="flex-1 min-w-0">
                    <p className="font-medium text-gray-900 truncate">
                      {resource.title}
                    </p>
                    {resource.fileSize && (
                      <p className="text-sm text-gray-500">
                        {formatFileSize(resource.fileSize)}
                      </p>
                    )}
                  </div>
                </div>
                <Button
                  as="a"
                  color="primary"
                  download
                  href={resource.fileUrl}
                  size="sm"
                  startContent={<Download className="w-4 h-4" />}
                  variant="flat"
                >
                  {t("lesson.downloadResource")}
                </Button>
              </div>
            );
          })}
        </div>
      </CardBody>
    </Card>
  );
}
