import hashlib
import hmac
import json
import time
import uuid
from typing import Dict, Any, Optional
import requests
from wechatpayv3 import WeChatPay, WeChatPayType
from app.core.config import settings
import os


class WeChatPayV3:
    """微信支付V3工具类"""
    
    def __init__(self):
        self.wechat_appid = settings.wechat_appid
        self.wechat_mchid = settings.wechat_mchid
        self.wechat_api_v3_key = settings.wechat_api_v3_key
        self.wechat_private_key_path = settings.wechat_private_key_path
        self.wechat_cert_serial_no = settings.wechat_cert_serial_no
        self.wechat_notify_url = settings.wechat_notify_url
        self.wechat_platform_cert_path = settings.wechat_platform_cert_path
        self.wechat_pay_type = settings.wechat_pay_type
        
        # 初始化微信支付V3客户端
        self._init_wechat_pay()
    
    def _init_wechat_pay(self):
        """初始化微信支付V3客户端"""
        try:
            if all([self.wechat_appid, self.wechat_mchid, self.wechat_api_v3_key, self.wechat_private_key_path, self.wechat_cert_serial_no]):
                # 使用完整配置初始化
                self.wechat_pay = WeChatPay(
                    wechatpay_type=WeChatPayType.NATIVE,
                    mchid=self.wechat_mchid,
                    private_key=self.wechat_private_key_path,
                    cert_serial_no=self.wechat_cert_serial_no,
                    apiv3_key=self.wechat_api_v3_key,
                    appid=self.wechat_appid,
                    notify_url=self.wechat_notify_url,
                    cert_dir="certs/"
                )
                print("✅ 微信支付V3客户端初始化成功")
            else:
                # 使用API密钥方式初始化（仅用于测试）
                self.wechat_pay = WeChatPay(
                    wechatpay_type=WeChatPayType.NATIVE,
                    mchid=self.wechat_mchid or "test_mchid",
                    private_key=None,
                    cert_serial_no=None,
                    apiv3_key=self.wechat_api_v3_key or "test_key",
                    appid=self.wechat_appid or "test_appid",
                    notify_url=self.wechat_notify_url,
                    cert_dir="certs/"
                )
                print("⚠️  使用测试模式初始化微信支付V3")
        except Exception as e:
            print(f"初始化微信支付V3失败: {e}")
            self.wechat_pay = None
    

    
    def create_order(self, out_trade_no: str, total_amount: int, description: str, 
                    openid: Optional[str] = None) -> Dict[str, Any]:
        """
        创建微信支付订单（V3版本）
        
        Args:
            out_trade_no: 商户订单号
            total_amount: 支付金额（分）
            description: 商品描述
            openid: 用户openid（JSAPI支付需要）
        
        Returns:
            包含支付信息的字典
        """
        if not self.wechat_pay:
            raise ValueError("微信支付客户端未初始化")
        
        if not all([self.wechat_appid, self.wechat_mchid]):
            raise ValueError("微信支付配置不完整")
        
        try:
            # 构建订单参数
            order_data = {
                "appid": self.wechat_appid,
                "mchid": self.wechat_mchid,
                "description": description,
                "out_trade_no": out_trade_no,
                "notify_url": self.wechat_notify_url,
                "amount": {
                    "total": total_amount,
                    "currency": "CNY"
                }
            }
            
            # 根据支付方式设置不同参数
            if openid:
                # JSAPI支付
                order_data["payer"] = {"openid": openid}
                result = self.wechat_pay.pay(
                    description=description,
                    out_trade_no=out_trade_no,
                    amount=total_amount,
                    payer_openid=openid,
                    notify_url=self.wechat_notify_url
                )
            else:
                # Native支付（扫码支付）
                result = self.wechat_pay.pay(
                    description=description,
                    out_trade_no=out_trade_no,
                    amount=total_amount,
                    notify_url=self.wechat_notify_url
                )
            
            # 处理返回结果
            if result.get("code_url"):
                return {
                    "prepay_id": result.get("prepay_id"),
                    "code_url": result.get("code_url"),
                    "trade_type": "NATIVE" if not openid else "JSAPI"
                }
            else:
                raise Exception(f"微信支付订单创建失败: {result}")
                
        except Exception as e:
            print(f"创建微信支付订单失败: {e}")
            raise
    
    def verify_notify(self, notify_data: str) -> Dict[str, Any]:
        """
        验证微信支付回调（V3版本）
        
        Args:
            notify_data: 微信回调的JSON数据
        
        Returns:
            解析后的回调数据
        """
        try:
            if not self.wechat_pay:
                raise Exception("微信支付客户端未初始化")
            
            # 验证回调数据
            result = self.wechat_pay.decrypt(notify_data)
            
            # 验证签名
            if not self.wechat_pay.verify(notify_data):
                raise Exception("微信支付回调签名验证失败")
            
            return result
            
        except Exception as e:
            print(f"验证微信支付回调失败: {e}")
            raise
    
    def query_order(self, out_trade_no: str) -> Dict[str, Any]:
        """
        查询订单状态（V3版本）
        
        Args:
            out_trade_no: 商户订单号
        
        Returns:
            订单状态信息
        """
        try:
            if not self.wechat_pay:
                raise Exception("微信支付客户端未初始化")
            
            result = self.wechat_pay.query_order(out_trade_no)
            return result
            
        except Exception as e:
            print(f"查询订单状态失败: {e}")
            raise
    
    def close_order(self, out_trade_no: str) -> bool:
        """
        关闭订单（V3版本）
        
        Args:
            out_trade_no: 商户订单号
        
        Returns:
            是否成功关闭
        """
        try:
            if not self.wechat_pay:
                raise Exception("微信支付客户端未初始化")
            
            result = self.wechat_pay.close_order(out_trade_no)
            return result.get("code") == 200
            
        except Exception as e:
            print(f"关闭订单失败: {e}")
            return False
    
    def refund(self, out_trade_no: str, out_refund_no: str, 
               total_amount: int, refund_amount: int) -> Dict[str, Any]:
        """
        申请退款（V3版本）
        
        Args:
            out_trade_no: 原订单号
            out_refund_no: 退款单号
            total_amount: 原订单金额（分）
            refund_amount: 退款金额（分）
        
        Returns:
            退款结果
        """
        try:
            if not self.wechat_pay:
                raise Exception("微信支付客户端未初始化")
            
            result = self.wechat_pay.refund(
                out_trade_no=out_trade_no,
                out_refund_no=out_refund_no,
                amount=total_amount,
                refund_amount=refund_amount
            )
            return result
            
        except Exception as e:
            print(f"申请退款失败: {e}")
            raise
    
    def generate_qr_code_url(self, code_url: str) -> str:
        """
        生成二维码图片URL
        
        Args:
            code_url: 微信返回的二维码链接
        
        Returns:
            二维码图片URL
        """
        # 这里可以集成二维码生成服务
        # 暂时返回原始链接
        return code_url


# 创建全局微信支付V3实例
wechat_pay_v3 = WeChatPayV3() 