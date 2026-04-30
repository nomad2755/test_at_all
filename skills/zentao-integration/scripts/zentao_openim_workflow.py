#!/usr/bin/env python3
"""
Open-IM 通知模块 v3
集成认证 + 发送消息

认证: POST http://192.168.0.27:10002/auth/user_token
发送: POST https://easydoc-test.rentsoft.cn/rpc/2/im/message/send
"""

import json
import requests
from datetime import datetime
from typing import Optional, List


class OpenIMClient:
    """
    Open-IM 客户端
    包含认证和消息发送功能
    """
    
    def __init__(self, api_host: str = "http://192.168.0.27:10002"):
        """
        初始化 Open-IM 客户端
        
        Args:
            api_host: Open-IM API 主机地址
        """
        self.api_host = api_host.rstrip('/')
        self.auth_url = f"{self.api_host}/auth/user_token"
        self.send_msg_url = f"https://easydoc-test.rentsoft.cn/rpc/2/im/message/send"
        self.token = None
    
    def authenticate(self, secret: str = "openIM123", user_id: str = "imAdmin", 
                   platform_id: int = 1) -> bool:
        """
        获取认证 Token
        
        Args:
            secret: 密钥 (默认: openIM123)
            user_id: 用户 ID (默认: imAdmin)
            platform_id: 平台 ID (默认: 1)
            
        Returns:
            bool: 认证是否成功
        """
        payload = {
            "secret": secret,
            "userID": user_id,
            "platformID": platform_id
        }
        
        headers = {
            "Content-Type": "application/json",
            "operationID": str(int(datetime.now().timestamp() * 1000))
        }
        
        try:
            response = requests.post(self.auth_url, json=payload, headers=headers, timeout=10)
            result = response.json()
            
            if result.get("errCode") == 0:
                self.token = result.get("data", {}).get("token")
                print(f"✅ Open-IM 认证成功")
                return True
            else:
                print(f"❌ Open-IM 认证失败: {result.get('errMsg')}")
                return False
        except Exception as e:
            print(f"❌ Open-IM 认证异常: {e}")
            return False
    
    def _send(self, recv_id: str, recv_id_type: str, content: str, 
             content_type: int = 1) -> dict:
        """
        发送消息的底层方法
        
        Args:
            recv_id: 接收者 ID
            recv_id_type: 接收者类型 ("singleChat" 或 "groupChat")
            content: 消息内容
            content_type: 内容类型 (1=text, 5=markdown, 6=card)
        """
        if not self.token:
            print("❌ 未认证，请先调用 authenticate()")
            return {"success": False, "error": "not authenticated"}
        
        params = {"token": self.token}
        payload = {
            "recvID": recv_id,
            "recvIDType": recv_id_type,
            "content": content,
            "contentType": content_type
        }
        
        try:
            response = requests.post(self.send_msg_url, json=payload, params=params, timeout=15)
            result = response.json()
            
            if result.get("errCode") == 0:
                print(f"✅ 消息发送成功")
                return {"success": True, "msg_id": result.get("data", {}).get("serverMsgID")}
            else:
                print(f"❌ 消息发送失败: {result.get('errMsg')}")
                return {"success": False, "error": result.get("errMsg")}
        except Exception as e:
            print(f"❌ 消息发送异常: {e}")
            return {"success": False, "error": str(e)}
    
    def send_text(self, user_id: str, text: str) -> dict:
        """发送文本消息给用户"""
        return self._send(user_id, "singleChat", text, content_type=1)
    
    def send_text_by_name(self, name: str, text: str) -> dict:
        """
        通过名字发送消息（先搜索用户 ID，再发送）
        
        Args:
            name: 用户名字
            text: 消息内容
            
        Returns:
            dict: 发送结果
        """
        user_id = self.find_user_by_name(name)
        if not user_id:
            return {"success": False, "error": f"用户 {name} 未找到"}
        
        return self.send_text(user_id, text)
        """发送文本消息到群"""
        return self._send(group_id, "groupChat", text, content_type=1)
    
    def send_markdown(self, user_id: str, markdown: str) -> dict:
        """发送 Markdown 消息 (contentType=5)"""
        return self._send(user_id, "singleChat", markdown, content_type=5)
    
    def send_test_report(self, user_id: str,
                        task_title: str, task_id: str,
                        total_cases: int, created_cases: int,
                        report_summary: str = "",
                        zentao_url: str = "http://192.168.0.28:9980") -> dict:
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
        
        return self.send_text(user_id, content)
    
    def send_bug_notification(self, user_id: str,
                             bug_id: int, bug_title: str,
                             severity: str, desc: str,
                             zentao_url: str = "http://192.168.0.28:9980") -> dict:
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
        
        return self.send_text(user_id, content)


# ============ 禅道 + Open-IM 工作流 ============

ZENTAO_BASE = "http://192.168.0.28:9980/api.php/v1"
ZENTAO_TOKEN = "cf2da27b8b734b419352d844bc451a14"
ZENTAO_HEADERS = {
    "Token": ZENTAO_TOKEN,
    "Content-Type": "application/json"
}


class ZenTaoOpenIMWorkflow:
    """
    禅道 + Open-IM 工作流
    整合测试用例创建和内部 IM 通知
    """
    
    def __init__(self, openim_host: str = "http://192.168.0.27:10002",
                 secret: str = "openIM123", user_id: str = "imAdmin"):
        self.zentao_base = ZENTAO_BASE
        self.headers = ZENTAO_HEADERS
        self.openim = OpenIMClient(api_host=openim_host)
        # 自动认证
        self.openim.authenticate(secret=secret, user_id=user_id)
    
    def create_test_case(self, title: str, pri: int = 3, 
                        steps: List[dict] = None,
                        type_: str = "feature",
                        product_id: int = 2) -> Optional[int]:
        """创建测试用例"""
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
    
    def batch_create_cases(self, cases: List[dict], 
                          product_id: int = 2) -> dict:
        """批量创建测试用例"""
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
            cases: List[dict] = None,
            report_summary: str = "",
            product_id: int = 2,
            recv_user_id: str = "user001") -> dict:
        """
        运行完整工作流：创建用例 → Open-IM 通知
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
        notify_result = self.openim.send_test_report(
            user_id=recv_user_id,
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
            "success": create_result["success"] > 0 and notify_result.get("success"),
            "cases_created": create_result["success"],
            "cases_failed": create_result["failed"],
            "im_notified": notify_result.get("success", False)
        }


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="禅道测试工作流 + Open-IM 通知")
    parser.add_argument("--task-id", type=str, required=True, help="禅道任务 ID")
    parser.add_argument("--task-title", type=str, required=True, help="任务标题")
    parser.add_argument("--case-count", type=int, default=5, help="生成用例数量")
    parser.add_argument("--product-id", type=int, default=2, help="产品 ID")
    parser.add_argument("--openim-host", type=str, default="http://192.168.0.27:10002", 
                       help="Open-IM 主机地址")
    parser.add_argument("--secret", type=str, default="openIM123", help="认证密钥")
    parser.add_argument("--recv", type=str, required=True, help="接收者用户 ID")
    
    args = parser.parse_args()
    
    # 示例用例
    sample_cases = [
        {
            "title": f"测试用例-{i}",
            "pri": 3,
            "steps": [{"desc": f"步骤{i}.1", "expect": f"预期{i}.1"}],
            "type": "feature"
        }
        for i in range(1, args.case_count + 1)
    ]
    
    workflow = ZenTaoOpenIMWorkflow(
        openim_host=args.openim_host,
        secret=args.secret
    )
    result = workflow.run(
        task_title=args.task_title,
        task_id=args.task_id,
        cases=sample_cases,
        recv_user_id=args.recv
    )
    
    print(f"\n执行结果: {json.dumps(result, ensure_ascii=False, indent=2)}")


if __name__ == "__main__":
    main()
