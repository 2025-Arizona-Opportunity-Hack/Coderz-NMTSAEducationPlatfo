import type { ForumPost } from "../../types/api";

import { Card, CardBody, CardFooter, CardHeader } from "@heroui/card";
import { Avatar } from "@heroui/avatar";
import { Chip } from "@heroui/chip";
import { useTranslation } from "react-i18next";
import { useNavigate } from "react-router-dom";
import { MessageCircle, ThumbsUp, Pin, Calendar } from "lucide-react";

interface ForumPostCardProps {
  post: ForumPost;
}

export function ForumPostCard({ post }: ForumPostCardProps) {
  const { t } = useTranslation();
  const navigate = useNavigate();

  const formatDate = (date: string) => {
    const postDate = new Date(date);
    const now = new Date();
    const diffInHours = Math.floor(
      (now.getTime() - postDate.getTime()) / (1000 * 60 * 60),
    );

    if (diffInHours < 1) {
      return t("forum.justNow");
    } else if (diffInHours < 24) {
      return t("forum.hoursAgo", { count: diffInHours });
    } else if (diffInHours < 48) {
      return t("forum.yesterday");
    } else {
      return postDate.toLocaleDateString(undefined, {
        day: "numeric",
        month: "short",
        year: "numeric",
      });
    }
  };

  const getRoleBadgeColor = (role: string) => {
    switch (role) {
      case "instructor":
        return "primary";
      case "admin":
        return "danger";
      default:
        return "default";
    }
  };

  return (
    <Card
      isPressable
      className="w-full hover:shadow-lg transition-shadow cursor-pointer"
      onPress={() => navigate(`/forum/${post.id}`)}
    >
      <CardHeader className="flex gap-3 pb-2">
        <Avatar
          className="flex-shrink-0"
          name={post.author.fullName}
          size="md"
          src={post.author.avatarUrl}
        />
        <div className="flex flex-col flex-1">
          <div className="flex items-center gap-2 flex-wrap">
            <p className="font-semibold">{post.author.fullName}</p>
            {post.author.role !== "student" && (
              <Chip
                color={getRoleBadgeColor(post.author.role)}
                size="sm"
                variant="flat"
              >
                {t(`forum.roles.${post.author.role}`)}
              </Chip>
            )}
          </div>
          <div className="flex items-center gap-2 text-xs text-default-500">
            <Calendar className="w-3 h-3" />
            <span>{formatDate(post.createdAt)}</span>
          </div>
        </div>
        {post.isPinned && (
          <Pin className="w-5 h-5 text-warning flex-shrink-0" />
        )}
      </CardHeader>

      <CardBody className="py-3">
        <div className="space-y-2">
          <h3 className="text-lg font-semibold line-clamp-2">{post.title}</h3>
          <p className="text-default-600 text-sm line-clamp-3">
            {post.excerpt}
          </p>

          {/* Tags */}
          {post.tags.length > 0 && (
            <div className="flex flex-wrap gap-2 mt-3">
              {post.tags.map((tag, index) => (
                <Chip key={index} color="default" size="sm" variant="flat">
                  {tag}
                </Chip>
              ))}
            </div>
          )}
        </div>
      </CardBody>

      <CardFooter className="pt-0 gap-4">
        <div className="flex items-center gap-1 text-default-600">
          <ThumbsUp className="w-4 h-4" />
          <span className="text-sm">{post.likes}</span>
        </div>
        <div className="flex items-center gap-1 text-default-600">
          <MessageCircle className="w-4 h-4" />
          <span className="text-sm">{post.commentsCount}</span>
        </div>
      </CardFooter>
    </Card>
  );
}
