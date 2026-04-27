# -*- coding: utf-8 -*-
"""
退款测试示例
演示退款流程测试
"""

from airtest.core.api import *
import logging

logging.basicConfig(level=logging.INFO)

# 配置
DEVICE_ID = ""
PACKAGE_NAME = "com.example.app"
TIMEOUT = 20

def main():
    """执行退款测试"""
    try:
        if DEVICE_ID:
            connect_device(f"Android:///{DEVICE_ID}")

        start_app(PACKAGE_NAME)

        # 进入订单列表
        wait(text("我的订单"), timeout=TIMEOUT)
        touch(text("我的订单"))

        # 选择要退款的订单
        touch(text("待收货"))
        wait(text("申请退款"), timeout=TIMEOUT)

        # 申请退款
        touch(text("申请退款"))

        # 填写退款原因
        touch(text("退款原因"))
        touch(text("不想要了"))

        # 提交退款
        touch(text("提交申请"))
        wait(text("退款申请已提交"), timeout=TIMEOUT)
        logging.info("退款申请已提交!")

        snapshot(filename="refund_success.png")
        return True

    except Exception as e:
        logging.error(f"退款测试失败: {e}")
        snapshot(filename="refund_error.png")
        return False

    finally:
        stop_app(PACKAGE_NAME)

if __name__ == "__main__":
    result = main()
    exit(0 if result else 1)
