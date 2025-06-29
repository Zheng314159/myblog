import request from "./request";
import { TokenManager } from "../utils/tokenManager";

export interface LoginParams {
  username: string;
  password: string;
}

export interface RegisterParams {
  username: string;
  email: string;
  password: string;
  full_name?: string;
  verification_code?: string;  // Email verification code
}

export interface ChangePasswordParams {
  current_password: string;
  new_password: string;
  verification_code?: string;  // Email verification code
}

export const login = async (data: LoginParams) => {
  const response = await request.post("/auth/login", data);
  if (response.data) {
    TokenManager.storeTokens(response.data);
  }
  return response;
};

export const register = async (data: RegisterParams) => {
  const response = await request.post("/auth/register", data);
  if (response.data) {
    TokenManager.storeTokens(response.data);
  }
  return response;
};

export const getMe = () => request.get("/auth/me");

export const changePassword = async (data: ChangePasswordParams) => {
  return request.post("/auth/change-password", data);
};

export const sendChangePasswordCode = async () => {
  return request.post("/auth/send-change-password-code");
};

export const refreshToken = async (refresh_token: string) => {
  const response = await request.post("/auth/refresh", { refresh_token });
  if (response.data) {
    TokenManager.storeTokens(response.data);
  }
  return response;
};

export const logout = async (access_token: string) => {
  const response = await request.post("/auth/logout", { access_token });
  TokenManager.clearTokens();
  return response;
}; 