import { useState } from "react";
import {
  Modal,
  ModalContent,
  ModalHeader,
  ModalBody,
  ModalFooter,
} from "@heroui/modal";
import { Button } from "@heroui/button";
import { Input } from "@heroui/input";
import { Textarea } from "@heroui/input";
import { Chip } from "@heroui/chip";
import { useTranslation } from "react-i18next";
import { X } from "lucide-react";

interface CreatePostModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: { title: string; content: string; tags: string[] }) => Promise<void>;
  availableTags?: string[];
}

export function CreatePostModal({
  isOpen,
  onClose,
  onSubmit,
  availableTags = [],
}: CreatePostModalProps) {
  const { t } = useTranslation();
  const [title, setTitle] = useState("");
  const [content, setContent] = useState("");
  const [selectedTags, setSelectedTags] = useState<string[]>([]);
  const [customTag, setCustomTag] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errors, setErrors] = useState<{ title?: string; content?: string }>({});

  const validateForm = () => {
    const newErrors: typeof errors = {};

    if (!title || title.trim().length < 5) {
      newErrors.title = t("forum.form.errors.titleTooShort");
    }

    if (!content || content.trim().length < 20) {
      newErrors.content = t("forum.form.errors.contentTooShort");
    }

    setErrors(newErrors);

    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async () => {
    if (!validateForm()) return;

    try {
      setIsSubmitting(true);
      await onSubmit({ title: title.trim(), content: content.trim(), tags: selectedTags });
      handleClose();
    } catch (error) {
      console.error("Failed to create post:", error);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleClose = () => {
    setTitle("");
    setContent("");
    setSelectedTags([]);
    setCustomTag("");
    setErrors({});
    onClose();
  };

  const handleAddTag = (tag: string) => {
    const normalizedTag = tag.trim().toLowerCase();

    if (normalizedTag && !selectedTags.includes(normalizedTag) && selectedTags.length < 5) {
      setSelectedTags([...selectedTags, normalizedTag]);
      setCustomTag("");
    }
  };

  const handleRemoveTag = (tag: string) => {
    setSelectedTags(selectedTags.filter((t) => t !== tag));
  };

  return (
    <Modal isOpen={isOpen} scrollBehavior="inside" size="2xl" onClose={handleClose}>
      <ModalContent>
        <ModalHeader>{t("forum.form.createPost")}</ModalHeader>
        <ModalBody>
          <div className="space-y-4">
            <Input
              errorMessage={errors.title}
              isInvalid={!!errors.title}
              isRequired
              label={t("forum.form.title")}
              placeholder={t("forum.form.titlePlaceholder")}
              value={title}
              onChange={(e) => {
                setTitle(e.target.value);
                setErrors((prev) => ({ ...prev, title: undefined }));
              }}
            />

            <Textarea
              errorMessage={errors.content}
              isInvalid={!!errors.content}
              isRequired
              label={t("forum.form.content")}
              maxRows={12}
              minRows={6}
              placeholder={t("forum.form.contentPlaceholder")}
              value={content}
              onChange={(e) => {
                setContent(e.target.value);
                setErrors((prev) => ({ ...prev, content: undefined }));
              }}
            />

            <div>
              <label className="block text-sm font-medium mb-2">
                {t("forum.form.tags")} ({t("common.optional")})
              </label>
              <div className="flex gap-2 mb-2">
                <Input
                  placeholder={t("forum.form.addTag")}
                  size="sm"
                  value={customTag}
                  onChange={(e) => setCustomTag(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === "Enter") {
                      e.preventDefault();
                      handleAddTag(customTag);
                    }
                  }}
                />
                <Button
                  color="primary"
                  size="sm"
                  onPress={() => handleAddTag(customTag)}
                >
                  {t("forum.form.add")}
                </Button>
              </div>

              {selectedTags.length > 0 && (
                <div className="flex flex-wrap gap-2 mb-3">
                  {selectedTags.map((tag) => (
                    <Chip
                      key={tag}
                      color="primary"
                      endContent={
                        <button
                          className="ml-1"
                          onClick={() => handleRemoveTag(tag)}
                        >
                          <X className="w-3 h-3" />
                        </button>
                      }
                      variant="flat"
                    >
                      {tag}
                    </Chip>
                  ))}
                </div>
              )}

              {availableTags.length > 0 && (
                <div>
                  <p className="text-xs text-default-500 mb-2">
                    {t("forum.form.popularTags")}:
                  </p>
                  <div className="flex flex-wrap gap-2">
                    {availableTags.slice(0, 10).map((tag) => (
                      <Chip
                        key={tag}
                        className="cursor-pointer"
                        color={selectedTags.includes(tag) ? "primary" : "default"}
                        size="sm"
                        variant="flat"
                        onClick={() => {
                          if (selectedTags.includes(tag)) {
                            handleRemoveTag(tag);
                          } else {
                            handleAddTag(tag);
                          }
                        }}
                      >
                        {tag}
                      </Chip>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        </ModalBody>
        <ModalFooter>
          <Button color="danger" variant="light" onPress={handleClose}>
            {t("common.cancel")}
          </Button>
          <Button color="primary" isLoading={isSubmitting} onPress={handleSubmit}>
            {t("forum.form.publish")}
          </Button>
        </ModalFooter>
      </ModalContent>
    </Modal>
  );
}
