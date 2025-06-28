import request from './request';

export const getTags = () => request.get('/tags/');
export const getPopularTags = () => request.get('/tags/popular');

// fastapi还未实现
// /api/v1/tag/：获取所有标签（支持分页、搜索）
// /api/v1/tag/hot：获取热门标签
// /api/v1/tag/{tag_id}：获取标签详情（含该标签下的文章列表）
// /api/v1/tag/（POST/PUT/DELETE）：标签的增删改（需管理员权限）
// 前端页面建议
// 标签云/标签列表页（/tags）：展示所有标签，支持点击跳转
// 标签详情页（/tags/:id）：展示该标签下的文章列表
// 热门标签可在首页/侧边栏展示

// 获取所有标签
export const getArgsTags = (params?: { page?: number; size?: number; search?: string }) =>
  request.get('/tags/', { params });

// 获取热门标签
export const getHotTags = () => request.get('/tags/popular');

// 获取标签详情及文章
export const getTagDetail = (tagId: number, params?: { page?: number; size?: number }) =>
  request.get(`/tags/${tagId}`, { params });

// 管理员：新增、编辑、删除标签
export const createTag = (data: { name: string; description?: string }) =>
  request.post('/tags/', data);

export const updateTag = (tagId: number, data: { name?: string; description?: string }) =>
  request.put(`/tags/${tagId}`, data);

export const deleteTag = (tagId: number) => request.delete(`/tags/${tagId}`);