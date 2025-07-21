import React, { useEffect, useState } from "react";
import { Card, Spin, Tabs, Image, message } from "antd";
import { getMediaList } from "../../api/upload";

const Media: React.FC = () => {
  const [media, setMedia] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    setLoading(true);
    getMediaList()
      .then((res) => {
        setMedia(res.data || []);
      })
      .catch(() => message.error("获取多媒体文件失败"))
      .finally(() => setLoading(false));
  }, []);

  const images = media.filter((m) => m.type === "image");
  const videos = media.filter((m) => m.type === "video");
  const pdfs = media.filter((m) => m.type === "pdf");

  const tabItems = [
    {
      key: "image",
      label: "图片",
      children: (
        <div style={{ display: "flex", flexWrap: "wrap", gap: 16 }}>
          {images.map((img) => (
            <Card
              key={img.filename}
              hoverable
              style={{ width: 200 }}
              cover={<Image src={img.url} alt={img.filename} style={{ height: 120, objectFit: "cover" }} />}
              actions={[
                <a href={img.url} download target="_blank" rel="noopener noreferrer">下载</a>,
              ]}
            >
              <Card.Meta title={img.filename} description={`大小: ${(img.size/1024).toFixed(1)}KB`} />
            </Card>
          ))}
        </div>
      ),
    },
    {
      key: "video",
      label: "视频",
      children: (
        <div style={{ display: "flex", flexWrap: "wrap", gap: 16 }}>
          {videos.map((vid) => (
            <Card
              key={vid.filename}
              hoverable
              style={{ width: 320 }}
              cover={
                <video src={vid.url} controls style={{ width: "100%", height: 180, objectFit: "cover" }} />
              }
              actions={[
                <a href={vid.url} download target="_blank" rel="noopener noreferrer">下载</a>,
              ]}
            >
              <Card.Meta title={vid.filename} description={`大小: ${(vid.size/1024/1024).toFixed(2)}MB`} />
            </Card>
          ))}
        </div>
      ),
    },
    {
      key: "pdf",
      label: "PDF文档",
      children: (
        <div style={{ display: "flex", flexWrap: "wrap", gap: 16 }}>
          {pdfs.map((pdf) => (
            <Card
              key={pdf.filename}
              hoverable
              style={{ width: 220 }}
              cover={
                <div style={{height:120,display:'flex',alignItems:'center',justifyContent:'center',background:'#fafafa'}}>
                  <img src="/pdf_icon.svg" alt="pdf" style={{height:60}} />
                </div>
              }
              actions={[
                <a href={pdf.url} download target="_blank" rel="noopener noreferrer">下载</a>,
                <a href={pdf.url} target="_blank" rel="noopener noreferrer">预览</a>
              ]}
            >
              <Card.Meta title={pdf.filename} description={`大小: ${(pdf.size/1024/1024).toFixed(2)}MB`} />
            </Card>
          ))}
        </div>
      ),
    },
  ];

  return (
    <div style={{ padding: 24 }}>
      <h2>多媒体文件</h2>
      <Spin spinning={loading}>
        <Tabs defaultActiveKey="image" items={tabItems} />
      </Spin>
    </div>
  );
};

export default Media; 