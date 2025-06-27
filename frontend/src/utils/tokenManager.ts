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

  /**
   * Store tokens in localStorage
   */
  static storeTokens(tokens: TokenInfo): void {
    localStorage.setItem(this.ACCESS_TOKEN_KEY, tokens.access_token);
    localStorage.setItem(this.REFRESH_TOKEN_KEY, tokens.refresh_token);
    console.log('Tokens stored successfully');
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
}

// Export convenience functions
export const clearTokens = () => TokenManager.clearTokens();
export const debugTokens = () => TokenManager.debugTokens();
export const hasTokens = () => TokenManager.hasTokens(); 