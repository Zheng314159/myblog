import instance from "./index";

export const searchArticles = (q: string, params?: any) => instance.get("/search", { params: { q, ...params } });
export const getSuggestions = (q: string) => instance.get("/search/suggest", { params: { q } });
export const getPopularSearches = () => instance.get("/search/popular");




////////还未实现
// 后端接口建议（FastAPI）
// /api/v1/search/：支持按关键词搜索文章、标签、用户（可选类型参数）
// 前端页面建议
// 搜索页（/search）：输入关键词，展示文章、标签、用户等综合搜索结果
// 支持高亮关键词、分页、类型筛选


import request from './request';

// 综合搜索
export const searchAll = (params: { q: string; type?: 'article' | 'tag' | 'user'; page?: number; size?: number }) =>
  request.get('/api/v1/search/', { params });