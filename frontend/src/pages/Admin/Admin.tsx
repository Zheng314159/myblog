import React, { useEffect, useState } from "react";
import { Card, List, Typography, Spin, message } from "antd";

const { Title } = Typography;

const Admin: React.FC = () => {
  const [tables, setTables] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchTables = async () => {
      try {
        const res = await fetch("/api/v1/config/tables");
        if (!res.ok) throw new Error("获取表失败");
        const data = await res.json();
        setTables(data.tables || []);
      } catch (e: any) {
        message.error(e.message || "获取数据库表失败");
      } finally {
        setLoading(false);
      }
    };
    fetchTables();
  }, []);

  return (
    <div style={{ maxWidth: 600, margin: "0 auto", padding: 32 }}>
      <Title level={3}>管理后台</Title>
      <Card title="所有数据库表">
        {loading ? (
          <Spin />
        ) : (
          <List
            dataSource={tables}
            renderItem={item => <List.Item>{item}</List.Item>}
            bordered
          />
        )}
      </Card>
    </div>
  );
};

export default Admin; 