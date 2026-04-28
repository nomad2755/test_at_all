# -*- coding: utf-8 -*-
"""
登录测试示例
演示基本的登录流程测试
"""

from airtest.core.api import *
import logging

logging.basicConfig(level=logging.INFO)

# 配置
DEVICE_ID = ""
PACKAGE_NAME = "com.example.app"
TIMEOUT = 20

# 测试账号
USERNAME = "test_user"
PASSWORD = "test_password"

def main():
    """执行登录测试"""
    try:
        # 连接设备
        if DEVICE_ID:
            connect_device(f"Android:///{DEVICE_ID}")

        # 启动应用
        start_app(PACKAGE_NAME)
        logging.info("应用已启动")

        # 等待登录页面
        wait(text("登录"), timeout=TIMEOUT)

        # 输入用户名
        touch(text("用户名"))
        text(USERNAME)
        logging.info(f"已输入用户名: {USERNAME}")

        # 输入密码
        touch(text("密码"))
        text(PASSWORD)
        logging.info("已输入密码")

        # 点击登录按钮
        touch(text("登录"))
        logging.info("已点击登录按钮")

        # 验证登录成功
        wait(text("首页"), timeout=TIMEOUT)
        logging.info("登录成功!")

        # 截图
        snapshot(filename="login_success.png")

        return True

    except Exception as e:
        logging.error(f"测试失败: {e}")
        snapshot(filename="login_error.png")
        return False

    finally:
        stop_app(PACKAGE_NAME)

if __name__ == "__main__":
    result = main()
    exit(0 if result else 1)
