import { Card, CardBody, CardHeader } from "@heroui/card";
import { Button } from "@heroui/button";
import { useTranslation } from "react-i18next";
import { Linkedin, Twitter, Globe } from "lucide-react";

import type { CourseDetail } from "../../types/api";

interface InstructorCardProps {
  instructor: CourseDetail["instructor"];
}

export function InstructorCard({ instructor }: InstructorCardProps) {
  const { t } = useTranslation();

  return (
    <Card className="w-full">
      <CardHeader className="flex-col items-start px-6 pt-6">
        <h2 className="text-2xl font-bold mb-1">
          {t("course.aboutInstructor")}
        </h2>
      </CardHeader>
      <CardBody className="px-6 pb-6">
        <div className="flex items-start gap-4 mb-4">
          <img
            alt={instructor.fullName}
            className="w-20 h-20 rounded-full object-cover"
            src={
              instructor.avatarUrl ||
              `https://ui-avatars.com/api/?name=${encodeURIComponent(instructor.fullName)}&size=80`
            }
          />
          <div className="flex-1">
            <h3 className="text-xl font-semibold mb-1">
              {instructor.fullName}
            </h3>
            {instructor.credentials && (
              <p className="text-sm text-gray-600 mb-2">
                {instructor.credentials}
              </p>
            )}
            {instructor.socialLinks && (
              <div className="flex items-center gap-2">
                {instructor.socialLinks.linkedin && (
                  <Button
                    isIconOnly
                    aria-label="LinkedIn"
                    as="a"
                    href={instructor.socialLinks.linkedin}
                    rel="noopener noreferrer"
                    size="sm"
                    target="_blank"
                    variant="light"
                  >
                    <Linkedin className="w-4 h-4" />
                  </Button>
                )}
                {instructor.socialLinks.twitter && (
                  <Button
                    isIconOnly
                    aria-label="Twitter"
                    as="a"
                    href={instructor.socialLinks.twitter}
                    rel="noopener noreferrer"
                    size="sm"
                    target="_blank"
                    variant="light"
                  >
                    <Twitter className="w-4 h-4" />
                  </Button>
                )}
                {instructor.socialLinks.website && (
                  <Button
                    isIconOnly
                    aria-label="Website"
                    as="a"
                    href={instructor.socialLinks.website}
                    rel="noopener noreferrer"
                    size="sm"
                    target="_blank"
                    variant="light"
                  >
                    <Globe className="w-4 h-4" />
                  </Button>
                )}
              </div>
            )}
          </div>
        </div>

        {instructor.bio && (
          <div className="text-gray-700">
            <p className="leading-relaxed">{instructor.bio}</p>
          </div>
        )}
      </CardBody>
    </Card>
  );
}
