import request from './request';

// 搜索文章
export const searchArticles = (q: string, params?: any) => 
  request.get('/search/', { params: { q, ...params } });

// 获取搜索建议
export const getSuggestions = (q: string) => 
  request.get('/search/suggestions', { params: { q } });

// 获取热门搜索
export const getPopularSearches = () => 
  request.get('/search/popular'); 