import type { Note } from "../../types/api";

import { useState } from "react";
import { Button } from "@heroui/button";
import { Textarea } from "@heroui/input";
import { Card, CardBody, CardHeader } from "@heroui/card";
import { useTranslation } from "react-i18next";
import { Trash2, Edit2, Save, X } from "lucide-react";

interface NotesSidebarProps {
  notes: Note[];
  onAddNote: (content: string, timestamp?: number) => Promise<void>;
  onUpdateNote: (noteId: string, content: string) => Promise<void>;
  onDeleteNote: (noteId: string) => Promise<void>;
  currentTimestamp?: number;
}

export function NotesSidebar({
  notes,
  onAddNote,
  onUpdateNote,
  onDeleteNote,
  currentTimestamp,
}: NotesSidebarProps) {
  const { t } = useTranslation();
  const [newNoteContent, setNewNoteContent] = useState("");
  const [editingNoteId, setEditingNoteId] = useState<string | null>(null);
  const [editContent, setEditContent] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleAddNote = async () => {
    if (!newNoteContent.trim()) return;

    setIsSubmitting(true);
    try {
      await onAddNote(newNoteContent, currentTimestamp);
      setNewNoteContent("");
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleUpdateNote = async (noteId: string) => {
    if (!editContent.trim()) return;

    setIsSubmitting(true);
    try {
      await onUpdateNote(noteId, editContent);
      setEditingNoteId(null);
      setEditContent("");
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDelete = async (noteId: string) => {
    if (!confirm(t("lesson.deleteNote") + "?")) return;

    await onDeleteNote(noteId);
  };

  const formatTimestamp = (seconds?: number) => {
    if (seconds === undefined) return "";

    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);

    return `${mins}:${secs.toString().padStart(2, "0")}`;
  };

  return (
    <div className="h-full flex flex-col bg-gray-50">
      <div className="p-4 border-b border-gray-200">
        <h2 className="text-lg font-semibold">{t("lesson.notes")}</h2>
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {/* Add New Note */}
        <Card>
          <CardBody>
            <Textarea
              maxRows={5}
              minRows={3}
              placeholder={t("lesson.takeNote")}
              value={newNoteContent}
              onChange={(e) => setNewNoteContent(e.target.value)}
            />
            {currentTimestamp !== undefined && (
              <p className="text-xs text-gray-500 mt-2">
                {t("lesson.videoTimestamp")}:{" "}
                {formatTimestamp(currentTimestamp)}
              </p>
            )}
            <Button
              className="mt-3"
              color="primary"
              isDisabled={!newNoteContent.trim()}
              isLoading={isSubmitting}
              size="sm"
              onPress={handleAddNote}
            >
              {t("lesson.addNote")}
            </Button>
          </CardBody>
        </Card>

        {/* Existing Notes */}
        {notes.length === 0 ? (
          <p className="text-center text-gray-500 py-8">
            {t("lesson.noNotes")}
          </p>
        ) : (
          notes.map((note) => (
            <Card key={note.id}>
              <CardHeader className="flex items-start justify-between pb-2">
                <div className="flex-1">
                  {note.timestamp !== undefined && (
                    <span className="text-xs text-primary font-medium">
                      {t("lesson.noteAt")} {formatTimestamp(note.timestamp)}
                    </span>
                  )}
                  <p className="text-xs text-gray-500 mt-1">
                    {new Date(note.createdAt).toLocaleDateString()}
                  </p>
                </div>
                {editingNoteId !== note.id && (
                  <div className="flex gap-1">
                    <Button
                      isIconOnly
                      size="sm"
                      variant="light"
                      onPress={() => {
                        setEditingNoteId(note.id);
                        setEditContent(note.content);
                      }}
                    >
                      <Edit2 className="w-4 h-4" />
                    </Button>
                    <Button
                      isIconOnly
                      color="danger"
                      size="sm"
                      variant="light"
                      onPress={() => handleDelete(note.id)}
                    >
                      <Trash2 className="w-4 h-4" />
                    </Button>
                  </div>
                )}
              </CardHeader>
              <CardBody className="pt-0">
                {editingNoteId === note.id ? (
                  <>
                    <Textarea
                      maxRows={5}
                      minRows={2}
                      value={editContent}
                      onChange={(e) => setEditContent(e.target.value)}
                    />
                    <div className="flex gap-2 mt-3">
                      <Button
                        color="primary"
                        isLoading={isSubmitting}
                        size="sm"
                        startContent={<Save className="w-4 h-4" />}
                        onPress={() => handleUpdateNote(note.id)}
                      >
                        {t("lesson.saveNote")}
                      </Button>
                      <Button
                        size="sm"
                        startContent={<X className="w-4 h-4" />}
                        variant="flat"
                        onPress={() => {
                          setEditingNoteId(null);
                          setEditContent("");
                        }}
                      >
                        {t("lesson.cancel")}
                      </Button>
                    </div>
                  </>
                ) : (
                  <p className="text-sm text-gray-700 whitespace-pre-wrap">
                    {note.content}
                  </p>
                )}
              </CardBody>
            </Card>
          ))
        )}
      </div>
    </div>
  );
}
