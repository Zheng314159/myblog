import request from "./request";

export const getArticles = (params?: any) => request.get("/articles/", { params });
export const getArticle = (id: number | string) => request.get(`/articles/${id}`);
export const createArticle = (data: any) => request.post("/articles/", data);
export const updateArticle = (id: number | string, data: any) => request.put(`/articles/${id}`, data);
export const deleteArticle = (id: number | string) => request.delete(`/articles/${id}`); 