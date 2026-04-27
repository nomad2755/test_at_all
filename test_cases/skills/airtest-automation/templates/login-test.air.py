# -*- coding: utf-8 -*-
"""
登录测试模板
用于测试用户登录功能
"""

from airtest.core.api import *
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)

# ============ 配置区域 ============
DEVICE_ID = "{{ device_id }}"
PACKAGE_NAME = "{{ package_name }}"
TIMEOUT = {{ timeout | default(20) }}

# 登录凭证
USERNAME = "{{ username }}"
PASSWORD = "{{ password }}"

# ============ 元素定位 ============
# 登录页面元素
LOCATORS = {
    "username_input": text("用户名"),
    "password_input": text("密码"),
    "login_button": text("登录"),
    "login_success": text("首页"),
    "error_message": text("错误"),
    "logout_button": text("退出")
}

# ============ 辅助函数 ============
def wait_for_element(locator, timeout=TIMEOUT):
    """等待元素出现"""
    try:
        wait(locator, timeout=timeout)
        return True
    except:
        return False

def input_text_safe(locator, text_content):
    """安全输入文本"""
    if wait_for_element(locator):
        touch(locator)
        text(text_content)
        return True
    return False

# ============ 测试步骤 ============
def test_open_app():
    """步骤1: 打开应用"""
    logging.info("打开应用...")
    if DEVICE_ID:
        connect_device(f"Android:///{DEVICE_ID}")

    if PACKAGE_NAME:
        start_app(PACKAGE_NAME)

    # 等待应用启动
    assert wait_for_element(LOCATORS["username_input"], timeout=10), \
        "登录页面加载失败"
    logging.info("应用启动成功,进入登录页面")

def test_input_credentials():
    """步骤2: 输入登录凭证"""
    logging.info("输入登录凭证...")

    # 输入用户名
    assert input_text_safe(LOCATORS["username_input"], USERNAME), \
        "用户名输入失败"

    # 输入密码
    assert input_text_safe(LOCATORS["password_input"], PASSWORD), \
        "密码输入失败"

    logging.info("凭证输入完成")

def test_click_login():
    """步骤3: 点击登录按钮"""
    logging.info("点击登录按钮...")

    touch(LOCATORS["login_button"])

    # 等待登录结果
    sleep(2)

def test_verify_login():
    """步骤4: 验证登录结果"""
    logging.info("验证登录结果...")

    # 检查是否登录成功
    if exists(LOCATORS["login_success"]):
        logging.info("登录成功!")
        return True

    # 检查是否有错误提示
    if exists(LOCATORS["error_message"]):
        error_text = get_text(LOCATORS["error_message"])
        logging.error(f"登录失败: {error_text}")
        return False

    logging.error("登录结果未知")
    return False

def test_logout():
    """步骤5: 退出登录"""
    logging.info("退出登录...")

    if exists(LOCATORS["logout_button"]):
        touch(LOCATORS["logout_button"])
        logging.info("已退出登录")

# ============ 主函数 ============
def main():
    """执行登录测试"""
    try:
        # 执行测试步骤
        test_open_app()
        test_input_credentials()
        test_click_login()

        # 验证结果
        success = test_verify_login()

        if success:
            # 可选: 退出登录
            # test_logout()
            pass

        # 生成报告
        snapshot(filename="login_result.png")

        return success

    except Exception as e:
        logging.error(f"测试异常: {e}")
        snapshot(filename="error.png")
        return False

    finally:
        if PACKAGE_NAME:
            stop_app(PACKAGE_NAME)

if __name__ == "__main__":
    result = main()
    logging.info(f"测试结果: {'通过' if result else '失败'}")
    exit(0 if result else 1)
