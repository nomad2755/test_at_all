#!/usr/bin/env python3
"""
钉钉通知模块
用于发送测试报告、Bug 通知等到钉钉群
"""

import json
import hmac
import hashlib
import base64
import time
import requests
from datetime import datetime
from typing import Optional


class DingTalkSender:
    """钉钉通知发送器"""
    
    def __init__(self, webhook_url: str, secret: str = ""):
        """
        初始化钉钉发送器
        
        Args:
            webhook_url: 钉钉 Webhook 地址
            secret: 加签密钥（可选）
        """
        self.webhook_url = webhook_url
        self.secret = secret
    
    def _sign(self) -> str:
        """生成加签签名"""
        if not self.secret:
            return ""
        
        timestamp = str(round(time.time() * 1000))
        secret_enc = self.secret.encode('utf-8')
        string_to_sign = f'{timestamp}\n{self.secret}'
        string_to_sign_enc = string_to_sign.encode('utf-8')
        hmac_code = hmac.new(secret_enc, string_to_sign_enc, digestmod=hashlib.sha256).digest()
        sign = base64.b64encode(hmac_code).decode('utf-8')
        
        # URL 编码签名
        import urllib.parse
        return urllib.parse.quote_plus(sign)
    
    def send(self, msgtype: str, content: dict) -> bool:
        """
        发送消息到钉钉群
        
        Args:
            msgtype: 消息类型 (text/markdown/link/actionCard)
            content: 消息内容
            
        Returns:
            bool: 发送是否成功
        """
        # 如果有加签，追加时间戳和签名
        url = self.webhook_url
        if self.secret:
            sign = self._sign()
            separator = "&" if "?" in url else "?"
            url = f"{url}{separator}timestamp={int(time.time() * 1000)}&sign={sign}"
        
        payload = {
            "msgtype": msgtype
        }
        payload.update(content)
        
        try:
            response = requests.post(url, json=payload, timeout=10)
            result = response.json()
            
            if result.get("errcode") == 0:
                return True
            else:
                print(f"发送失败: {result.get('errmsg')}")
                return False
        except Exception as e:
            print(f"发送异常: {e}")
            return False
    
    def send_text(self, content: str, at_mobiles: list = None) -> bool:
        """发送文本消息"""
        data = {
            "text": {"content": content},
            "at": {"atMobiles": at_mobiles or [], "isAtAll": False}
        }
        return self.send("text", data)
    
    def send_markdown(self, title: str, text: str) -> bool:
        """发送 Markdown 消息"""
        data = {
            "markdown": {"title": title, "text": text}
        }
        return self.send("markdown", data)
    
    def send_link(self, title: str, text: str, message_url: str, pic_url: str = "") -> bool:
        """发送链接消息"""
        data = {
            "link": {
                "title": title,
                "text": text,
                "messageUrl": message_url,
                "picUrl": pic_url
            }
        }
        return self.send("link", data)
    
    def send_action_card(self, title: str, text: str, 
                        single_title: str = "", single_url: str = "",
                        btn_orientation: str = "0") -> bool:
        """
        发送 ActionCard 消息
        
        Args:
            single_title: 跳转按钮标题（为空则显示两个按钮）
            single_url: 按钮跳转链接
            btn_orientation: 0-竖直排列 1-横向排列
        """
        if single_title:
            data = {
                "actionCard": {
                    "title": title,
                    "text": text,
                    "singleTitle": single_title,
                    "singleURL": single_url,
                    "btnOrientation": btn_orientation
                }
            }
        else:
            data = {
                "actionCard": {
                    "title": title,
                    "text": text,
                    "btnOrientation": btn_orientation
                }
            }
        return self.send("actionCard", data)


def create_test_report_message(task_id: str, task_title: str,
                               total: int, passed: int, failed: int,
                               zentao_url: str = "http://192.168.0.28:9980") -> tuple:
    """
    创建测试报告 Markdown 消息
    
    Returns:
        (title, text) 元组
    """
    pass_rate = (passed / total * 100) if total > 0 else 0
    
    title = f"测试报告 | {task_title[:20]}..."
    
    text = f"""# 测试报告 📋

> 任务: **{task_title}**
> 时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}

## 📊 执行统计

| 指标 | 数值 |
|------|------|
| 总用例数 | {total} |
| 通过 | ✅ {passed} |
| 失败 | ❌ {failed} |
| 通过率 | {pass_rate:.1f}% |

## 🔗 快速链接

- 禅道任务: [点击查看]({zentao_url}/task-view-{task_id}.html)
- 测试报告: [点击查看]({zentao_url}/testreport-view-{task_id}.html)

---

*🤖 由测试助手自动生成 | {datetime.now().strftime('%Y-%m-%d')}*"""
    
    return title, text


def create_bug_notification_message(bug_id: int, bug_title: str,
                                   severity: str, desc: str,
                                   zentao_url: str = "http://192.168.0.28:9980") -> tuple:
    """
    创建 Bug 通知 Markdown 消息
    """
    severity_map = {"1": "🔴 致命", "2": "🟠 严重", "3": "🟡 一般", "4": "🔵 优化"}
    
    title = f"🐛 新建 Bug: {bug_title[:25]}..."
    
    text = f"""# 🐛 Bug 报告

## 基本信息

| 字段 | 值 |
|------|-----|
| Bug ID | [{bug_id}]({zentao_url}/bug-view-{bug_id}.html) |
| 标题 | {bug_title} |
| 严重程度 | {severity_map.get(severity, severity)} |
| 状态 | 🟡 待处理 |

## 问题描述

{desc}

## 复现步骤

1. 打开页面
2. 执行操作
3. 观察异常

---

*🤖 由测试助手自动创建 | {datetime.now().strftime('%Y-%m-%d %H:%M')}*"""
    
    return title, text


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="钉钉通知发送工具")
    parser.add_argument("--webhook", required=True, help="钉钉 Webhook URL")
    parser.add_argument("--secret", default="", help="加签密钥")
    parser.add_argument("--type", choices=["text", "markdown", "link", "report", "bug"], 
                       default="markdown", help="消息类型")
    parser.add_argument("--title", default="", help="消息标题")
    parser.add_argument("--content", default="", help="消息内容")
    parser.add_argument("--task-id", help="禅道任务 ID（用于生成报告链接）")
    parser.add_argument("--task-title", help="任务标题")
    
    args = parser.parse_args()
    
    sender = DingTalkSender(args.webhook, args.secret)
    
    if args.type == "text":
        sender.send_text(args.content)
    elif args.type == "markdown":
        sender.send_markdown(args.title, args.content)
    elif args.type == "report":
        title, text = create_test_report_message(
            task_id=args.task_id or "0",
            task_title=args.task_title or "测试任务",
            total=10, passed=8, failed=2
        )
        sender.send_markdown(title, text)
    elif args.type == "bug":
        title, text = create_bug_notification_message(
            bug_id=1001,
            bug_title=args.title or "测试 Bug",
            severity="3",
            desc=args.content or "Bug 描述"
        )
        sender.send_markdown(title, text)
    
    print("✅ 消息发送完成")


if __name__ == "__main__":
    main()
