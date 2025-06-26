import instance from "./index";

export const uploadImage = (file: File) => {
  const formData = new FormData();
  formData.append("file", file);
  return instance.post("/upload/image", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
}; 