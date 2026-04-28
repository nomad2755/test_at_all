# -*- coding: utf-8 -*-
"""
基础测试模板
用于快速创建简单的UI自动化测试
"""

from airtest.core.api import *
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)

# ============ 配置区域 ============
# 设备ID (可选,留空则自动连接)
DEVICE_ID = "{{ device_id }}"

# 测试应用包名
PACKAGE_NAME = "{{ package_name }}"

# 测试超时时间
TIMEOUT = {{ timeout | default(20) }}

# ============ 初始化 ============
def setup():
    """初始化测试环境"""
    if DEVICE_ID:
        connect_device(f"Android:///{DEVICE_ID}")

    # 启动应用
    if PACKAGE_NAME:
        start_app(PACKAGE_NAME)

    logging.info("测试环境初始化完成")

def teardown():
    """清理测试环境"""
    # 停止应用
    if PACKAGE_NAME:
        stop_app(PACKAGE_NAME)

    logging.info("测试环境清理完成")

# ============ 测试步骤 ============
def test_step_1():
    """测试步骤1: 等待应用启动"""
    # TODO: 修改为实际的元素定位
    wait(text("欢迎"), timeout=TIMEOUT)
    logging.info("应用启动成功")

def test_step_2():
    """测试步骤2: 执行主要操作"""
    # TODO: 添加测试操作
    # touch(text("按钮"))
    # text("输入内容")
    pass

def test_step_3():
    """测试步骤3: 验证结果"""
    # TODO: 添加验证逻辑
    # assert_exists(text("成功"), "操作应该成功")
    pass

# ============ 主函数 ============
def main():
    """执行测试"""
    try:
        setup()

        # 执行测试步骤
        test_step_1()
        test_step_2()
        test_step_3()

        logging.info("测试通过!")
        return True

    except Exception as e:
        logging.error(f"测试失败: {e}")
        # 截图保存失败场景
        snapshot(filename="failure.png")
        return False

    finally:
        teardown()

if __name__ == "__main__":
    result = main()
    exit(0 if result else 1)
