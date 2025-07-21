import request from "./request";

export const uploadImage = (file: File) => {
  const formData = new FormData();
  formData.append("file", file);
  return request.post("/articles/upload-image", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
};

export const uploadVideo = (file: File) => {
  const formData = new FormData();
  formData.append("file", file);
  return request.post("/articles/upload-video", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
};

export const uploadPdf = (file: File) => {
  const formData = new FormData();
  formData.append("file", file);
  return request.post("/articles/upload-pdf", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
};

export const getMediaList = () => {
  return request.get("/articles/media/list");
};

export const getPdf = (filename: string) => {
  return request.get(`/pdfs/${filename}`);
};

export const getUserMediaList = (uploader_id: number) => {
  return request.get(`/articles/media/list?uploader_id=${uploader_id}`);
};

export const getAdminUserId = async () => {
  // 假设有 /users?role=ADMIN 接口，返回管理员用户列表
  const res = await request.get('/users?role=ADMIN');
  const admins = res.data || [];
  return admins.length > 0 ? admins[0].id : null;
};

export const getAdminMediaList = async () => {
  const adminId = await getAdminUserId();
  if (!adminId) return [];
  const res = await getUserMediaList(adminId);
  return res.data || [];
};

export const deleteMedia = (id: number | string) => {
  return request.delete(`/articles/media/${id}`);
}; 