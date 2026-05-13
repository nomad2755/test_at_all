#!/usr/bin/env python3
"""
Bug 截图管理工具
功能：
1. 上传截图到 bug_screenshots 目录
2. 自动同步到 Jenkins UserContent（公网可访问）
3. 生成禅道可用的图片 URL
4. 列出所有截图
5. 删除截图

用法：
  python3 bug_screenshot_manager.py upload <图片路径> [描述]
  python3 bug_screenshot_manager.py list
  python3 bug_screenshot_manager.py delete <文件名>
  python3 bug_screenshot_manager.py url <文件名>
"""

import os
import sys
import json
import uuid
import shutil
import argparse
from datetime import datetime
from pathlib import Path

# === 配置 ===
LOCAL_DIR = "/root/.openclaw/workspace/bug_screenshots"
JENKINS_DIR = "/opt/jenkins_home/userContent/bug_screenshots"
METADATA_FILE = "/root/.openclaw/workspace/bug_screenshots/metadata.json"

# Jenkins 公网地址（需要根据实际情况修改）
JENKINS_PUBLIC_URL = "http://120.202.35.151:10240"

# 确保目录存在
os.makedirs(LOCAL_DIR, exist_ok=True)
os.makedirs(JENKINS_DIR, exist_ok=True)


def load_metadata():
    """加载元数据"""
    if os.path.exists(METADATA_FILE):
        with open(METADATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"screenshots": []}


def save_metadata(metadata):
    """保存元数据"""
    with open(METADATA_FILE, "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)


def upload_screenshot(image_path, description=""):
    """上传截图"""
    if not os.path.exists(image_path):
        print(f"错误：文件不存在: {image_path}")
        return None

    # 生成唯一文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    ext = os.path.splitext(image_path)[1].lower()
    if ext not in [".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp"]:
        ext = ".png"
    
    unique_id = str(uuid.uuid4())[:8]
    filename = f"{timestamp}_{unique_id}{ext}"
    
    # 复制到本地目录
    local_path = os.path.join(LOCAL_DIR, filename)
    shutil.copy2(image_path, local_path)
    
    # 复制到 Jenkins 目录（公网访问）
    jenkins_path = os.path.join(JENKINS_DIR, filename)
    shutil.copy2(image_path, jenkins_path)
    
    # 更新元数据
    metadata = load_metadata()
    record = {
        "filename": filename,
        "original_name": os.path.basename(image_path),
        "description": description,
        "local_path": local_path,
        "jenkins_url": f"{JENKINS_PUBLIC_URL}/userContent/bug_screenshots/{filename}",
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    metadata["screenshots"].insert(0, record)  # 最新在前
    save_metadata(metadata)
    
    return record


def list_screenshots():
    """列出所有截图"""
    metadata = load_metadata()
    if not metadata["screenshots"]:
        print("暂无截图")
        return
    
    print(f"\n{'='*80}")
    print(f"{'文件名':<40} {'描述':<20} {'上传时间':<20}")
    print(f"{'-'*80}")
    for item in metadata["screenshots"][:50]:  # 只显示前50条
        desc = item.get("description", "")[:18]
        print(f"{item['filename']:<40} {desc:<20} {item['created_at']:<20}")
    print(f"{'='*80}")
    print(f"共 {len(metadata['screenshots'])} 张截图")


def get_url(filename):
    """获取指定截图的 URL"""
    metadata = load_metadata()
    for item in metadata["screenshots"]:
        if item["filename"] == filename:
            return item["jenkins_url"]
    return None


def delete_screenshot(filename):
    """删除截图"""
    metadata = load_metadata()
    record = None
    for item in metadata["screenshots"]:
        if item["filename"] == filename:
            record = item
            break
    
    if not record:
        print(f"错误：找不到截图: {filename}")
        return False
    
    # 删除文件
    try:
        if os.path.exists(record["local_path"]):
            os.remove(record["local_path"])
        if os.path.exists(record["jenkins_url"].replace(JENKINS_PUBLIC_URL, "/opt/jenkins_home/userContent")):
            os.remove(record["jenkins_url"].replace(JENKINS_PUBLIC_URL, "/opt/jenkins_home/userContent"))
    except Exception as e:
        print(f"警告：删除文件失败: {e}")
    
    # 更新元数据
    metadata["screenshots"] = [s for s in metadata["screenshots"] if s["filename"] != filename]
    save_metadata(metadata)
    
    print(f"已删除: {filename}")
    return True


def main():
    parser = argparse.ArgumentParser(description="Bug 截图管理工具")
    subparsers = parser.add_subparsers(dest="command", help="子命令")
    
    # upload 命令
    upload_parser = subparsers.add_parser("upload", help="上传截图")
    upload_parser.add_argument("image_path", help="图片路径")
    upload_parser.add_argument("description", nargs="?", default="", help="描述（可选）")
    
    # list 命令
    subparsers.add_parser("list", help="列出所有截图")
    
    # url 命令
    url_parser = subparsers.add_parser("url", help="获取截图URL")
    url_parser.add_argument("filename", help="文件名")
    
    # delete 命令
    delete_parser = subparsers.add_parser("delete", help="删除截图")
    delete_parser.add_argument("filename", help="文件名")
    
    args = parser.parse_args()
    
    if args.command == "upload":
        result = upload_screenshot(args.image_path, args.description)
        if result:
            print(f"\n✅ 上传成功！")
            print(f"   文件: {result['filename']}")
            print(f"   描述: {result['description']}")
            print(f"   访问URL: {result['jenkins_url']}")
    elif args.command == "list":
        list_screenshots()
    elif args.command == "url":
        url = get_url(args.filename)
        if url:
            print(url)
        else:
            print(f"错误：找不到截图: {args.filename}")
    elif args.command == "delete":
        delete_screenshot(args.filename)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
