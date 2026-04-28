# -*- coding: utf-8 -*-
"""
冒烟测试示例
基础功能验证测试
"""

from airtest.core.api import *
import logging

logging.basicConfig(level=logging.INFO)

# 配置
DEVICE_ID = ""
PACKAGE_NAME = "com.example.app"
TIMEOUT = 20

def test_app_launch():
    """测试应用启动"""
    logging.info("测试应用启动...")
    start_app(PACKAGE_NAME)
    result = wait(text("首页"), timeout=TIMEOUT)
    assert result, "应用启动失败"
    logging.info("应用启动成功")
    return True

def test_navigation():
    """测试底部导航"""
    logging.info("测试底部导航...")

    # 遍历底部导航
    tabs = ["首页", "分类", "购物车", "我的"]

    for tab in tabs:
        touch(text(tab))
        sleep(1)
        result = exists(text(tab))
        assert result, f"切换到{tab}失败"
        logging.info(f"已切换到{tab}")

    return True

def test_search():
    """测试搜索功能"""
    logging.info("测试搜索功能...")

    # 进入搜索
    touch(text("搜索"))
    wait(text("搜索框"), timeout=TIMEOUT)

    # 输入搜索关键词
    text("测试商品")
    touch(text("搜索"))

    # 验证搜索结果
    result = exists(text("测试商品"))
    assert result, "搜索无结果"
    logging.info("搜索功能正常")

    return True

def test_profile():
    """测试个人中心"""
    logging.info("测试个人中心...")

    touch(text("我的"))
    wait(text("设置"), timeout=TIMEOUT)

    # 验证个人中心元素
    elements = ["我的订单", "收货地址", "设置"]
    for elem in elements:
        result = exists(text(elem))
        assert result, f"缺少{elem}元素"
        logging.info(f"个人中心包含{elem}")

    return True

def main():
    """执行冒烟测试"""
    tests = [
        ("应用启动", test_app_launch),
        ("底部导航", test_navigation),
        ("搜索功能", test_search),
        ("个人中心", test_profile)
    ]

    results = []

    try:
        if DEVICE_ID:
            connect_device(f"Android:///{DEVICE_ID}")

        for name, test_func in tests:
            try:
                success = test_func()
                results.append({"name": name, "status": "PASS" if success else "FAIL"})
            except Exception as e:
                logging.error(f"{name}测试失败: {e}")
                results.append({"name": name, "status": "FAIL", "error": str(e)})
                snapshot(filename=f"smoke_{name}_error.png")

        # 输出测试结果
        logging.info("=" * 50)
        logging.info("冒烟测试结果:")
        for r in results:
            logging.info(f"  {r['name']}: {r['status']}")
        logging.info("=" * 50)

        return all(r["status"] == "PASS" for r in results)

    except Exception as e:
        logging.error(f"冒烟测试异常: {e}")
        return False

    finally:
        stop_app(PACKAGE_NAME)

if __name__ == "__main__":
    result = main()
    exit(0 if result else 1)
