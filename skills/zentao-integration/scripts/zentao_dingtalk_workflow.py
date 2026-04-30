#!/usr/bin/env python3
"""
禅道测试工作流 + 通知
支持 Open-IM 和钉钉通知

功能：创建测试用例 → 导入禅道 → 发送 IM 通知
"""

import json
import requests
import argparse
from datetime import datetime
from typing import List, Dict, Any, Optional

# ============ 配置 ============
ZENTAO_BASE = "http://192.168.0.28:9980/api.php/v1"
ZENTAO_TOKEN = "cf2da27b8b734b419352d844bc451a14"
ZENTAO_HEADERS = {
    "Token": ZENTAO_TOKEN,
    "Content-Type": "application/json"
}

# Open-IM 配置（可通过环境变量覆盖）
OPENIM_API_URL = "http://YOUR_OPENIM_SERVER:10000"
OPENIM_TOKEN = "YOUR_IM_TOKEN"


class OpenIMNotifier:
    """
    Open-IM 通知发送器
    
    使用 Open-IM 的 Webhook 接口发送消息
    API: http://IP:10000/callback/send_msg
    """
    
    def __init__(self, api_url: str = None, im_token: str = None):
        self.api_url = (api_url or OPENIM_API_URL).rstrip('/')
        self.callback_url = f"{self.api_url}/callback/send_msg"
        self.im_token = im_token or OPENIM_TOKEN
    
    def send_text(self, sender_id: str, recv_id: str, text: str) -> bool:
        """
        发送文本消息
        
        Args:
            sender_id: 发送者 ID
            recv_id: 接收者 ID (用户ID或群ID)
            text: 文本内容
            
        Returns:
            bool: 发送是否成功
        """
        import base64
        
        payload = {
            "callbackCommand": "sendMsg",
            "imToken": self.im_token,
            "sendMsgReq": {
                "senderId": sender_id,
                "recvId": recv_id,
                "content": base64.b64encode(text.encode('utf-8')).decode('utf-8'),
                "contentType": 1,  # 1=text, 2=image, etc.
                "options": {
                    "callbackTimeout": 10
                }
            }
        }
        
        try:
            response = requests.post(self.callback_url, json=payload, timeout=15)
            result = response.json()
            
            if result.get("errCode") == 0:
                print(f"✅ Open-IM 消息发送成功")
                return True
            else:
                print(f"❌ Open-IM 消息发送失败: {result.get('errMsg')}")
                return False
        except Exception as e:
            print(f"❌ Open-IM 消息发送异常: {e}")
            return False
    
    def send_test_report(self, sender_id: str, recv_id: str,
                        task_title: str, task_id: str,
                        total_cases: int, created_cases: int,
                        report_summary: str = "",
                        zentao_url: str = "http://192.168.0.28:9980") -> bool:
        """
        发送测试报告到 Open-IM
        """
        content = f"""【测试报告】

📌 任务: {task_title}
🔗 禅道: {zentao_url}/task-view-{task_id}.html

📊 用例统计:
• 总数: {total_cases}
• 已创建: {created_cases}

📝 摘要: {report_summary or '测试用例已成功创建'}

⏰ {datetime.now().strftime('%Y-%m-%d %H:%M')}"""
        
        return self.send_text(sender_id, recv_id, content)
    
    def send_bug_notification(self, sender_id: str, recv_id: str,
                             bug_id: int, bug_title: str,
                             severity: str, desc: str,
                             zentao_url: str = "http://192.168.0.28:9980") -> bool:
        """
        发送 Bug 通知到 Open-IM
        """
        severity_map = {"1": "🔴 致命", "2": "🟠 严重", "3": "🟡 一般", "4": "🔵 优化"}
        
        content = f"""🐛 【新建Bug】

🔖 ID: {bug_id}
📛 标题: {bug_title}
⚠️ 严重程度: {severity_map.get(severity, severity)}
🔗 禅道: {zentao_url}/bug-view-{bug_id}.html

📄 描述: {desc}

⏰ {datetime.now().strftime('%Y-%m-%d %H:%M')}"""
        
        return self.send_text(sender_id, recv_id, content)


class ZenTaoOpenIMWorkflow:
    """
    禅道 + Open-IM 工作流
    整合测试用例创建和内部 IM 通知
    """
    
    def __init__(self, openim_api_url: str = None, openim_token: str = None):
        self.zentao_token = ZENTAO_TOKEN
        self.zentao_base = ZENTAO_BASE
        self.headers = ZENTAO_HEADERS
        self.openim = OpenIMNotifier(api_url=openim_api_url, im_token=openim_token)
    
    def create_test_case(self, title: str, pri: int = 3, 
                        steps: List[Dict[str, str]] = None,
                        type_: str = "feature",
                        product_id: int = 2) -> Optional[int]:
        """
        创建测试用例
        
        Args:
            title: 用例标题
            pri: 优先级 (1-4)
            steps: 步骤列表 [{"desc": "步骤", "expect": "预期"}]
            type_: 用例类型 (feature/performance/config/security/others)
            product_id: 产品 ID (2=个人数字空间)
            
        Returns:
            int: 创建的用例 ID，失败返回 None
        """
        url = f"{self.zentao_base}/products/{product_id}/testcases"
        
        data = {
            "title": title,
            "pri": pri,
            "type": type_,
            "steps": steps or [{"desc": "待补充", "expect": "待补充"}]
        }
        
        try:
            response = requests.post(url, headers=self.headers, json=data, timeout=10)
            
            if response.status_code == 201:
                result = response.json()
                case_id = result.get("id") or result.get("data", {}).get("id")
                print(f"✅ 测试用例创建成功: {title} (ID: {case_id})")
                return case_id
            else:
                print(f"❌ 测试用例创建失败: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            print(f"❌ 测试用例创建异常: {e}")
            return None
    
    def batch_create_cases(self, cases: List[Dict[str, Any]], 
                          product_id: int = 2) -> Dict[str, int]:
        """
        批量创建测试用例
        
        Args:
            cases: 用例列表
            [
                {
                    "title": "用例标题",
                    "pri": 1,
                    "steps": [{"desc": "步骤", "expect": "预期"}],
                    "type": "feature"
                }
            ]
            product_id: 产品 ID
            
        Returns:
            {"total": 10, "success": 8, "failed": 2}
        """
        results = {"total": len(cases), "success": 0, "failed": 0}
        
        for case in cases:
            case_id = self.create_test_case(
                title=case.get("title"),
                pri=case.get("pri", 3),
                steps=case.get("steps"),
                type_=case.get("type", "feature"),
                product_id=product_id
            )
            
            if case_id:
                results["success"] += 1
            else:
                results["failed"] += 1
        
        return results
    
    def run(self, task_title: str, task_id: str,
            cases: List[Dict[str, Any]] = None,
            report_summary: str = "",
            product_id: int = 2,
            recv_id: str = "user001") -> Dict[str, Any]:
        """
        运行完整工作流：创建用例 → Open-IM 通知
        
        Args:
            task_title: 禅道任务标题
            task_id: 禅道任务 ID
            cases: 测试用例列表
            report_summary: 报告摘要
            product_id: 产品 ID
            recv_id: Open-IM 接收者 ID
            
        Returns:
            工作流执行结果
        """
        print(f"\n{'='*50}")
        print(f"🚀 禅道测试工作流启动")
        print(f"{'='*50}")
        print(f"任务: {task_title} (ID: {task_id})")
        print(f"产品ID: {product_id}")
        print(f"用例数量: {len(cases) if cases else 0}")
        print()
        
        # 1. 创建测试用例
        if cases:
            print("📝 正在创建测试用例...")
            create_result = self.batch_create_cases(cases, product_id)
            print(f"   创建结果: 成功 {create_result['success']}, 失败 {create_result['failed']}")
        else:
            create_result = {"total": 0, "success": 0, "failed": 0}
        
        # 2. 发送 Open-IM 通知
        print("\n📤 正在发送 Open-IM 通知...")
        notified = self.openim.send_test_report(
            sender_id="robot001",  # 可配置为机器人 ID
            recv_id=recv_id,
            task_title=task_title,
            task_id=task_id,
            total_cases=create_result["total"],
            created_cases=create_result["success"],
            report_summary=report_summary
        )
        
        print(f"\n{'='*50}")
        print(f"✅ 工作流执行完成")
        print(f"{'='*50}")
        
        return {
            "success": create_result["success"] > 0 and notified,
            "cases_created": create_result["success"],
            "cases_failed": create_result["failed"],
            "im_notified": notified
        }


def main():
    parser = argparse.ArgumentParser(description="禅道测试工作流 + Open-IM 通知")
    parser.add_argument("--task-id", type=str, required=True, help="禅道任务 ID")
    parser.add_argument("--task-title", type=str, required=True, help="任务标题")
    parser.add_argument("--case-count", type=int, default=5, help="生成用例数量")
    parser.add_argument("--product-id", type=int, default=2, help="产品 ID")
    parser.add_argument("--openim-url", type=str, help="Open-IM API 地址")
    parser.add_argument("--recv", type=str, default="user001", help="接收者 ID")
    
    args = parser.parse_args()
    
    # 示例：用 LLM 生成测试用例（或从文件读取）
    sample_cases = [
        {
            "title": f"测试用例-{i}",
            "pri": 3,
            "steps": [{"desc": f"步骤{i}.1", "expect": f"预期{i}.1"}],
            "type": "feature"
        }
        for i in range(1, args.case_count + 1)
    ]
    
    workflow = ZenTaoOpenIMWorkflow(openim_api_url=args.openim_url)
    result = workflow.run(
        task_title=args.task_title,
        task_id=args.task_id,
        cases=sample_cases,
        recv_id=args.recv
    )
    
    print(f"\n执行结果: {json.dumps(result, ensure_ascii=False, indent=2)}")


if __name__ == "__main__":
    main()
