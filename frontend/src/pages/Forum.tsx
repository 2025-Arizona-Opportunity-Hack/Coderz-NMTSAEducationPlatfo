import type { ForumPost } from "../types/api";

import { useState, useEffect } from "react";
import { useTranslation } from "react-i18next";
import { Helmet } from "react-helmet-async";
import { Button } from "@heroui/button";
import { Input } from "@heroui/input";
import { Select, SelectItem } from "@heroui/select";
import { Spinner } from "@heroui/spinner";
import { Pagination } from "@heroui/pagination";
import { Chip } from "@heroui/chip";
import { useDisclosure } from "@heroui/use-disclosure";
import { Plus, Search, TrendingUp, Clock } from "lucide-react";

import { forumService } from "../services/forum.service";
import { ForumPostCard } from "../components/forum/ForumPostCard";
import { CreatePostModal } from "../components/forum/CreatePostModal";

export function Forum() {
  const { t } = useTranslation();
  const [loading, setLoading] = useState(true);
  const [posts, setPosts] = useState<ForumPost[]>([]);
  const [availableTags, setAvailableTags] = useState<string[]>([]);
  const [totalPages, setTotalPages] = useState(1);
  const [currentPage, setCurrentPage] = useState(1);
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedTags, setSelectedTags] = useState<string[]>([]);
  const [sortBy, setSortBy] = useState<"recent" | "popular">("recent");
  const [error, setError] = useState<string | null>(null);
  const createModalDisclosure = useDisclosure();

  useEffect(() => {
    loadPosts();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [currentPage, sortBy, searchQuery, selectedTags]);

  useEffect(() => {
    loadTags();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const loadPosts = async () => {
    try {
      setLoading(true);
      setError(null);

      const response = await forumService.getPosts(
        currentPage,
        12,
        searchQuery || undefined,
        selectedTags.length > 0 ? selectedTags : undefined,
        sortBy,
      );

      setPosts(response.data);
      setTotalPages(response.pagination.totalPages);
    } catch (err: any) {
      setError(err.response?.data?.message || "Failed to load forum posts");
    } finally {
      setLoading(false);
    }
  };

  const loadTags = async () => {
    try {
      const tags = await forumService.getTags();

      setAvailableTags(tags);
    } catch (err) {
      console.error("Failed to load tags:", err);
    }
  };

  const handleCreatePost = async (data: {
    title: string;
    content: string;
    tags: string[];
  }) => {
    await forumService.createPost(data);
    setCurrentPage(1);
    await loadPosts();
  };

  const handleSearch = () => {
    setCurrentPage(1);
    loadPosts();
  };

  const handleTagToggle = (tag: string) => {
    setSelectedTags((prev) => {
      if (prev.includes(tag)) {
        return prev.filter((t) => t !== tag);
      }

      return [...prev, tag];
    });
    setCurrentPage(1);
  };

  if (loading && posts.length === 0) {
    return (
      <div className="flex justify-center items-center min-h-[60vh]">
        <Spinner color="primary" size="lg" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex justify-center items-center min-h-[60vh]">
        <div className="text-center">
          <p className="text-danger text-lg mb-4">{error}</p>
          <Button color="primary" onPress={loadPosts}>
            {t("common.tryAgain")}
          </Button>
        </div>
      </div>
    );
  }

  return (
    <>
      <Helmet>
        <title>
          {t("forum.title")} - {t("common.siteName")}
        </title>
        <meta content={t("forum.description")} name="description" />
      </Helmet>

      <div className="container mx-auto px-4 py-8 max-w-7xl">
        {/* Header */}
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-3xl md:text-4xl font-bold mb-2">
              {t("forum.title")}
            </h1>
            <p className="text-default-600">{t("forum.subtitle")}</p>
          </div>
          <Button
            color="primary"
            size="lg"
            startContent={<Plus className="w-5 h-5" />}
            onPress={createModalDisclosure.onOpen}
          >
            {t("forum.newPost")}
          </Button>
        </div>

        {/* Search and Filters */}
        <div className="mb-6 space-y-4">
          <div className="flex gap-3">
            <Input
              className="flex-1"
              placeholder={t("forum.searchPlaceholder")}
              startContent={<Search className="w-4 h-4 text-default-400" />}
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter") {
                  handleSearch();
                }
              }}
            />
            <Button color="primary" onPress={handleSearch}>
              {t("common.search")}
            </Button>
            <Select
              className="w-48"
              selectedKeys={[sortBy]}
              onSelectionChange={(keys) => {
                const key = Array.from(keys)[0] as "recent" | "popular";

                setSortBy(key);
              }}
            >
              <SelectItem
                key="recent"
                startContent={<Clock className="w-4 h-4" />}
              >
                {t("forum.sortRecent")}
              </SelectItem>
              <SelectItem
                key="popular"
                startContent={<TrendingUp className="w-4 h-4" />}
              >
                {t("forum.sortPopular")}
              </SelectItem>
            </Select>
          </div>

          {/* Tags Filter */}
          {availableTags.length > 0 && (
            <div>
              <p className="text-sm text-default-600 mb-2">
                {t("forum.filterByTags")}:
              </p>
              <div className="flex flex-wrap gap-2">
                {availableTags.map((tag) => (
                  <Chip
                    key={tag}
                    className="cursor-pointer"
                    color={selectedTags.includes(tag) ? "primary" : "default"}
                    variant="flat"
                    onClick={() => handleTagToggle(tag)}
                  >
                    {tag}
                  </Chip>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Posts Grid */}
        <div>
          {loading ? (
            <div className="flex justify-center py-12">
              <Spinner color="primary" size="lg" />
            </div>
          ) : posts.length === 0 ? (
            <div className="text-center py-12">
              <h3 className="text-xl font-semibold mb-2">
                {t("forum.noPosts")}
              </h3>
              <p className="text-default-600 mb-4">
                {t("forum.noPostsDescription")}
              </p>
              <Button
                color="primary"
                startContent={<Plus className="w-5 h-5" />}
                onPress={createModalDisclosure.onOpen}
              >
                {t("forum.newPost")}
              </Button>
            </div>
          ) : (
            <>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {posts.map((post) => (
                  <ForumPostCard key={post.id} post={post} />
                ))}
              </div>

              {/* Pagination */}
              {totalPages > 1 && (
                <div className="flex justify-center mt-8">
                  <Pagination
                    showControls
                    color="primary"
                    page={currentPage}
                    total={totalPages}
                    onChange={setCurrentPage}
                  />
                </div>
              )}
            </>
          )}
        </div>
      </div>

      {/* Create Post Modal */}
      <CreatePostModal
        availableTags={availableTags}
        isOpen={createModalDisclosure.isOpen}
        onClose={createModalDisclosure.onClose}
        onSubmit={handleCreatePost}
      />
    </>
  );
}
