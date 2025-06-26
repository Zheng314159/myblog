import request from "./request";

export interface LoginParams {
  username: string;
  password: string;
}

export interface RegisterParams {
  username: string;
  email: string;
  password: string;
  full_name?: string;
}

export const login = (data: LoginParams) => request.post("/auth/login", data);
export const register = (data: RegisterParams) => request.post("/auth/register", data);
export const getMe = () => request.get("/auth/me");
export const refreshToken = (refresh_token: string) => request.post("/auth/refresh", { refresh_token });
export const logout = (access_token: string) => request.post("/auth/logout", { access_token }); 