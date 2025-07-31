import request from "./request.ts";


export interface CreateCommentPayload {
  content: string;
  parent_id?: number | null; 
}

export const getComments = (articleId: number | string) => request.get(`/articles/${articleId}/comments`);
export const addComment = (articleId: number | string, data: CreateCommentPayload) => request.post(`/articles/${articleId}/comments`, data);
export const deleteComment = (articleId: number | string, commentId: number | string) => request.delete(`/articles/${articleId}/comments/${commentId}`); 