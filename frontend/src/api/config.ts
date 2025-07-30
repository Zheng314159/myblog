import request from './request.ts';

export const getStatistics = async () => {
  const response = await request.get("/config/statistics");
  return response;
};

export const getHealth = async () => {
  const response = await request.get("/config/health");
  return response;
};

export const getConfig = async () => {
  const response = await request.get("/config/");
  return response.data;
};

export const getNotifications = async (limit = 5) => {
  const response = await request.get(`/config/notifications?limit=${limit}`);
  return response.data;
}; 