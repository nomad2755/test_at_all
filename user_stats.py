#!/usr/bin/env python3
"""
OpenClaw用户使用情况统计脚本 - 支持JSON输出
"""

import json
import os
import glob
from datetime import datetime, timedelta
from collections import defaultdict
import re
import sys
import argparse

def parse_timestamp(timestamp_str):
    """解析时间戳字符串"""
    try:
        return datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
    except:
        try:
            return datetime.strptime(timestamp_str, '%Y-%m-%dT%H:%M:%S.%fZ')
        except:
            return None

def extract_username(content):
    """从消息内容提取用户名"""
    if isinstance(content, str):
        text = content
    elif isinstance(content, list):
        text_parts = []
        for item in content:
            if isinstance(item, dict) and item.get('type') == 'text':
                text_parts.append(item.get('text', ''))
        text = '\n'.join(text_parts)
    else:
        return 'unknown'
    
    # 查找username字段
    patterns = [
        r'"username"\s*:\s*"([^"]+)"',
        r'"name"\s*:\s*"([^"]+)"',
        r'username:\s*([^\s,]+)',
        r'用户:\s*([^\s,]+)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(1)
    
    return 'unknown'

def analyze_stats(sessions_dir):
    """分析使用统计"""
    today = datetime.now().date()
    week_ago = today - timedelta(days=7)
    
    stats = {
        'global': {
            'total_sessions': 0,
            'total_questions': 0,
            'total_duration': 0,
            'recent_sessions': 0,
            'recent_questions': 0,
            'recent_duration': 0,
            'today_sessions': 0,
            'today_questions': 0,
            'today_duration': 0,
            'user_count': 0,
            'analysis_time': datetime.now().isoformat(),
            'server_ip': os.uname().nodename
        },
        'users': {}
    }
    
    session_files = glob.glob(os.path.join(sessions_dir, '*.jsonl'))
    
    user_stats = defaultdict(lambda: {
        'total_sessions': 0,
        'total_questions': 0,
        'total_duration': 0,
        'recent_sessions': 0,
        'recent_questions': 0,
        'recent_duration': 0,
        'today_sessions': 0,
        'today_questions': 0,
        'today_duration': 0
    })
    
    for filepath in session_files:
        session_users = set()
        user_messages = []
        session_start = None
        session_end = None
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        record = json.loads(line.strip())
                        ts_str = record.get('timestamp')
                        if not ts_str:
                            continue
                        
                        ts = parse_timestamp(ts_str)
                        if not ts:
                            continue
                        
                        # 更新会话时间
                        if not session_start or ts < session_start:
                            session_start = ts
                        if not session_end or ts > session_end:
                            session_end = ts
                        
                        if record.get('type') == 'message':
                            msg = record.get('message', {})
                            if msg.get('role') == 'user':
                                username = extract_username(msg.get('content', ''))
                                session_users.add(username)
                                user_messages.append({
                                    'username': username,
                                    'timestamp': ts
                                })
                                
                    except json.JSONDecodeError:
                        continue
                        
        except Exception as e:
            print(f"警告: 读取文件失败 {filepath}: {e}", file=sys.stderr)
            continue
        
        if not user_messages:
            continue
        
        # 计算会话时长
        duration = 0
        if session_start and session_end:
            duration = max(0, (session_end - session_start).total_seconds())
        
        session_date = session_start.date() if session_start else None
        is_recent = session_date and session_date >= week_ago
        is_today = session_date == today
        
        # 按用户统计
        for username in session_users:
            user_questions = len([m for m in user_messages if m['username'] == username])
            
            user_stats[username]['total_sessions'] += 1
            user_stats[username]['total_questions'] += user_questions
            user_stats[username]['total_duration'] += duration
            
            if is_recent:
                user_stats[username]['recent_sessions'] += 1
                user_stats[username]['recent_questions'] += user_questions
                user_stats[username]['recent_duration'] += duration
            
            if is_today:
                user_stats[username]['today_sessions'] += 1
                user_stats[username]['today_questions'] += user_questions
                user_stats[username]['today_duration'] += duration
        
        # 全局统计
        stats['global']['total_sessions'] += 1
        stats['global']['total_questions'] += len(user_messages)
        stats['global']['total_duration'] += duration
        
        if is_recent:
            stats['global']['recent_sessions'] += 1
            stats['global']['recent_questions'] += len(user_messages)
            stats['global']['recent_duration'] += duration
        
        if is_today:
            stats['global']['today_sessions'] += 1
            stats['global']['today_questions'] += len(user_messages)
            stats['global']['today_duration'] += duration
    
    stats['global']['user_count'] = len(user_stats)
    stats['users'] = dict(user_stats)
    
    return stats

def format_time(seconds):
    """格式化时间"""
    if seconds < 60:
        return f"{seconds:.0f}秒"
    elif seconds < 3600:
        return f"{seconds/60:.1f}分钟"
    elif seconds < 86400:
        return f"{seconds/3600:.1f}小时"
    else:
        return f"{seconds/86400:.1f}天"

def print_report(stats):
    """打印报告"""
    g = stats['global']
    
    print("\n" + "="*80)
    print("OpenClaw 使用情况统计报告")
    print("="*80)
    print(f"服务器: {g.get('server_ip', '未知')}")
    print(f"分析时间: {g.get('analysis_time', '未知')}")
    print(f"总用户数: {g['user_count']}")
    print()
    
    print("【全局统计】")
    print("-"*60)
    print(f"总会话总数: {g['total_sessions']}")
    print(f"总提问总数: {g['total_questions']}")
    print(f"总会话时长: {format_time(g['total_duration'])}")
    print()
    print(f"最近一周会话总数: {g['recent_sessions']}")
    print(f"最近一周提问总数: {g['recent_questions']}")
    print(f"最近一周会话时长: {format_time(g['recent_duration'])}")
    print()
    print(f"今日会话总数: {g['today_sessions']}")
    print(f"今日提问总数: {g['today_questions']}")
    print(f"今日会话时长: {format_time(g['today_duration'])}")
    print()
    
    print("【按用户统计】")
    print("-"*60)
    print(f"{'用户名':<20} {'总会话':<8} {'总提问':<8} {'总时长':<12} {'近7天会话':<10} {'近7天提问':<10} {'今日会话':<8} {'今日提问':<8}")
    print("-"*60)
    
    # 按总提问数排序
    sorted_users = sorted(stats['users'].items(), key=lambda x: x[1]['total_questions'], reverse=True)
    
    for username, u in sorted_users:
        print(f"{username:<20} "
              f"{u['total_sessions']:<8} "
              f"{u['total_questions']:<8} "
              f"{format_time(u['total_duration']):<12} "
              f"{u['recent_sessions']:<10} "
              f"{u['recent_questions']:<10} "
              f"{u['today_sessions']:<8} "
              f"{u['today_questions']:<8}")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='OpenClaw使用情况统计')
    parser.add_argument('--json', action='store_true', help='输出JSON格式')
    parser.add_argument('--sessions-dir', default='/root/.openclaw/agents/main/sessions',
                       help='会话目录路径')
    
    args = parser.parse_args()
    
    # 自动检测会话目录
    sessions_dir = args.sessions_dir
    if not os.path.exists(sessions_dir):
        home_dir = os.path.expanduser('~')
        sessions_dir = os.path.join(home_dir, '.openclaw/agents/main/sessions')
        
        if not os.path.exists(sessions_dir):
            print(f"错误: 会话目录不存在: {sessions_dir}", file=sys.stderr)
            sys.exit(1)
    
    stats = analyze_stats(sessions_dir)
    
    if args.json:
        # 输出JSON格式
        print(json.dumps(stats, ensure_ascii=False, indent=2, default=str))
    else:
        # 输出文本报告
        print_report(stats)

if __name__ == "__main__":
    main()