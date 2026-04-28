# -*- coding: utf-8 -*-
"""
注册测试示例
演示用户注册流程测试
"""

from airtest.core.api import *
import logging
import random

logging.basicConfig(level=logging.INFO)

# 配置
DEVICE_ID = ""
PACKAGE_NAME = "com.example.app"
TIMEOUT = 20

def generate_test_data():
    """生成测试数据"""
    random_num = random.randint(1000, 9999)
    return {
        "username": f"test_user_{random_num}",
        "password": f"Test@{random_num}",
        "email": f"test{random_num}@example.com"
    }

def main():
    """执行注册测试"""
    try:
        # 生成测试数据
        test_data = generate_test_data()
        logging.info(f"测试数据: {test_data}")

        # 连接设备
        if DEVICE_ID:
            connect_device(f"Android:///{DEVICE_ID}")

        # 启动应用
        start_app(PACKAGE_NAME)

        # 进入注册页面
        wait(text("注册"), timeout=TIMEOUT)
        touch(text("注册"))

        # 填写注册信息
        touch(text("用户名"))
        text(test_data["username"])

        touch(text("邮箱"))
        text(test_data["email"])

        touch(text("密码"))
        text(test_data["password"])

        touch(text("确认密码"))
        text(test_data["password"])

        # 提交注册
        touch(text("注册"))

        # 验证注册成功
        wait(text("注册成功"), timeout=TIMEOUT)
        logging.info("注册成功!")

        snapshot(filename="register_success.png")
        return True

    except Exception as e:
        logging.error(f"注册失败: {e}")
        snapshot(filename="register_error.png")
        return False

    finally:
        stop_app(PACKAGE_NAME)

if __name__ == "__main__":
    result = main()
    exit(0 if result else 1)
