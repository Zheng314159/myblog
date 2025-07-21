import request from "./request";

export const getComments = (articleId: number | string) => request.get(`/articles/${articleId}/comments`);
export const addComment = (articleId: number | string, data: any) => request.post(`/articles/${articleId}/comments`, data);
export const deleteComment = (articleId: number | string, commentId: number | string) => request.delete(`/articles/${articleId}/comments/${commentId}`); 