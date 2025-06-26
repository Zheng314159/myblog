import React, { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { Card, Form, Input, Button, Select, message, Spin } from "antd";
import { createArticle, getArticle, updateArticle } from "../../api/article";
import MarkdownEditor from "../../components/MarkdownEditor/MarkdownEditor";
import { getTags } from "../../api/tag";

const { Option } = Select;

const ArticleEdit: React.FC = () => {
  const { id } = useParams();
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [tags, setTags] = useState<string[]>([]);
  const [content, setContent] = useState("");
  const navigate = useNavigate();

  useEffect(() => {
    getTags().then((res) => setTags(res.tags || res.data || []));
    if (id) {
      setLoading(true);
      getArticle(id).then((res) => {
        const data = res.data || res;
        form.setFieldsValue(data);
        setContent(data.content || "");
        setLoading(false);
      });
    }
  }, [id, form]);

  const onFinish = async (values: any) => {
    setLoading(true);
    try {
      if (id) {
        await updateArticle(id, { ...values, content });
        message.success("文章更新成功");
      } else {
        const res = await createArticle({ ...values, content });
        message.success("文章发布成功");
        navigate(`/article/${res.id || res.data?.id}`);
      }
    } catch (e: any) {
      message.error(e.message || "操作失败");
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card title={id ? "编辑文章" : "发布新文章"}>
      <Spin spinning={loading}>
        <Form form={form} layout="vertical" onFinish={onFinish}>
          <Form.Item name="title" label="标题" rules={[{ required: true }]}>
            <Input />
          </Form.Item>
          <Form.Item name="tags" label="标签">
            <Select mode="tags" style={{ width: "100%" }}>
              {tags.map((tag) => (
                <Option key={tag} value={tag}>
                  {tag}
                </Option>
              ))}
            </Select>
          </Form.Item>
          <Form.Item label="正文" required>
            <MarkdownEditor value={content} onChange={setContent} />
          </Form.Item>
          <Form.Item>
            <Button type="primary" htmlType="submit" loading={loading}>
              {id ? "保存修改" : "发布文章"}
            </Button>
          </Form.Item>
        </Form>
      </Spin>
    </Card>
  );
};

export default ArticleEdit;