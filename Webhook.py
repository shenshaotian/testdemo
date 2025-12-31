# fixed_main.py
import pytest
import os
import shutil
import requests
import json
import time
import hmac
import hashlib
import base64
import socket
import http.server
import socketserver
import webbrowser
from threading import Thread
import subprocess


def safe_remove_directory(dir_path):
    """安全删除目录"""
    if os.path.exists(dir_path):
        try:
            shutil.rmtree(dir_path)
            print(f"✅ 删除目录: {dir_path}")
        except PermissionError:
            backup_name = f"{dir_path}_backup_{int(time.time())}"
            try:
                os.rename(dir_path, backup_name)
                print(f"✅ 重命名目录: {backup_name}")
            except:
                print(f"⚠️ 无法删除或重命名 {dir_path}，跳过")


def find_available_port():
    """查找可用的端口"""
    ports_to_try = [8000, 8080, 8082, 8888, 9000, 9090]
    for port in ports_to_try:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('localhost', port))
                return port
        except OSError:
            continue
    return 8000  # 默认端口


def start_reliable_server(port, directory):
    """启动可靠的HTTP服务器"""

    class Handler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=directory, **kwargs)

        def log_message(self, format, *args):
            print(f"🌐 {self.client_address[0]} 访问: {args[0] if args else ''}")

    def serve():
        try:
            server = socketserver.TCPServer(("0.0.0.0", port), Handler)
            print(f"🚀 服务器启动: 0.0.0.0:{port}")
            print(f"📁 目录: {os.path.abspath(directory)}")
            server.serve_forever()
        except Exception as e:
            print(f"❌ 服务器错误: {e}")

    # 启动服务器线程
    server_thread = Thread(target=serve, daemon=True)
    server_thread.start()

    # 等待并验证-=[]p
    time.sleep(3)
    return ca_server_access(port)


def ca_server_access(port):
    """测试服务器访问"""
    print(f"🔍 测试服务器访问...")

    # 测试本地访问
    try:
        response = requests.get(f'http://localhost:{port}', timeout=5)
        if response.status_code == 200:
            print(f"✅ 本地访问成功: http://localhost:{port}")

            # 测试IP访问
            local_ip = get_local_ip()
            try:
                response = requests.get(f'http://{local_ip}:{port}', timeout=5)
                if response.status_code == 200:
                    print(f"✅ IP访问成功: http://{local_ip}:{port}")
                    return f"http://{local_ip}:{port}", port
                else:
                    print(f"⚠️ IP访问状态码异常: {response.status_code}")
            except:
                print(f"⚠️ IP访问失败，但本地可访问")

            return f"http://{local_ip}:{port}", port
        else:
            print(f"❌ 本地访问状态码异常: {response.status_code}")
    except Exception as e:
        print(f"❌ 本地访问失败: {e}")

    return None, None


def get_local_ip():
    """获取本机IP地址"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "localhost"


def send_feishu_notification(webhook_url, report_url, secret=None):
    """发送飞书通知"""
    current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

    message_content = {
        "msg_type": "interactive",
        "card": {
            "header": {
                "title": {"content": "📊 Allure 测试报告已生成", "tag": "plain_text"},
                "template": "blue"
            },
            "elements": [
                {
                    "tag": "div",
                    "text": {
                        "content": f"**🕐 生成时间：** {current_time}\n**🌐 访问地址：** {report_url}\n**🔧 状态：** 服务器已启动\n**💡 提示：** 如无法访问，请检查网络设置",
                        "tag": "lark_md"
                    }
                },
                {
                    "tag": "action",
                    "actions": [
                        {
                            "tag": "button",
                            "text": {"content": "点击查看报告", "tag": "plain_text"},
                            "type": "primary",
                            "url": report_url
                        }
                    ]
                }
            ]
        }
    }

    # 处理签名
    if secret:
        timestamp = str(int(time.time()))
        string_to_sign = f"{timestamp}\n{secret}"
        hmac_code = hmac.new(string_to_sign.encode("utf-8"), digestmod=hashlib.sha256).digest()
        sign = base64.b64encode(hmac_code).decode("utf-8")
        webhook_url_with_sign = f"{webhook_url}?timestamp={timestamp}&sign={sign}"
    else:
        webhook_url_with_sign = webhook_url

    headers = {"Content-Type": "application/json"}

    try:
        response = requests.post(webhook_url_with_sign, headers=headers, data=json.dumps(message_content))
        response.raise_for_status()
        print("✅ 飞书通知发送成功！")
        return True
    except requests.exceptions.RequestException as e:
        print(f"❌ 发送飞书通知时出错：{e}")
        return False


if __name__ == '__main__':
    # 配置
    WEBHOOK_URL = "https://open.feishu.cn/open-apis/bot/v2/hook/2be2687f-dea1-4961-994f-dae2c8668591"
    SECRET = None

    # 清理目录
    print("🧹 清理报告目录...")
    safe_remove_directory('report/tmp')
    safe_remove_directory('report/html')
    os.makedirs('report/tmp', exist_ok=True)
    os.makedirs('report/html', exist_ok=True)

    # 运行测试
    print("🚀 开始执行测试...")
    pytest.main(['-v', '--alluredir', 'report/tmp'])

    # 生成报告
    print("📊 生成Allure报告...")
    os.system('allure generate report/tmp -o report/html --clean')

    # 查找可用端口并启动服务器
    print("🌐 启动HTTP服务器...")
    port = find_available_port()
    print(f"🔧 使用端口: {port}")

    report_url, actual_port = start_reliable_server(port, 'report/html')

    if report_url:
        print(f"\n🎉 部署完成！")
        print(f"📢 访问地址: {report_url}")

        # 发送通知
        print("📤 发送飞书通知...")
        send_feishu_notification(WEBHOOK_URL, report_url, SECRET)

        # 打开浏览器
        print("🌐 在浏览器中打开...")
        webbrowser.open(f"http://localhost:{actual_port}")

        print(f"\n💡 如果其他设备无法访问:")
        print(f"   1. 检查防火墙设置")
        print(f"   2. 确认设备在同一网络")
        print(f"   3. 尝试访问: http://192.168.0.181:{actual_port}")

        # 保持运行
        print(f"\n🔄 服务器运行中...按 Ctrl+C 停止")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n⏹️ 停止服务器")
    else:
        print("❌ 服务器启动失败")