from alipay import AliPay

# 沙箱参数（请用你自己的沙箱app_id和密钥文件路径）
app_id = "9021000150609176"
app_private_key_string = open("keys/app_private_key.pem").read()
alipay_public_key_string = open("keys/alipay_public_key.pem").read()

alipay = AliPay(
    appid=app_id,
    app_notify_url="https://b74e-125-78-212-167.ngrok-free.app/api/v1/donation/alipay/notify",  # 必须公网可访问
    app_private_key_string=app_private_key_string,
    alipay_public_key_string=alipay_public_key_string,
    sign_type="RSA2",
    debug=True  # 沙箱环境
)

# 订单参数
out_trade_no = "testorder123456"  # 商户订单号，唯一
subject = "手机网站支付测试商品"
total_amount = "0.01"
body = "购买测试商品0.01元"
timeout_express = "2m"
product_code = "QUICK_WAP_WAY"

# 生成 WAP 支付 order_string
order_string = alipay.api_alipay_trade_wap_pay(
    out_trade_no=out_trade_no,
    total_amount=total_amount,
    subject=subject,
    return_url="http://localhost:8000/return",  # 可用本地
    notify_url="https://b74e-125-78-212-167.ngrok-free.app/api/v1/donation/alipay/notify",  # 必须公网可访问
    charset="utf-8",
    # 其它参数可加在 biz_content
)

# 生成 form 表单
form_html = f'''
<form id="alipaysubmit" name="alipaysubmit" action="https://openapi.alipaydev.com/gateway.do" method="POST">
    {''.join([f'<input type="hidden" name="{k}" value="{v}" />' for k, v in [tuple(p.split('=', 1)) for p in order_string.split('&')]])}
</form>
<script>document.forms['alipaysubmit'].submit();</script>
'''

with open("alipay_wap_test.html", "w", encoding="utf-8") as f:
    f.write(form_html)

print("已生成 alipay_wap_test.html，双击用浏览器打开测试跳转")