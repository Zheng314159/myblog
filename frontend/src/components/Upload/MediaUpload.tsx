import React, { useRef } from "react";
import { Button, Upload, Space, App } from "antd";
import { UploadOutlined, FileImageOutlined, VideoCameraOutlined, FilePdfOutlined } from "@ant-design/icons";
import { uploadImage, uploadVideo, uploadPdf } from "../../api/upload";

interface MediaUploadProps {
  onUpload: (url: string, type: string) => void;
}

const MediaUpload: React.FC<MediaUploadProps> = ({ onUpload }) => {
  const uploading = useRef(false);
  const { message } = App.useApp();

  const handleUpload = async (file: File, type: string, uploadFn: (file: File) => Promise<any>) => {
    if (uploading.current) return;
    uploading.current = true;
    try {
      let res = await uploadFn(file);
      onUpload(res.data?.url || res.url, type);
      message.success("上传成功");
    } catch (e: any) {
      message.error(e?.message || "上传失败");
    } finally {
      uploading.current = false;
    }
  };

  const beforeUploadImage = (file: File) => {
    if (!file.type.startsWith("image/")) {
      message.error("请选择图片文件");
      return Upload.LIST_IGNORE;
    }
    if (file.size > 5 * 1024 * 1024) {
      message.error("图片不能超过5MB");
      return Upload.LIST_IGNORE;
    }
    return true;
  };

  const beforeUploadVideo = (file: File) => {
    if (!file.type.startsWith("video/")) {
      message.error("请选择视频文件");
      return Upload.LIST_IGNORE;
    }
    if (file.size > 100 * 1024 * 1024) {
      message.error("视频不能超过100MB");
      return Upload.LIST_IGNORE;
    }
    return true;
  };

  const beforeUploadPdf = (file: File) => {
    if (file.type !== "application/pdf") {
      message.error("请选择PDF文件");
      return Upload.LIST_IGNORE;
    }
    if (file.size > 20 * 1024 * 1024) {
      message.error("PDF不能超过20MB");
      return Upload.LIST_IGNORE;
    }
    return true;
  };

  return (
    <Space>
      <Upload
        showUploadList={false}
        beforeUpload={beforeUploadImage}
        customRequest={({ file, onSuccess, onError }) =>
          handleUpload(file as File, "image", uploadImage)
            .then(() => onSuccess && onSuccess({}, file))
            .catch((err) => onError && onError(err))
        }
        accept="image/*"
      >
        <Button icon={<FileImageOutlined />}>上传图片</Button>
      </Upload>
      <Upload
        showUploadList={false}
        beforeUpload={beforeUploadVideo}
        customRequest={({ file, onSuccess, onError }) =>
          handleUpload(file as File, "video", uploadVideo)
            .then(() => onSuccess && onSuccess({}, file))
            .catch((err) => onError && onError(err))
        }
        accept="video/*"
      >
        <Button icon={<VideoCameraOutlined />}>上传视频</Button>
      </Upload>
      <Upload
        showUploadList={false}
        beforeUpload={beforeUploadPdf}
        customRequest={({ file, onSuccess, onError }) =>
          handleUpload(file as File, "pdf", uploadPdf)
            .then(() => onSuccess && onSuccess({}, file))
            .catch((err) => onError && onError(err))
        }
        accept="application/pdf"
      >
        <Button icon={<FilePdfOutlined />}>上传PDF</Button>
      </Upload>
    </Space>
  );
};

export default MediaUpload; 