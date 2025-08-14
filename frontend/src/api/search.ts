import request from './request.ts';

// 搜索文章
export const searchArticles = (params: {
  q?: string;
  tag?: string;
  skip?: number;
  limit?: number;
  status?: string;
}) => request.get("/search/", { params });

// 获取搜索建议
export const getSuggestions = (q: string) => 
  request.get('/search/suggestions', { params: { q } });

// 获取热门搜索
export const getPopularSearches = () => 
  request.get('/search/popular'); 