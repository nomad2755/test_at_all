# -*- coding: utf-8 -*-
"""
订单测试示例
演示订单创建流程测试
"""

from airtest.core.api import *
import logging

logging.basicConfig(level=logging.INFO)

# 配置
DEVICE_ID = ""
PACKAGE_NAME = "com.example.app"
TIMEOUT = 20

def main():
    """执行订单测试"""
    try:
        if DEVICE_ID:
            connect_device(f"Android:///{DEVICE_ID}")

        start_app(PACKAGE_NAME)

        # 假设已登录,进入商品列表
        wait(text("商品"), timeout=TIMEOUT)

        # 选择商品
        touch(text("商品详情"))
        logging.info("进入商品详情")

        # 添加到购物车
        touch(text("加入购物车"))
        wait(text("已添加"), timeout=5)
        logging.info("商品已加入购物车")

        # 进入购物车
        touch(text("购物车"))
        wait(text("去结算"), timeout=TIMEOUT)

        # 提交订单
        touch(text("去结算"))
        wait(text("确认订单"), timeout=TIMEOUT)
        touch(text("提交订单"))

        # 验证订单创建
        wait(text("订单创建成功"), timeout=TIMEOUT)
        logging.info("订单创建成功!")

        snapshot(filename="order_success.png")
        return True

    except Exception as e:
        logging.error(f"订单测试失败: {e}")
        snapshot(filename="order_error.png")
        return False

    finally:
        stop_app(PACKAGE_NAME)

if __name__ == "__main__":
    result = main()
    exit(0 if result else 1)
