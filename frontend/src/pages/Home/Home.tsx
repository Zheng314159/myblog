import React, { useEffect, useState } from "react";
import { 
  List, 
  Tag, 
  Typography, 
  Spin, 
  Card, 
  Image, 
  message, 
  App, 
  Carousel, 
  Button, 
  Row, 
  Col, 
  Statistic 
} from "antd";
import { 
  FileTextOutlined, 
  UserOutlined, 
  PictureOutlined, 
  EyeOutlined 
} from "@ant-design/icons";
import { getArticles } from "../../api/article";
import { getMediaList } from "../../api/upload";
import { getStatistics, getConfig, getNotifications } from "../../api/config";
import { useNavigate } from "react-router-dom";
import { connectWebSocket, disconnectWebSocket } from "../../api/websocket";

const { Title, Paragraph } = Typography;

const Home: React.FC = () => {
  const [articles, setArticles] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [media, setMedia] = useState<any[]>([]);
  const [statistics, setStatistics] = useState({
    total_articles: 0,
    published_articles: 0,
    total_users: 0,
    active_users: 0,
    total_media: 0,
    total_views: 0
  });
  const [statsLoading, setStatsLoading] = useState(false);
  const [notifications, setNotifications] = useState<any[]>([]);
  const [taskStatus, setTaskStatus] = useState<any>(null);
  const [enableNotificationFetch, setEnableNotificationFetch] = useState(false);
  const navigate = useNavigate();

  const carouselItems = [
    {
      id: 1,
      title: "欢迎来到学术博客系统",
      description: "分享知识，交流思想，共同进步",
      image: "https://images.unsplash.com/photo-1481627834876-b7833e8f5570?w=800&h=400&fit=crop",
      link: "/edit/new"
    },
    {
      id: 2,
      title: "多媒体资源库",
      description: "丰富的图片、视频和文档资源",
      image: "https://images.unsplash.com/photo-1516321318423-f06f85e504b3?w=800&h=400&fit=crop",
      link: "/media"
    },
    {
      id: 3,
      title: "学术交流平台",
      description: "与同行学者深入讨论，碰撞思想火花",
      image: "https://images.unsplash.com/photo-1522202176988-66273c2fd55f?w=800&h=400&fit=crop",
      link: "/search"
    }
  ];

  useEffect(() => {
    setLoading(true);
    getArticles({ status: 'published' }).then((res) => {
      const allArticles = res.data || [];
      const adminArticles = allArticles.filter((item: any) => item.author?.role === 'ADMIN');
      setArticles(adminArticles);
      setLoading(false);
    });
    // 获取多媒体
    getMediaList()
      .then((res) => setMedia((res.data || []).filter((m: any) => m.uploader_role === 'ADMIN')))
      .catch(() => message.error("获取多媒体文件失败"));
    
    // 获取统计数据
    setStatsLoading(true);
    getStatistics()
      .then((res) => {
        setStatistics(res.data);
        setStatsLoading(false);
      })
      .catch(() => {
        message.error("获取统计数据失败");
        setStatsLoading(false);
      });

    let wsCleanup: (() => void) | undefined;

    getConfig().then(cfg => {
      const fetchEnabled = cfg && cfg.enable_notification_fetch;
      const pushEnabled = cfg && cfg.enable_notification_push;
      setEnableNotificationFetch(!!fetchEnabled);
      // 只拉取历史
      if (fetchEnabled && !pushEnabled) {
        getNotifications(5)
          .then(data => {
            if (Array.isArray(data.notifications)) {
              const normalized = data.notifications.map((n: any) => ({
                type: 'system_notification',
                data: n
              }));
              setNotifications(() => {
                const map = new Map();
                for (const n of normalized) {
                  const key = (n.data?.id?.toString().trim()) || (n.id?.toString().trim()) || (n.data?.title && n.data?.message ? n.data.title.toString().trim() + '_' + n.data.message.toString().trim() : undefined);
                  if (!key) continue;
                  if (!map.has(key)) {
                    map.set(key, n);
                  }
                }
                return Array.from(map.values()).slice(0, 5);
              });
            }
          });
        return;
      }
      // 只推送
      if (!fetchEnabled && pushEnabled) {
        const token = localStorage.getItem("access_token");
        const ws = connectWebSocket(token || undefined);
        ws.onmessage = (event) => {
          try {
            const msg = JSON.parse(event.data);
            if (msg.type && msg.type.includes("notification")) {
              setNotifications((prev) => {
                const all = [msg, ...prev];
                const map = new Map();
                for (const n of all) {
                  const key = (n.data?.id?.toString().trim()) || (n.id?.toString().trim()) || (n.data?.title && n.data?.message ? n.data.title.toString().trim() + '_' + n.data.message.toString().trim() : undefined);
                  if (!key) continue;
                  if (!map.has(key)) {
                    map.set(key, n);
                  }
                }
                return Array.from(map.values()).slice(0, 5);
              });
            } else if (msg.type === "task_status") {
              setTaskStatus(msg.data);
            }
          } catch (e) {}
        };
        wsCleanup = () => { disconnectWebSocket(); };
        return;
      }
      // 拉取+推送
      if (fetchEnabled && pushEnabled) {
        getNotifications(5)
          .then(data => {
            if (Array.isArray(data.notifications)) {
              const normalized = data.notifications.map((n: any) => ({
                type: 'system_notification',
                data: n
              }));
              setNotifications((prev) => {
                const all = [...normalized, ...prev];
                const map = new Map();
                for (const n of all) {
                  const key = (n.data?.id?.toString().trim()) || (n.id?.toString().trim()) || (n.data?.title && n.data?.message ? n.data.title.toString().trim() + '_' + n.data.message.toString().trim() : undefined);
                  if (!key) continue;
                  if (!map.has(key)) {
                    map.set(key, n);
                  }
                }
                return Array.from(map.values()).slice(0, 5);
              });
            }
          });
        const token = localStorage.getItem("access_token");
        const ws = connectWebSocket(token || undefined);
        ws.onmessage = (event) => {
          try {
            const msg = JSON.parse(event.data);
            if (msg.type && msg.type.includes("notification")) {
              setNotifications((prev) => {
                const all = [msg, ...prev];
                const map = new Map();
                for (const n of all) {
                  const key = (n.data?.id?.toString().trim()) || (n.id?.toString().trim()) || (n.data?.title && n.data?.message ? n.data.title.toString().trim() + '_' + n.data.message.toString().trim() : undefined);
                  if (!key) continue;
                  if (!map.has(key)) {
                    map.set(key, n);
                  }
                }
                return Array.from(map.values()).slice(0, 5);
              });
            } else if (msg.type === "task_status") {
              setTaskStatus(msg.data);
            }
          } catch (e) {}
        };
        wsCleanup = () => { disconnectWebSocket(); };
        return;
      }
    });
    // useEffect cleanup: 组件卸载时断开WebSocket
    return () => {
      if (wsCleanup) wsCleanup();
    };
  }, []);

  // 任务栏和通知栏 key debug
  if (taskStatus && taskStatus.jobs) {
    console.log('job keys:', taskStatus.jobs.map((job: any, idx: number) => job.id ? String(job.id) : String(job.name) + '-' + idx));
  }
  if (notifications) {
    console.log('notify keys:', notifications.map((n, idx) => n.data?.id ? String(n.data.id) : (n.id ? String(n.id) : 'notify-' + idx)));
  }

  const renderCarousel = () => (
    <Carousel autoplay style={{ marginBottom: 32 }}>
      {carouselItems.map(item => (
        <div key={item.id}>
          <div
            style={{
              height: 400,
              background: `linear-gradient(rgba(0,0,0,0.4), rgba(0,0,0,0.4)), url(${item.image})`,
              backgroundSize: 'cover',
              backgroundPosition: 'center',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: 'white',
              textAlign: 'center'
            }}
          >
            <div>
              <Title level={1} style={{ color: 'white', marginBottom: 16 }}>
                {item.title}
              </Title>
              <Paragraph style={{ color: 'white', fontSize: 18, marginBottom: 24 }}>
                {item.description}
              </Paragraph>
              <Button 
                type="primary" 
                size="large"
                onClick={() => navigate(item.link)}
              >
                了解更多
              </Button>
            </div>
          </div>
        </div>
      ))}
    </Carousel>
  );

  const renderStatistics = () => (
    <Card style={{ marginBottom: 32 }}>
      <Row gutter={16}>
        <Col span={6}>
          <Statistic
            title="总文章数"
            value={statistics.total_articles}
            prefix={<FileTextOutlined />}
            loading={statsLoading}
          />
        </Col>
        <Col span={6}>
          <Statistic
            title="活跃用户"
            value={statistics.active_users}
            prefix={<UserOutlined />}
            loading={statsLoading}
          />
        </Col>
        <Col span={6}>
          <Statistic
            title="媒体资源"
            value={statistics.total_media}
            prefix={<PictureOutlined />}
            loading={statsLoading}
          />
        </Col>
        <Col span={6}>
          <Statistic
            title="总浏览量"
            value={statistics.total_views}
            prefix={<EyeOutlined />}
            loading={statsLoading}
          />
        </Col>
      </Row>
    </Card>
  );

  return (
    <App>
      {/* 只保留数据库驱动的系统通知栏，type为system_notification，无限滚动，右到左滚动动画 */}
      {notifications.filter((n: any) => n.type === 'system_notification').length > 0 && (
        <div
          style={{
            position: "fixed",
            top: 0,
            left: 0,
            width: "100%",
            zIndex: 1000,
            background: "none",
            color: "#d46b08",
            fontWeight: "bold",
            fontSize: 18,
            textAlign: "center",
            padding: "12px 0",
            height: 48,
            boxShadow: "none",
            overflow: "hidden",
            whiteSpace: "nowrap"
          }}
        >
          <div style={{
            display: "inline-block",
            whiteSpace: "nowrap",
            animation: "marquee-notify 15s linear infinite",
            minWidth: "100%"
          }}>
            {notifications.filter((n: any) => n.type === 'system_notification').map((n, idx) => (
              <span key={
                (n.data?.id?.toString().trim()) ||
                (n.id?.toString().trim()) ||
                (n.data?.title && n.data?.message ? n.data.title.toString().trim() + '_' + n.data.message.toString().trim() : 'notify-' + idx)
              } style={{ margin: "0 16px" }}>
                <b>{n.data?.title || n.type}</b>: {n.data?.message || n.data?.content}
              </span>
            ))}
          </div>
          <style>{`
            @keyframes marquee-notify {
              0% { transform: translateX(100%); }
              100% { transform: translateX(-100%); }
            }
          `}</style>
        </div>
      )}
      <div>
        {renderCarousel()}
        {renderStatistics()}
        
        <Title level={2}>最新文章</Title>
        <Spin spinning={loading}>
          <List
            itemLayout="vertical"
            dataSource={articles}
            renderItem={item => (
              <List.Item
                key={item.id}
                onClick={() => navigate(`/article/${item.id}`)}
                style={{ cursor: "pointer" }}
                extra={item.tags && item.tags.map((tag: any) => <Tag key={typeof tag === 'string' ? tag : tag.name}>{typeof tag === 'string' ? tag : tag.name}</Tag>)}
              >
                <List.Item.Meta
                  title={item.title}
                  description={`作者: ${item.author?.username || "匿名"} | 发布时间: ${item.created_at?.slice(0, 10)}`}
                />
                <div>{item.summary || item.content?.slice(0, 120) + "..."}</div>
              </List.Item>
            )}
          />
        </Spin>
        <div style={{ marginBottom: 32 }}>
          <Title level={3}>最新多媒体</Title>
          <div style={{ display: "flex", gap: 16 }}>
            {media.filter(m => m.type === "image").slice(0,3).map(img => (
              <Card key={img.filename} hoverable style={{ width: 120 }}
                cover={<Image src={img.url} alt={img.filename} style={{ height: 80, objectFit: "cover" }} />}
                actions={[<a href={img.url} download target="_blank" rel="noopener noreferrer">下载</a>]}
              >
                <div style={{ fontSize: 12, wordBreak: 'break-all', textAlign: 'center' }} title={img.filename}>
                  <span style={{
                    display: 'inline-block',
                    maxWidth: '100%',
                    overflow: 'hidden',
                    textOverflow: 'ellipsis',
                    whiteSpace: 'nowrap',
                    verticalAlign: 'bottom'
                  }}>{img.filename}</span>
                </div>
              </Card>
            ))}
            {media.filter(m => m.type === "video").slice(0,3).map(vid => (
              <Card key={vid.filename} hoverable style={{ width: 160 }}
                cover={<video src={vid.url} controls style={{ width: "100%", height: 80, objectFit: "cover" }} />}
                actions={[<a href={vid.url} download target="_blank" rel="noopener noreferrer">下载</a>]}
              >
                <div style={{ fontSize: 12, wordBreak: 'break-all', textAlign: 'center' }} title={vid.filename}>
                  <span style={{
                    display: 'inline-block',
                    maxWidth: '100%',
                    overflow: 'hidden',
                    textOverflow: 'ellipsis',
                    whiteSpace: 'nowrap',
                    verticalAlign: 'bottom'
                  }}>{vid.filename}</span>
                </div>
              </Card>
            ))}
            {media.filter(m => m.type === "pdf").slice(0,3).map(pdf => (
              <Card key={pdf.filename} hoverable style={{ width: 120 }}
                cover={<div style={{height:80,display:'flex',alignItems:'center',justifyContent:'center',background:'#fafafa'}}>
                  <img src="/pdf_icon.svg" alt="pdf" style={{height:48}} />
                </div>}
                actions={[
                  <a href={pdf.url} download target="_blank" rel="noopener noreferrer">下载</a>,
                  <a href={pdf.url} target="_blank" rel="noopener noreferrer">预览</a>
                ]}
              >
                <div style={{ fontSize: 12, wordBreak: 'break-all', textAlign: 'center' }} title={pdf.filename}>
                  <span style={{
                    display: 'inline-block',
                    maxWidth: '100%',
                    overflow: 'hidden',
                    textOverflow: 'ellipsis',
                    whiteSpace: 'nowrap',
                    verticalAlign: 'bottom'
                  }}>{pdf.filename}</span>
                </div>
              </Card>
            ))}
          </div>
        </div>
      </div>
    </App>
  );
};

export default Home; 