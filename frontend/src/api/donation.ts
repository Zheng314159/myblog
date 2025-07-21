import request from './request';

// 捐赠配置接口
export interface DonationConfig {
  id: number;
  is_enabled: boolean;
  title: string;
  description: string;
  alipay_enabled: boolean;
  wechat_enabled: boolean;
  paypal_enabled: boolean;
  alipay_app_id: string;
  alipay_app_private_key_path: string;
  alipay_public_key_path: string;
  alipay_notify_url: string;
  alipay_return_url: string;
  alipay_gateway: string;
  alipay_qr_base: string;
  wechat_appid: string;
  wechat_mchid: string;
  wechat_api_v3_key: string;
  wechat_private_key_path: string;
  wechat_cert_serial_no: string;
  wechat_notify_url: string;
  wechat_platform_cert_path: string;
  wechat_pay_type: string;
  wechat_qr_base: string;
  paypal_client_id: string;
  paypal_client_secret: string;
  paypal_api_base: string;
  paypal_return_url: string;
  paypal_cancel_url: string;
  paypal_currency: string;
  paypal_qr_base: string;
  bank_transfer_enabled: boolean;
  crypto_enabled: boolean;
  preset_amounts: string;
  created_at: string;
  updated_at: string;
}

// 捐赠记录接口
export interface DonationRecord {
  id: number;
  donor_name: string;
  donor_email?: string;
  donor_message?: string;
  is_anonymous: boolean;
  amount: number;
  currency: string;
  payment_method: 'ALIPAY' | 'WECHAT' | 'PAYPAL';
  payment_status: 'PENDING' | 'SUCCESS' | 'FAILED' | 'CANCELLED';
  transaction_id?: string;
  user_id?: number;
  created_at: string;
  updated_at: string;
  paid_at?: string;
  alipay_form_html?: string;
  alipay_qr?: string;
  wechat_qr?: string;
  wechat_prepay_id?: string;
  wechat_trade_type?: string;
  wechat_error?: string;
  paypal_url?: string;
  paypal_order_id?: string;
  paypal_error?: string;
}

// 捐赠目标接口
export interface DonationGoal {
  id: number;
  title: string;
  description: string;
  target_amount: number;
  current_amount: number;
  currency: string;
  start_date: string;
  end_date?: string;
  is_active: boolean;
  is_completed: boolean;
  progress_percentage: number;
  created_at: string;
  updated_at: string;
}

// 捐赠统计接口
export interface DonationStats {
  total_donations: number;
  total_amount: number;
  currency: string;
  monthly_donations: number;
  monthly_amount: number;
  active_goals: number;
  completed_goals: number;
}

// 创建捐赠请求接口
export interface CreateDonationRequest {
  donor_name: string;
  donor_email?: string;
  donor_message?: string;
  is_anonymous: boolean;
  amount: number;
  currency: string;
  payment_method: 'ALIPAY' | 'WECHAT' | 'PAYPAL';
}

// 捐赠配置API
export const getDonationConfig = () => {
  return request.get<DonationConfig>('/donation/config');
};

export const updateDonationConfig = (config: Partial<DonationConfig>) => {
  return request.put<DonationConfig>('/donation/config', config);
};

// 捐赠记录API
export const createDonation = (data: CreateDonationRequest) => {
  return request.post<DonationRecord>('/donation/create', data);
};

export const getDonationRecords = (params?: {
  skip?: number;
  limit?: number;
  status_filter?: string;
}) => {
  return request.get<DonationRecord[]>('/donation/records', { params });
};

export const getMyDonationRecords = () => {
  return request.get<DonationRecord[]>('/donation/records/my');
};

export const updateDonationStatus = (
  donationId: number,
  status: string,
  transactionId?: string
) => {
  return request.put(`/donation/records/${donationId}/status`, {
    status,
    transaction_id: transactionId,
  });
};

// 捐赠目标API
export const getDonationGoals = (activeOnly: boolean = true) => {
  return request.get<DonationGoal[]>('/donation/goals', {
    params: { active_only: activeOnly },
  });
};

export const createDonationGoal = (data: {
  title: string;
  description: string;
  target_amount: number;
  currency: string;
  start_date: string;
  end_date?: string;
}) => {
  return request.post<DonationGoal>('/donation/goals', data);
};

export const updateDonationGoal = (
  goalId: number,
  data: Partial<DonationGoal>
) => {
  return request.put<DonationGoal>(`/donation/goals/${goalId}`, data);
};

export const deleteDonationGoal = (goalId: number) => {
  return request.delete(`/donation/goals/${goalId}`);
};

// 捐赠统计API
export const getDonationStats = () => {
  return request.get<DonationStats>('/donation/stats');
};

export const getPublicDonationStats = () => {
  return request.get<{
    total_donations: number;
    total_amount: number;
    currency: string;
    active_goals: number;
  }>('/donation/public-stats');
};

export async function getPaymentMethods() {
  return request.get('/donation/payment_methods');
}

// 公开捐赠榜单API（如后端未实现可用getDonationRecords的前10条作为临时方案）
export async function getPublicDonationRecords(limit: number = 10) {
  // 假设后端有/api/v1/donation/records/public，若无则用/records?skip=0&limit=10
  // return request.get('/donation/records/public', { params: { limit } });
  return request.get('/donation/records', { params: { skip: 0, limit } });
} 