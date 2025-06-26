// API基础配置
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

// 请求工具函数
const request = async (endpoint, options = {}) => {
  const url = `${API_BASE_URL}${endpoint}`;
  const config = {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    ...options,
  };

  try {
    const response = await fetch(url, config);
    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.message || `HTTP error! status: ${response.status}`);
    }

    return data;
  } catch (error) {
    console.error('API request failed:', error);
    throw error;
  }
};

// 认证相关API
export const authAPI = {
  // 用户注册
  register: (userData) => request('/auth/register', {
    method: 'POST',
    body: JSON.stringify(userData),
  }),

  // 用户登录
  login: (credentials) => request('/auth/login', {
    method: 'POST',
    body: JSON.stringify(credentials),
  }),

  // 刷新Token
  refreshToken: (refreshToken) => request('/auth/refresh', {
    method: 'POST',
    body: JSON.stringify({ refresh_token: refreshToken }),
  }),

  // 用户登出
  logout: (accessToken) => request('/auth/logout', {
    method: 'POST',
    body: JSON.stringify({ access_token: accessToken }),
  }),

  // 忘记密码
  forgotPassword: (email) => request('/auth/forgot-password', {
    method: 'POST',
    body: JSON.stringify({ email }),
  }),

  // 重置密码
  resetPassword: (token, newPassword) => request('/auth/reset-password', {
    method: 'POST',
    body: JSON.stringify({ token, new_password: newPassword }),
  }),
};

// OAuth相关API
export const oauthAPI = {
  // 获取可用的OAuth提供商
  getProviders: () => request('/oauth/providers'),

  // 获取用户的OAuth账户
  getAccounts: () => request('/oauth/accounts'),

  // GitHub OAuth登录
  githubLogin: () => {
    window.location.href = `${API_BASE_URL}/oauth/github/login`;
  },

  // Google OAuth登录
  googleLogin: () => {
    window.location.href = `${API_BASE_URL}/oauth/google/login`;
  },

  // 绑定OAuth账户
  bindAccount: (provider) => request(`/oauth/bind/${provider}`),

  // 解绑OAuth账户
  unbindAccount: (provider) => request(`/oauth/unbind/${provider}`),

  // 处理OAuth回调
  handleCallback: () => {
    const urlParams = new URLSearchParams(window.location.search);
    const accessToken = urlParams.get('access_token');
    const refreshToken = urlParams.get('refresh_token');
    const tokenType = urlParams.get('token_type');

    if (accessToken && refreshToken) {
      // 存储token
      localStorage.setItem('access_token', accessToken);
      localStorage.setItem('refresh_token', refreshToken);
      localStorage.setItem('token_type', tokenType || 'bearer');

      // 清除URL参数
      window.history.replaceState({}, document.title, window.location.pathname);

      return {
        success: true,
        accessToken,
        refreshToken,
        tokenType: tokenType || 'bearer'
      };
    }

    return { success: false };
  },
};

// 文章相关API
export const articleAPI = {
  // 获取文章列表
  getArticles: (params = {}) => {
    const queryString = new URLSearchParams(params).toString();
    return request(`/articles?${queryString}`);
  },

  // 获取单篇文章
  getArticle: (id) => request(`/articles/${id}`),

  // 创建文章
  createArticle: (articleData) => request('/articles', {
    method: 'POST',
    body: JSON.stringify(articleData),
  }),

  // 更新文章
  updateArticle: (id, articleData) => request(`/articles/${id}`, {
    method: 'PUT',
    body: JSON.stringify(articleData),
  }),

  // 删除文章
  deleteArticle: (id) => request(`/articles/${id}`, {
    method: 'DELETE',
  }),

  // 上传文件
  uploadFile: (file) => {
    const formData = new FormData();
    formData.append('file', file);

    return request('/articles/upload', {
      method: 'POST',
      body: formData,
    });
  },

  // 获取LaTeX渲染
  getLatexRender: (latex) => request('/articles/latex/render', {
    method: 'POST',
    body: JSON.stringify({ latex }),
  }),

  // 获取文章评论
  getComments: (articleId, params = {}) => {
    const queryParams = new URLSearchParams(params).toString();
    return request(`/articles/${articleId}/comments?${queryParams}`);
  },

  // 创建评论
  createComment: (articleId, commentData) => request(`/articles/${articleId}/comments`, {
    method: 'POST',
    body: JSON.stringify(commentData),
  }),

  // 删除评论
  deleteComment: (commentId) => request(`/articles/comments/${commentId}`, {
    method: 'DELETE',
  }),
};

// 标签相关API
export const tagAPI = {
  // 获取标签列表
  getTags: () => request('/tags'),

  // 获取标签详情
  getTag: (id) => request(`/tags/${id}`),

  // 创建标签（管理员）
  createTag: (tagData) => request('/tags', {
    method: 'POST',
    body: JSON.stringify(tagData),
  }),

  // 更新标签（管理员）
  updateTag: (id, tagData) => request(`/tags/${id}`, {
    method: 'PUT',
    body: JSON.stringify(tagData),
  }),

  // 删除标签（管理员）
  deleteTag: (id) => request(`/tags/${id}`, {
    method: 'DELETE',
  }),

  // 获取热门标签
  getPopularTags: (limit = 10) => request(`/tags/popular?limit=${limit}`),
};

// WebSocket相关
export const websocketAPI = {
  // 获取WebSocket状态
  getStatus: () => request('/ws/status'),

  // 广播消息（管理员）
  broadcast: (message, channel = null) => request('/ws/broadcast', {
    method: 'POST',
    body: JSON.stringify({ message, channel }),
  }),
};

// 工具函数
export const apiUtils = {
  // 获取图片URL
  getImageUrl: (filename) => `${API_BASE_URL}/articles/images/${filename}`,

  // 检查Token是否过期
  isTokenExpired: (token) => {
    if (!token) return true;
    
    try {
      const payload = JSON.parse(atob(token.split('.')[1]));
      return payload.exp * 1000 < Date.now();
    } catch {
      return true;
    }
  },

  // 自动刷新Token
  refreshTokenIfNeeded: async () => {
    const accessToken = localStorage.getItem('access_token');
    const refreshToken = localStorage.getItem('refresh_token');
    
    if (!accessToken || !refreshToken) {
      return false;
    }
    
    if (apiUtils.isTokenExpired(accessToken)) {
      try {
        const response = await authAPI.refreshToken(refreshToken);
        localStorage.setItem('access_token', response.access_token);
        localStorage.setItem('refresh_token', response.refresh_token);
        return true;
      } catch (error) {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        return false;
      }
    }
    
    return true;
  },

  // 清除认证信息
  clearAuth: () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('token_type');
  },
};

// WebSocket连接管理
export class WebSocketManager {
  constructor() {
    this.ws = null;
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
    this.reconnectDelay = 1000;
    this.messageHandlers = new Map();
  }

  // 连接WebSocket
  connect(token) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      return;
    }

    this.ws = new WebSocket(`ws://127.0.0.1:8000/api/v1/ws`);
    
    this.ws.onopen = () => {
      console.log('WebSocket connected');
      this.reconnectAttempts = 0;
      
      // 发送认证消息
      this.ws.send(JSON.stringify({ token }));
    };

    this.ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        this.handleMessage(data);
      } catch (error) {
        console.error('Failed to parse WebSocket message:', error);
      }
    };

    this.ws.onclose = () => {
      console.log('WebSocket disconnected');
      this.attemptReconnect();
    };

    this.ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };
  }

  // 尝试重连
  attemptReconnect() {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      setTimeout(() => {
        const token = localStorage.getItem('access_token');
        if (token) {
          this.connect(token);
        }
      }, this.reconnectDelay * this.reconnectAttempts);
    }
  }

  // 断开连接
  disconnect() {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }

  // 发送消息
  send(message) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(message));
    }
  }

  // 订阅频道
  subscribe(channel) {
    this.send({
      type: 'subscribe',
      data: { channel }
    });
  }

  // 取消订阅频道
  unsubscribe(channel) {
    this.send({
      type: 'unsubscribe',
      data: { channel }
    });
  }

  // 添加消息处理器
  onMessage(type, handler) {
    this.messageHandlers.set(type, handler);
  }

  // 移除消息处理器
  offMessage(type) {
    this.messageHandlers.delete(type);
  }

  // 处理接收到的消息
  handleMessage(data) {
    const { type } = data;
    const handler = this.messageHandlers.get(type);
    
    if (handler) {
      handler(data);
    } else {
      console.log('Unhandled WebSocket message:', data);
    }
  }

  // 心跳检测
  startHeartbeat() {
    this.heartbeatInterval = setInterval(() => {
      this.send({
        type: 'ping',
        data: { timestamp: Date.now() }
      });
    }, 30000); // 30秒发送一次心跳
  }

  // 停止心跳检测
  stopHeartbeat() {
    if (this.heartbeatInterval) {
      clearInterval(this.heartbeatInterval);
      this.heartbeatInterval = null;
    }
  }
}

// 创建全局WebSocket管理器实例
export const wsManager = new WebSocketManager();

export default {
  auth: authAPI,
  articles: articleAPI,
  tags: tagAPI,
  websocket: websocketAPI,
  utils: apiUtils,
  wsManager,
}; 