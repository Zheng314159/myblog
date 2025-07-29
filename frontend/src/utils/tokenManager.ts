// src/utils/tokenManager.ts
import axios from "axios";
import { showSessionExpiredModal } from "./showSessionExpiredModal";
import {showTokenRefreshToast} from "./showTokenRefreshToast";

export interface TokenInfo {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export class TokenManager {
  private static readonly ACCESS_TOKEN_KEY = "access_token";
  private static readonly REFRESH_TOKEN_KEY = "refresh_token";
  private static checkInterval: NodeJS.Timeout | null = null;
  private static refreshTokenInterval: NodeJS.Timeout | null = null;
  private static readonly CHECK_INTERVAL = 60 * 1000; // 每分钟检查
  private static readonly REFRESH_THRESHOLD = 5 * 60 * 1000; // 5分钟内过期就刷新
  private static readonly REFRESH_TOKEN_CHECK_INTERVAL = 12 * 60 * 60 * 1000; // 每12小时检查
  private static readonly REFRESH_TOKEN_THRESHOLD = 24 * 60 * 60 * 1000; // 剩余1天主动刷新

  static storeTokens(tokens: TokenInfo): void {
    localStorage.setItem(this.ACCESS_TOKEN_KEY, tokens.access_token);
    localStorage.setItem(this.REFRESH_TOKEN_KEY, tokens.refresh_token);
    this.startTokenCheck();
  }

  static getAccessToken(): string | null {
    return localStorage.getItem(this.ACCESS_TOKEN_KEY);
  }

  static getRefreshToken(): string | null {
    return localStorage.getItem(this.REFRESH_TOKEN_KEY);
  }

  static clearTokens(): void {
    localStorage.removeItem(this.ACCESS_TOKEN_KEY);
    localStorage.removeItem(this.REFRESH_TOKEN_KEY);
    this.stopTokenCheck();
  }

  static hasTokens(): boolean {
    return !!(this.getAccessToken() && this.getRefreshToken());
  }

  static decodeToken(token: string): any {
    const base64Url = token.split(".")[1];
    const base64 = base64Url.replace(/-/g, "+").replace(/_/g, "/");
    const jsonPayload = decodeURIComponent(
      atob(base64)
        .split("")
        .map((c) => "%" + ("00" + c.charCodeAt(0).toString(16)).slice(-2))
        .join("")
    );
    return JSON.parse(jsonPayload);
  }

  static isAccessTokenExpiringSoon(
    token: string,
    thresholdMs: number = this.REFRESH_THRESHOLD
  ): boolean {
    try {
      const payload = this.decodeToken(token);
      return payload.exp * 1000 - Date.now() <= thresholdMs;
    } catch {
      return true;
    }
  }

  static isRefreshTokenExpiringSoon(
    token: string,
    thresholdMs: number = this.REFRESH_TOKEN_THRESHOLD
  ): boolean {
    try {
      const payload = this.decodeToken(token);
      return payload.exp * 1000 - Date.now() <= thresholdMs;
    } catch {
      return true;
    }
  }

  static async refreshTokens(): Promise<string> {
    const refreshToken = this.getRefreshToken();
    if (!refreshToken) throw new Error("No refresh token available");

    try {
      const res = await axios.post("/api/v1/auth/refresh", {
        refresh_token: refreshToken,
      });
      const data = res.data;
      this.storeTokens(data);
      showTokenRefreshToast(); // 使用节流提示函数
      return data.access_token;
    } catch (error) {
      this.clearTokens();
      showSessionExpiredModal();
      throw error;
    }
  }

  /**
   * 启动定时检查，定期刷新 token
   */

  static startTokenCheck(): void {
    this.stopTokenCheck();
    const accessToken = this.getAccessToken();
    const refreshToken = this.getRefreshToken();
    if (!accessToken || !refreshToken) return;
    this.checkInterval = setInterval(() => {
      if (this.isAccessTokenExpiringSoon(accessToken)) {
        this.refreshTokens();
      }
    }, this.CHECK_INTERVAL);
    this.refreshTokenInterval = setInterval(() => {
      if (this.isRefreshTokenExpiringSoon(refreshToken)) {
        this.refreshTokens();
      }
    }, this.REFRESH_TOKEN_CHECK_INTERVAL);
  }

  static stopTokenCheck(): void {
    if (this.checkInterval) clearInterval(this.checkInterval);
    if (this.refreshTokenInterval) clearInterval(this.refreshTokenInterval);
    this.checkInterval = null;
    this.refreshTokenInterval = null;
  }

  /**
   * Debug: Log current token information
   */
  static debugTokens(): void {
    const accessToken = this.getAccessToken();
    const refreshToken = this.getRefreshToken();

    console.log("=== Token Debug Info ===");
    console.log("Has access token:", !!accessToken);
    console.log("Has refresh token:", !!refreshToken);

    if (accessToken) {
      console.log(
        "Access token (first 50 chars):",
        accessToken.substring(0, 50) + "..."
      );
      try {
        const payload = this.decodeToken(accessToken);
        console.log("Access token payload:", payload);
        const expTime = payload.exp * 1000;
        const currentTime = Date.now();
        const timeLeft = expTime - currentTime;
        console.log(
          "Token expires in:",
          Math.floor(timeLeft / 1000),
          "seconds"
        );
        console.log(
          "Will refresh in:",
          Math.floor((timeLeft - this.REFRESH_THRESHOLD) / 1000),
          "seconds"
        );
      } catch (e) {
        console.log("Failed to decode access token:", e);
      }
    }

    if (refreshToken) {
      console.log(
        "Refresh token (first 50 chars):",
        refreshToken.substring(0, 50) + "..."
      );
      try {
        const payload = this.decodeToken(refreshToken);
        console.log("Refresh token payload:", payload);
      } catch (e) {
        console.log("Failed to decode refresh token:", e);
      }
    }
  }
}



export const clearTokens = () => TokenManager.clearTokens();
export const hasTokens = () => TokenManager.hasTokens();
export const debugTokens= () => TokenManager.debugTokens();

