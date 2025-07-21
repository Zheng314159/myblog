#!/usr/bin/env python3
"""
PayPal支付工具类
"""

import requests
import json
import base64
from typing import Dict, Optional, Any
from app.core.config import settings


class PayPalPay:
    """PayPal支付工具类"""
    
    def __init__(self):
        self.paypal_client_id = settings.paypal_client_id
        self.paypal_client_secret = settings.paypal_client_secret
        self.paypal_api_base = settings.paypal_api_base
        self.paypal_return_url = settings.paypal_return_url
        self.paypal_cancel_url = settings.paypal_cancel_url
        self.paypal_currency = settings.paypal_currency
        self.access_token = None
        
        # 初始化PayPal客户端
        self._init_paypal()
    
    def _init_paypal(self):
        """初始化PayPal客户端"""
        try:
            if all([self.paypal_client_id, self.paypal_client_secret]):
                # 获取访问令牌
                self.access_token = self._get_access_token()
                if self.access_token:
                    print("✅ PayPal客户端初始化成功")
                else:
                    print("❌ PayPal访问令牌获取失败")
            else:
                print("⚠️  PayPal配置不完整，使用测试模式")
        except Exception as e:
            print(f"初始化PayPal失败: {e}")
            self.access_token = None
    
    def _get_access_token(self) -> Optional[str]:
        """获取PayPal访问令牌"""
        try:
            # 构建认证头
            credentials = f"{self.paypal_client_id}:{self.paypal_client_secret}"
            encoded_credentials = base64.b64encode(credentials.encode()).decode()
            
            headers = {
                "Authorization": f"Basic {encoded_credentials}",
                "Content-Type": "application/x-www-form-urlencoded"
            }
            
            data = {
                "grant_type": "client_credentials"
            }
            
            # 发送请求获取访问令牌
            response = requests.post(
                f"{self.paypal_api_base}/v1/oauth2/token",
                headers=headers,
                data=data,
                timeout=30
            )
            
            if response.status_code == 200:
                token_data = response.json()
                return token_data.get("access_token")
            else:
                print(f"获取PayPal访问令牌失败: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"获取PayPal访问令牌异常: {e}")
            return None
    
    def create_order(self, out_trade_no: str, total_amount: float, description: str) -> Dict[str, Any]:
        """创建PayPal订单"""
        try:
            if not self.access_token:
                return {"error": "PayPal访问令牌未获取"}
            
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }
            
            # 构建订单数据
            order_data = {
                "intent": "CAPTURE",
                "purchase_units": [
                    {
                        "reference_id": out_trade_no,
                        "description": description,
                        "amount": {
                            "currency_code": self.paypal_currency,
                            "value": str(total_amount)
                        }
                    }
                ],
                "application_context": {
                    "return_url": f"{self.paypal_return_url}?order_id={out_trade_no}",
                    "cancel_url": f"{self.paypal_cancel_url}?order_id={out_trade_no}"
                }
            }
            
            # 发送创建订单请求
            response = requests.post(
                f"{self.paypal_api_base}/v2/checkout/orders",
                headers=headers,
                json=order_data,
                timeout=30
            )
            
            if response.status_code == 201:
                order_info = response.json()
                return {
                    "success": True,
                    "order_id": order_info.get("id"),
                    "approval_url": self._get_approval_url(order_info),
                    "status": order_info.get("status")
                }
            else:
                print(f"创建PayPal订单失败: {response.status_code} - {response.text}")
                return {"error": f"创建订单失败: {response.text}"}
                
        except Exception as e:
            print(f"创建PayPal订单异常: {e}")
            return {"error": str(e)}
    
    def _get_approval_url(self, order_info: Dict[str, Any]) -> Optional[str]:
        """从订单信息中获取审批URL"""
        try:
            links = order_info.get("links", [])
            for link in links:
                if link.get("rel") == "approve":
                    return link.get("href")
            return None
        except Exception as e:
            print(f"获取PayPal审批URL失败: {e}")
            return None
    
    def capture_order(self, order_id: str) -> Dict[str, Any]:
        """捕获PayPal订单"""
        try:
            if not self.access_token:
                return {"error": "PayPal访问令牌未获取"}
            
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }
            
            # 发送捕获订单请求
            response = requests.post(
                f"{self.paypal_api_base}/v2/checkout/orders/{order_id}/capture",
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 201:
                capture_info = response.json()
                return {
                    "success": True,
                    "capture_id": capture_info.get("id"),
                    "status": capture_info.get("status"),
                    "amount": capture_info.get("amount", {}).get("value")
                }
            else:
                print(f"捕获PayPal订单失败: {response.status_code} - {response.text}")
                return {"error": f"捕获订单失败: {response.text}"}
                
        except Exception as e:
            print(f"捕获PayPal订单异常: {e}")
            return {"error": str(e)}
    
    def get_order_details(self, order_id: str) -> Dict[str, Any]:
        """获取PayPal订单详情"""
        try:
            if not self.access_token:
                return {"error": "PayPal访问令牌未获取"}
            
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }
            
            # 发送获取订单详情请求
            response = requests.get(
                f"{self.paypal_api_base}/v2/checkout/orders/{order_id}",
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                order_info = response.json()
                return {
                    "success": True,
                    "order_id": order_info.get("id"),
                    "status": order_info.get("status"),
                    "amount": order_info.get("amount", {}).get("value"),
                    "intent": order_info.get("intent")
                }
            else:
                print(f"获取PayPal订单详情失败: {response.status_code} - {response.text}")
                return {"error": f"获取订单详情失败: {response.text}"}
                
        except Exception as e:
            print(f"获取PayPal订单详情异常: {e}")
            return {"error": str(e)}
    
    def refund_payment(self, capture_id: str, amount: Optional[float] = None) -> Dict[str, Any]:
        """退款PayPal支付"""
        try:
            if not self.access_token:
                return {"error": "PayPal访问令牌未获取"}
            
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }
            
            # 构建退款数据
            refund_data = {}
            if amount:
                refund_data["amount"] = {
                    "currency_code": self.paypal_currency,
                    "value": str(amount)
                }
            
            # 发送退款请求
            response = requests.post(
                f"{self.paypal_api_base}/v2/payments/captures/{capture_id}/refund",
                headers=headers,
                json=refund_data,
                timeout=30
            )
            
            if response.status_code == 201:
                refund_info = response.json()
                return {
                    "success": True,
                    "refund_id": refund_info.get("id"),
                    "status": refund_info.get("status"),
                    "amount": refund_info.get("amount", {}).get("value")
                }
            else:
                print(f"PayPal退款失败: {response.status_code} - {response.text}")
                return {"error": f"退款失败: {response.text}"}
                
        except Exception as e:
            print(f"PayPal退款异常: {e}")
            return {"error": str(e)}
    
    def verify_webhook(self, headers: Dict[str, str], body: str) -> bool:
        """验证PayPal Webhook签名"""
        # TODO: 实现PayPal Webhook签名验证
        # 这需要PayPal的Webhook证书
        return True


# 创建全局PayPal实例
paypal_pay = PayPalPay() 