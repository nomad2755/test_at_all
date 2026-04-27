# -*- coding: utf-8 -*-
"""
工作流测试模板
用于测试多步骤的业务流程
"""

from airtest.core.api import *
import logging
import time

# 配置日志
logging.basicConfig(level=logging.INFO)

# ============ 配置区域 ============
DEVICE_ID = "{{ device_id }}"
PACKAGE_NAME = "{{ package_name }}"
TIMEOUT = {{ timeout | default(20) }}

# ============ 工作流步骤定义 ============
WORKFLOW_STEPS = [
    {
        "name": "步骤1",
        "description": "准备阶段",
        "action": "prepare"
    },
    {
        "name": "步骤2",
        "description": "执行操作",
        "action": "execute"
    },
    {
        "name": "步骤3",
        "description": "验证结果",
        "action": "verify"
    }
]

# ============ 工作流执行器 ============
class WorkflowRunner:
    def __init__(self):
        self.current_step = 0
        self.results = []
        self.start_time = None

    def log_step(self, step_name, status, message=""):
        """记录步骤执行结果"""
        self.results.append({
            "step": step_name,
            "status": status,
            "message": message,
            "timestamp": time.time()
        })
        logging.info(f"[{step_name}] {status}: {message}")

    def execute_step(self, step_config):
        """执行单个步骤"""
        step_name = step_config["name"]
        action = step_config["action"]

        try:
            # 根据action执行对应方法
            method = getattr(self, f"action_{action}", None)
            if method:
                result = method(step_config)
                self.log_step(step_name, "SUCCESS", result)
                return True
            else:
                self.log_step(step_name, "SKIPPED", f"Action {action} not implemented")
                return True

        except Exception as e:
            self.log_step(step_name, "FAILED", str(e))
            return False

    # ============ 具体操作方法 ============
    def action_prepare(self, config):
        """准备阶段"""
        logging.info("执行准备操作...")

        # TODO: 添加准备逻辑
        # 例如: 检查登录状态、清理数据等

        return "准备完成"

    def action_execute(self, config):
        """执行主要操作"""
        logging.info("执行主要操作...")

        # TODO: 添加主要操作逻辑
        # 例如: 填写表单、点击按钮等

        return "操作完成"

    def action_verify(self, config):
        """验证结果"""
        logging.info("验证结果...")

        # TODO: 添加验证逻辑
        # 例如: 检查数据是否正确保存

        return "验证通过"

    def action_navigate(self, config):
        """导航操作"""
        target = config.get("target")
        logging.info(f"导航到: {target}")

        # TODO: 实现导航逻辑
        return f"已导航到 {target}"

    def action_input(self, config):
        """输入操作"""
        field = config.get("field")
        value = config.get("value")
        logging.info(f"输入: {field} = {value}")

        # TODO: 实现输入逻辑
        return f"已输入 {value}"

    def action_click(self, config):
        """点击操作"""
        element = config.get("element")
        logging.info(f"点击: {element}")

        # TODO: 实现点击逻辑
        return f"已点击 {element}"

    # ============ 运行工作流 ============
    def run(self, steps):
        """运行完整工作流"""
        self.start_time = time.time()
        all_passed = True

        for i, step in enumerate(steps):
            self.current_step = i
            success = self.execute_step(step)

            if not success:
                all_passed = False
                # 可选: 失败后是否继续
                # break

            # 步骤间等待
            sleep(1)

        # 生成报告
        self.generate_report()

        return all_passed

    def generate_report(self):
        """生成工作流报告"""
        duration = time.time() - self.start_time

        report = {
            "total_steps": len(self.results),
            "passed": sum(1 for r in self.results if r["status"] == "SUCCESS"),
            "failed": sum(1 for r in self.results if r["status"] == "FAILED"),
            "duration": f"{duration:.2f}s",
            "steps": self.results
        }

        logging.info(f"工作流报告: {report}")
        return report

# ============ 主函数 ============
def main():
    """执行工作流测试"""
    try:
        # 初始化设备
        if DEVICE_ID:
            connect_device(f"Android:///{DEVICE_ID}")

        if PACKAGE_NAME:
            start_app(PACKAGE_NAME)

        # 创建工作流执行器
        runner = WorkflowRunner()

        # 执行工作流
        success = runner.run(WORKFLOW_STEPS)

        # 截图
        snapshot(filename="workflow_result.png")

        return success

    except Exception as e:
        logging.error(f"工作流异常: {e}")
        snapshot(filename="error.png")
        return False

    finally:
        if PACKAGE_NAME:
            stop_app(PACKAGE_NAME)

if __name__ == "__main__":
    result = main()
    logging.info(f"工作流测试结果: {'通过' if result else '失败'}")
    exit(0 if result else 1)
