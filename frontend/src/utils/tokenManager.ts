/**
 * Token Manager Utility
 * Handles token storage, retrieval, and debugging
 */

export interface TokenInfo {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export class TokenManager {
  private static readonly ACCESS_TOKEN_KEY = 'access_token';
  private static readonly REFRESH_TOKEN_KEY = 'refresh_token';
  private static checkInterval: NodeJS.Timeout | null = null;
  private static readonly CHECK_INTERVAL = 60000; // 每分钟检查一次
  private static readonly REFRESH_THRESHOLD = 5 * 60 * 1000; // 提前5分钟刷新
  private static refreshTokenInterval: NodeJS.Timeout | null = null;
  private static readonly REFRESH_TOKEN_CHECK_INTERVAL = 12 * 60 * 60 * 1000; // 每12小时检查一次
  private static readonly REFRESH_TOKEN_THRESHOLD = 24 * 60 * 60 * 1000; // 剩余1天时主动刷新

  /**
   * Store tokens in localStorage
   */
  static storeTokens(tokens: TokenInfo): void {
    localStorage.setItem(this.ACCESS_TOKEN_KEY, tokens.access_token);
    localStorage.setItem(this.REFRESH_TOKEN_KEY, tokens.refresh_token);
    console.log('[TokenManager] Tokens stored:', {
      access_token: tokens.access_token.substring(0, 30) + '...',
      refresh_token: tokens.refresh_token.substring(0, 30) + '...'
    });
    this.startTokenCheck();
  }

  /**
   * Get access token from localStorage
   */
  static getAccessToken(): string | null {
    return localStorage.getItem(this.ACCESS_TOKEN_KEY);
  }

  /**
   * Get refresh token from localStorage
   */
  static getRefreshToken(): string | null {
    return localStorage.getItem(this.REFRESH_TOKEN_KEY);
  }

  /**
   * Clear all tokens from localStorage
   */
  static clearTokens(): void {
    localStorage.removeItem(this.ACCESS_TOKEN_KEY);
    localStorage.removeItem(this.REFRESH_TOKEN_KEY);
    console.log('Tokens cleared from localStorage');
    this.stopTokenCheck();
  }

  /**
   * Check if user has valid tokens
   */
  static hasTokens(): boolean {
    const accessToken = this.getAccessToken();
    const refreshToken = this.getRefreshToken();
    return !!(accessToken && refreshToken);
  }

  /**
   * Check if token is expired or will expire soon
   */
  static isTokenExpiredOrExpiringSoon(token: string, thresholdMs: number = this.REFRESH_THRESHOLD): boolean {
    try {
      const payload = this.decodeToken(token);
      const expTime = payload.exp * 1000; // Convert to milliseconds
      const currentTime = Date.now();
      return expTime - currentTime <= thresholdMs;
    } catch (e) {
      console.error('Failed to decode token:', e);
      return true;
    }
  }

  /**
   * Start automatic token checking
   */
  static startTokenCheck(): void {
    if (this.checkInterval) {
      this.stopTokenCheck();
    }
    this.checkInterval = setInterval(() => {
      this.checkAndRefreshToken();
    }, this.CHECK_INTERVAL);
    // 新增：定期主动刷新refresh token
    if (this.refreshTokenInterval) {
      clearInterval(this.refreshTokenInterval);
    }
    this.refreshTokenInterval = setInterval(() => {
      const refreshToken = this.getRefreshToken();
      if (refreshToken && this.isRefreshTokenExpiringSoon(refreshToken)) {
        console.log('[TokenManager] Refresh token expiring soon, proactive refresh...');
        this.checkAndRefreshToken();
      }
    }, this.REFRESH_TOKEN_CHECK_INTERVAL);
    console.log('Token check started');
  }

  /**
   * Stop automatic token checking
   */
  static stopTokenCheck(): void {
    if (this.checkInterval) {
      clearInterval(this.checkInterval);
      this.checkInterval = null;
      console.log('Token check stopped');
    }
    if (this.refreshTokenInterval) {
      clearInterval(this.refreshTokenInterval);
      this.refreshTokenInterval = null;
    }
  }

  /**
   * Check and refresh token if needed
   */
  static async checkAndRefreshToken(): Promise<boolean> {
    const accessToken = this.getAccessToken();
    const refreshToken = this.getRefreshToken();

    if (!accessToken || !refreshToken) {
      return false;
    }

    // Check if token is expired or will expire soon
    if (this.isTokenExpiredOrExpiringSoon(accessToken)) {
      console.log('[TokenManager] Token expired or expiring soon, attempting refresh...');
      try {
        const response = await fetch('/api/v1/auth/refresh', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ refresh_token: refreshToken }),
        });

        if (response.ok) {
          const data = await response.json();
          console.log('[TokenManager] Refresh response:', data);
          this.storeTokens(data);
          console.log('[TokenManager] Token refreshed successfully');
          return true;
        } else {
          console.log('[TokenManager] Token refresh failed, clearing tokens');
          this.clearTokens();
          window.location.href = '/login';
          return false;
        }
      } catch (error) {
        console.error('[TokenManager] Token refresh error:', error);
        this.clearTokens();
        window.location.href = '/login';
        return false;
      }
    }

    return true;
  }

  /**
   * Debug: Log current token information
   */
  static debugTokens(): void {
    const accessToken = this.getAccessToken();
    const refreshToken = this.getRefreshToken();
    
    console.log('=== Token Debug Info ===');
    console.log('Has access token:', !!accessToken);
    console.log('Has refresh token:', !!refreshToken);
    
    if (accessToken) {
      console.log('Access token (first 50 chars):', accessToken.substring(0, 50) + '...');
      try {
        const payload = this.decodeToken(accessToken);
        console.log('Access token payload:', payload);
        const expTime = payload.exp * 1000;
        const currentTime = Date.now();
        const timeLeft = expTime - currentTime;
        console.log('Token expires in:', Math.floor(timeLeft / 1000), 'seconds');
        console.log('Will refresh in:', Math.floor((timeLeft - this.REFRESH_THRESHOLD) / 1000), 'seconds');
      } catch (e) {
        console.log('Failed to decode access token:', e);
      }
    }
    
    if (refreshToken) {
      console.log('Refresh token (first 50 chars):', refreshToken.substring(0, 50) + '...');
      try {
        const payload = this.decodeToken(refreshToken);
        console.log('Refresh token payload:', payload);
      } catch (e) {
        console.log('Failed to decode refresh token:', e);
      }
    }
  }

  /**
   * Decode JWT token (without verification)
   */
  static decodeToken(token: string): any {
    try {
      const base64Url = token.split('.')[1];
      const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
      const jsonPayload = decodeURIComponent(atob(base64).split('').map(function(c) {
        return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
      }).join(''));
      return JSON.parse(jsonPayload);
    } catch (e) {
      throw new Error('Invalid token format');
    }
  }

  static isRefreshTokenExpiringSoon(token: string, thresholdMs: number = this.REFRESH_TOKEN_THRESHOLD): boolean {
    try {
      const payload = this.decodeToken(token);
      const expTime = payload.exp * 1000;
      const currentTime = Date.now();
      return expTime - currentTime <= thresholdMs;
    } catch (e) {
      return true;
    }
  }
}

// Export convenience functions
export const clearTokens = () => TokenManager.clearTokens();
export const debugTokens = () => TokenManager.debugTokens();
export const hasTokens = () => TokenManager.hasTokens(); 