#!/usr/bin/env python3
"""
PayPal支付集成演示脚本
"""

import asyncio
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.config import settings
from app.core.paypal import paypal_pay


def demo_paypal_config():
    """演示PayPal配置"""
    print("PayPal支付集成演示")
    print("=" * 50)
    print("1. 配置检查")
    print(f"   PayPal Client ID: {settings.paypal_client_id or '未配置'}")
    print(f"   PayPal Client Secret: {'已配置' if settings.paypal_client_secret else '未配置'}")
    print(f"   PayPal API Base: {settings.paypal_api_base}")
    print(f"   PayPal Return URL: {settings.paypal_return_url or '未配置'}")
    print(f"   PayPal Cancel URL: {settings.paypal_cancel_url or '未配置'}")
    print(f"   PayPal Currency: {settings.paypal_currency}")
    print()


def demo_paypal_order_creation():
    """演示PayPal订单创建"""
    print("2. 订单创建演示")
    if all([paypal_pay.client_id, paypal_pay.client_secret, paypal_pay.access_token]):
        try:
            # 模拟创建捐赠订单
            result = paypal_pay.create_order(
                out_trade_no="DEMO_PAYPAL_001",
                total_amount=25.00,  # 25美元
                description="演示捐赠PayPal"
            )
            
            if result.get("success"):
                print("✅ PayPal订单创建成功")
                print(f"   订单ID: {result.get('order_id')}")
                print(f"   审批URL: {result.get('approval_url')}")
                print(f"   状态: {result.get('status')}")
            else:
                print(f"❌ PayPal订单创建失败: {result.get('error')}")
        except Exception as e:
            print(f"❌ PayPal订单创建异常: {e}")
    else:
        print("⚠️  配置不完整，跳过订单创建演示")
    print()


def demo_paypal_features():
    """演示PayPal功能"""
    print("3. 功能演示")
    
    # 演示获取订单详情
    print("   获取订单详情功能:")
    print("   - 支持查询订单状态")
    print("   - 支持获取订单金额")
    print("   - 支持获取订单信息")
    
    # 演示捕获订单
    print("   捕获订单功能:")
    print("   - 支持自动捕获支付")
    print("   - 支持手动捕获支付")
    print("   - 支持部分捕获")
    
    # 演示退款
    print("   退款功能:")
    print("   - 支持全额退款")
    print("   - 支持部分退款")
    print("   - 支持退款查询")
    print()


def demo_paypal_webhook():
    """演示PayPal Webhook"""
    print("4. Webhook回调演示")
    print("   PayPal支持以下Webhook事件:")
    print("   - PAYMENT.CAPTURE.COMPLETED: 支付完成")
    print("   - PAYMENT.CAPTURE.DENIED: 支付被拒绝")
    print("   - PAYMENT.CAPTURE.PENDING: 支付待处理")
    print("   - PAYMENT.CAPTURE.REFUNDED: 支付已退款")
    print("   - PAYMENT.CAPTURE.REVERSED: 支付已撤销")
    print()


def demo_frontend_integration():
    """演示前端集成"""
    print("5. 前端集成说明")
    print("   在捐赠表单中，用户选择PayPal后：")
    print("   1. 前端发送POST请求到 /api/v1/donation/create")
    print("   2. 后端创建PayPal订单")
    print("   3. 返回PayPal审批URL")
    print("   4. 前端跳转到PayPal支付页面")
    print("   5. 用户完成支付后回调 /api/v1/donation/callback/paypal")
    print("   6. 后端更新订单状态并发送通知")
    print()


def demo_config_suggestions():
    """演示配置建议"""
    print("6. 配置建议")
    print("   要使用真实的PayPal支付，需要：")
    print("   1. 注册PayPal开发者账户")
    print("   2. 创建PayPal应用获取Client ID和Secret")
    print("   3. 在.env文件中配置相关参数")
    print("   4. 配置正确的Return URL和Cancel URL")
    print("   5. 配置Webhook回调URL")
    print("   6. 测试沙盒环境支付流程")
    print("   7. 切换到生产环境")
    print()


def main():
    """主演示函数"""
    demo_paypal_config()
    demo_paypal_order_creation()
    demo_paypal_features()
    demo_paypal_webhook()
    demo_frontend_integration()
    demo_config_suggestions()
    
    print("=" * 50)
    print("演示完成！")
    print("PayPal支付集成已准备就绪，配置真实参数后即可使用。")


if __name__ == "__main__":
    main() 