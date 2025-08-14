import { useState, useEffect } from "react";
import { Tag, Input } from "antd";
import { useNavigate, useSearchParams } from "react-router-dom";

interface TagItem {
  name: string;
}

export default function HotTags({ tags }: { tags: (string | TagItem)[] }) {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const currentQ = searchParams.get("q") || "";
  const currentTag = searchParams.get("tag") || "";

  const [searchTerm, setSearchTerm] = useState(currentQ);
  const [selectedTag, setSelectedTag] = useState<string | null>(
    currentTag || null
  );

  useEffect(() => {
    setSearchTerm(currentQ);
    setSelectedTag(currentTag || null);
  }, [currentQ, currentTag]);

  const handleTagClick = (tagName: string) => {
    const newTag = selectedTag === tagName ? null : tagName; // 再次点击取消
    setSelectedTag(newTag);

    const params = new URLSearchParams();
    if (searchTerm) params.set("q", searchTerm);
    if (newTag) params.set("tag", newTag);
    navigate(`/search?${params.toString()}`);
  };

  const handleSearch = (value: string) => {
    setSearchTerm(value);
    const params = new URLSearchParams();
    if (value) params.set("q", value);
    if (selectedTag) params.set("tag", selectedTag);
    navigate(`/search?${params.toString()}`);
  };

  return (
    <div>
      <Input.Search
        placeholder="搜索文章"
        enterButton
        onSearch={handleSearch}
        style={{ maxWidth: 400, marginBottom: 24 }}
        value={searchTerm}
        onChange={(e) => setSearchTerm(e.target.value)}
        // defaultValue={query}
      />
      <div style={{ marginBottom: 16 }}>
        热门标签：
        {tags.map((tag) => {
          const tagName = typeof tag === "string" ? tag : tag.name;
          return (
            <Tag
              key={tagName}
              color={selectedTag === tagName ? "red" : "blue"}
              style={{ cursor: "pointer" }}
              onClick={() => handleTagClick(tagName)}
            >
              {tagName}
            </Tag>
          );
        })}
      </div>
    </div>
  );
}
