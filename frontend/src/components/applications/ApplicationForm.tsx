import { useState } from "react";
import { Modal, ModalContent, ModalHeader, ModalBody, ModalFooter } from "@heroui/modal";
import { Button } from "@heroui/button";
import { Input } from "@heroui/input";
import { Textarea } from "@heroui/input";
import { Select, SelectItem } from "@heroui/select";
import { Checkbox } from "@heroui/checkbox";
import { Card, CardBody } from "@heroui/card";
import { Avatar } from "@heroui/avatar";
import { useTranslation } from "react-i18next";
import { Upload, X, FileText } from "lucide-react";

interface EligibleCourse {
  id: string;
  title: string;
  description: string;
  thumbnailUrl?: string;
  prerequisites: string[];
  instructor: {
    id: string;
    fullName: string;
    avatarUrl?: string;
  };
}

interface ApplicationFormProps {
  isOpen: boolean;
  onClose: () => void;
  eligibleCourses: EligibleCourse[];
  onSubmit: (data: {
    courseId: string;
    motivationStatement: string;
    prerequisitesConfirmed: boolean;
    documents?: File[];
  }) => Promise<void>;
}

export function ApplicationForm({
  isOpen,
  onClose,
  eligibleCourses,
  onSubmit,
}: ApplicationFormProps) {
  const { t } = useTranslation();
  const [selectedCourseId, setSelectedCourseId] = useState<string>("");
  const [motivationStatement, setMotivationStatement] = useState("");
  const [prerequisitesConfirmed, setPrerequisitesConfirmed] = useState(false);
  const [documents, setDocuments] = useState<File[]>([]);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errors, setErrors] = useState<{
    courseId?: string;
    motivation?: string;
    prerequisites?: string;
  }>({});

  const selectedCourse = eligibleCourses.find((c) => c.id === selectedCourseId);

  const validateForm = () => {
    const newErrors: typeof errors = {};

    if (!selectedCourseId) {
      newErrors.courseId = t("applications.form.errors.courseRequired");
    }

    if (!motivationStatement || motivationStatement.trim().length < 50) {
      newErrors.motivation = t("applications.form.errors.motivationTooShort");
    }

    if (!prerequisitesConfirmed) {
      newErrors.prerequisites = t("applications.form.errors.prerequisitesRequired");
    }

    setErrors(newErrors);

    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async () => {
    if (!validateForm()) return;

    try {
      setIsSubmitting(true);
      await onSubmit({
        courseId: selectedCourseId,
        motivationStatement,
        prerequisitesConfirmed,
        documents: documents.length > 0 ? documents : undefined,
      });
      handleClose();
    } catch (error) {
      console.error("Failed to submit application:", error);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleClose = () => {
    setSelectedCourseId("");
    setMotivationStatement("");
    setPrerequisitesConfirmed(false);
    setDocuments([]);
    setErrors({});
    onClose();
  };

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(event.target.files || []);

    setDocuments((prev) => [...prev, ...files]);
  };

  const removeDocument = (index: number) => {
    setDocuments((prev) => prev.filter((_, i) => i !== index));
  };

  return (
    <Modal
      isOpen={isOpen}
      scrollBehavior="inside"
      size="2xl"
      onClose={handleClose}
    >
      <ModalContent>
        <ModalHeader className="flex flex-col gap-1">
          {t("applications.form.title")}
        </ModalHeader>
        <ModalBody>
          <div className="space-y-6">
            {/* Course Selection */}
            <div>
              <Select
                errorMessage={errors.courseId}
                isInvalid={!!errors.courseId}
                isRequired
                label={t("applications.form.selectCourse")}
                placeholder={t("applications.form.selectCoursePlaceholder")}
                selectedKeys={selectedCourseId ? [selectedCourseId] : []}
                onSelectionChange={(keys) => {
                  const key = Array.from(keys)[0] as string;

                  setSelectedCourseId(key);
                  setErrors((prev) => ({ ...prev, courseId: undefined }));
                }}
              >
                {eligibleCourses.map((course) => (
                  <SelectItem key={course.id} textValue={course.title}>
                    <div className="flex items-center gap-2">
                      <Avatar
                        className="flex-shrink-0"
                        name={course.instructor.fullName}
                        size="sm"
                        src={course.instructor.avatarUrl}
                      />
                      <div className="flex flex-col">
                        <span className="text-small">{course.title}</span>
                        <span className="text-tiny text-default-400">
                          {course.instructor.fullName}
                        </span>
                      </div>
                    </div>
                  </SelectItem>
                ))}
              </Select>
            </div>

            {/* Selected Course Info */}
            {selectedCourse && (
              <Card>
                <CardBody>
                  <div className="space-y-3">
                    <h4 className="font-semibold">
                      {t("applications.form.courseDetails")}
                    </h4>
                    <p className="text-sm text-default-600">
                      {selectedCourse.description}
                    </p>
                    {selectedCourse.prerequisites.length > 0 && (
                      <div>
                        <p className="text-sm font-medium mb-2">
                          {t("applications.form.prerequisites")}:
                        </p>
                        <ul className="list-disc list-inside space-y-1">
                          {selectedCourse.prerequisites.map((prereq, index) => (
                            <li
                              key={index}
                              className="text-sm text-default-600"
                            >
                              {prereq}
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                </CardBody>
              </Card>
            )}

            {/* Motivation Statement */}
            <Textarea
              errorMessage={errors.motivation}
              isInvalid={!!errors.motivation}
              isRequired
              label={t("applications.form.motivation")}
              maxRows={8}
              minRows={4}
              placeholder={t("applications.form.motivationPlaceholder")}
              value={motivationStatement}
              onChange={(e) => {
                setMotivationStatement(e.target.value);
                setErrors((prev) => ({ ...prev, motivation: undefined }));
              }}
            />
            <p className="text-xs text-default-500">
              {t("applications.form.motivationHint")} ({motivationStatement.length}/500)
            </p>

            {/* Prerequisites Confirmation */}
            <Checkbox
              isInvalid={!!errors.prerequisites}
              isSelected={prerequisitesConfirmed}
              onValueChange={(checked) => {
                setPrerequisitesConfirmed(checked);
                setErrors((prev) => ({ ...prev, prerequisites: undefined }));
              }}
            >
              <span className="text-sm">
                {t("applications.form.confirmPrerequisites")}
              </span>
            </Checkbox>
            {errors.prerequisites && (
              <p className="text-xs text-danger">{errors.prerequisites}</p>
            )}

            {/* Document Upload */}
            <div className="space-y-3">
              <label className="block text-sm font-medium">
                {t("applications.form.documents")}{" "}
                <span className="text-default-400">
                  ({t("common.optional")})
                </span>
              </label>
              <div className="border-2 border-dashed border-default-300 rounded-lg p-4 text-center">
                <input
                  multiple
                  accept=".pdf,.doc,.docx,.jpg,.jpeg,.png"
                  className="hidden"
                  id="file-upload"
                  type="file"
                  onChange={handleFileUpload}
                />
                <label
                  className="cursor-pointer flex flex-col items-center"
                  htmlFor="file-upload"
                >
                  <Upload className="w-8 h-8 text-default-400 mb-2" />
                  <span className="text-sm text-default-600">
                    {t("applications.form.uploadDocuments")}
                  </span>
                  <span className="text-xs text-default-400 mt-1">
                    PDF, DOC, DOCX, JPG, PNG
                  </span>
                </label>
              </div>

              {/* Uploaded Documents List */}
              {documents.length > 0 && (
                <div className="space-y-2">
                  {documents.map((file, index) => (
                    <div
                      key={index}
                      className="flex items-center justify-between p-2 bg-default-100 rounded-lg"
                    >
                      <div className="flex items-center gap-2">
                        <FileText className="w-4 h-4 text-default-600" />
                        <span className="text-sm">{file.name}</span>
                        <span className="text-xs text-default-400">
                          ({(file.size / 1024).toFixed(1)} KB)
                        </span>
                      </div>
                      <Button
                        isIconOnly
                        color="danger"
                        size="sm"
                        variant="light"
                        onPress={() => removeDocument(index)}
                      >
                        <X className="w-4 h-4" />
                      </Button>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </ModalBody>
        <ModalFooter>
          <Button color="danger" variant="light" onPress={handleClose}>
            {t("common.cancel")}
          </Button>
          <Button
            color="primary"
            isLoading={isSubmitting}
            onPress={handleSubmit}
          >
            {t("applications.form.submit")}
          </Button>
        </ModalFooter>
      </ModalContent>
    </Modal>
  );
}
