#!/usr/bin/env python3
"""
OpenClaw用户使用情况统计脚本 - 智能分段统计版本
超过1小时无活动，自动分割为新会话
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

def calculate_duration_smart(timestamps, gap_minutes=30):
    """
    智能计算会话时长：超过30分钟无活动则分割

    Args:
        timestamps: 时间戳列表（已排序）
        gap_minutes: 分割阈值（分钟），默认30分钟
    
    Returns:
        实际使用时长（秒）
    """
    if len(timestamps) < 2:
        return 0
    
    # 按时间排序
    timestamps_sorted = sorted(timestamps)
    
    # 计算有效时长
    total_duration = 0
    segment_start = timestamps_sorted[0]
    prev_timestamp = timestamps_sorted[0]
    
    for i in range(1, len(timestamps_sorted)):
        current_ts = timestamps_sorted[i]
        gap = (current_ts - prev_timestamp).total_seconds()
        
        # 超过阈值，结束当前段
        if gap > gap_minutes * 60:
            segment_duration = (prev_timestamp - segment_start).total_seconds()
            total_duration += max(0, segment_duration)
            segment_start = current_ts
        
        prev_timestamp = current_ts
    
    # 加上最后一段
    final_duration = (prev_timestamp - segment_start).total_seconds()
    total_duration += max(0, final_duration)
    
    return total_duration

def calculate_session_lifespan(timestamps):
    """
    计算会话存活时间（从第一条到最后一条记录）
    
    Args:
        timestamps: 时间戳列表
    
    Returns:
        会话存活时间（秒）
    """
    if len(timestamps) < 2:
        return 0
    
    timestamps_sorted = sorted(timestamps)
    return (timestamps_sorted[-1] - timestamps_sorted[0]).total_seconds()

def analyze_stats(sessions_dir, gap_minutes=30, target_date=None):
    """
    分析使用统计
    
    Args:
        sessions_dir: 会话目录路径
        gap_minutes: 分段阈值（分钟），默认30分钟
        target_date: 目标统计日期，格式 YYYY-MM-DD，默认为今天
    """
    if target_date:
        # 解析传入的日期
        if isinstance(target_date, str):
            target_date = datetime.strptime(target_date, '%Y-%m-%d').date()
        today = target_date
    else:
        today = datetime.now().date()
    
    week_ago = today - timedelta(days=7)
    
    stats = {
        'global': {
            'total_sessions': 0,
            'total_questions': 0,
            'total_duration': 0,           # 智能分段统计的实际使用时长
            'total_lifespan': 0,            # 会话存活时间
            'recent_sessions': 0,
            'recent_questions': 0,
            'recent_duration': 0,
            'recent_lifespan': 0,
            'today_sessions': 0,
            'today_questions': 0,
            'today_duration': 0,
            'today_lifespan': 0,
            'user_count': 0,
            'analysis_time': datetime.now().isoformat(),
            'server_ip': os.uname().nodename,
            'gap_minutes': gap_minutes,
            'target_date': str(today)
        },
        'users': {}
    }
    
    # 收集所有会话文件
    all_files = glob.glob(os.path.join(sessions_dir, '*.jsonl*'))
    # 排除trajectory文件
    all_files = [f for f in all_files if 'trajectory' not in f]
    
    # 按会话ID分组（文件名去掉.jsonl后缀）
    session_groups = defaultdict(list)
    for filepath in all_files:
        filename = os.path.basename(filepath)
        # 提取会话ID：8c393295-235b-4e9d-9a03-a68d52fae1b4
        session_id = filename.split('.')[0]
        session_groups[session_id].append(filepath)
    
    # 对每个会话，选择优先级最高的文件
    # 优先级: 主文件 > .reset文件 > checkpoint文件
    session_files = []
    for session_id, files in session_groups.items():
        # 按文件类型排序
        main_files = [f for f in files if '.reset.' not in f and '.checkpoint.' not in f and '.deleted.' not in f]
        reset_files = [f for f in files if '.reset.' in f]
        deleted_files = [f for f in files if '.deleted.' in f]
        checkpoint_files = [f for f in files if '.checkpoint.' in f]
        
        # 选择优先级最高的文件
        # OpenClaw自身的成本统计也包含了.deleted和.reset文件
        # 参考: session-cost-usage-DsNok5Xd.js
        # 优先级: 主文件 > .reset文件 > .deleted文件 > checkpoint文件
        if main_files:
            selected = max(main_files, key=os.path.getsize)
        elif reset_files:
            selected = max(reset_files, key=os.path.getmtime)
        elif deleted_files:
            selected = max(deleted_files, key=os.path.getmtime)
        else:
            selected = max(checkpoint_files, key=os.path.getmtime)
        
        session_files.append(selected)
    
    user_stats = defaultdict(lambda: {
        'total_sessions': 0,
        'total_questions': 0,
        'total_duration': 0,
        'total_lifespan': 0,
        'recent_sessions': 0,
        'recent_questions': 0,
        'recent_duration': 0,
        'recent_lifespan': 0,
        'today_sessions': 0,
        'today_questions': 0,
        'today_duration': 0,
        'today_lifespan': 0
    })
    
    for filepath in session_files:
        session_users = set()
        user_messages = []
        all_timestamps = []
        
        # 为每个用户单独收集时间戳（修复重复计算问题）
        user_timestamps = defaultdict(list)
        
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
                        
                        all_timestamps.append(ts)
                        
                        if record.get('type') == 'message':
                            msg = record.get('message', {})
                            if msg.get('role') == 'user':
                                username = extract_username(msg.get('content', ''))
                                session_users.add(username)
                                user_messages.append({
                                    'username': username,
                                    'timestamp': ts
                                })
                                # 为该用户记录时间戳
                                user_timestamps[username].append(ts)
                                
                    except json.JSONDecodeError:
                        continue
                        
        except Exception as e:
            print(f"警告: 读取文件失败 {filepath}: {e}", file=sys.stderr)
            continue
        
        if not user_messages:
            continue
        
        # 计算会话时长（智能分段统计）
        duration_smart = calculate_duration_smart(all_timestamps, gap_minutes)
        
        # 计算会话存活时间（原有方法）
        duration_lifespan = calculate_session_lifespan(all_timestamps)
        
        # 只使用今天的时间戳计算今日时长（修复）
        today_timestamps = [ts for ts in all_timestamps if ts.date() == today]
        today_duration_smart = calculate_duration_smart(today_timestamps, gap_minutes) if len(today_timestamps) >= 2 else 0
        today_duration_lifespan = calculate_session_lifespan(today_timestamps) if len(today_timestamps) >= 2 else 0
        
        # 只使用最近一周的时间戳计算最近一周时长（修复）
        recent_timestamps = [ts for ts in all_timestamps if ts.date() >= week_ago]
        recent_duration_smart = calculate_duration_smart(recent_timestamps, gap_minutes) if len(recent_timestamps) >= 2 else 0
        recent_duration_lifespan = calculate_session_lifespan(recent_timestamps) if len(recent_timestamps) >= 2 else 0
        
        # 使用第一条用户消息的时间作为会话开始时间（用于总统计）
        session_date = user_messages[0]['timestamp'].date() if user_messages else None
        is_recent = session_date and session_date >= week_ago
        
        # 统计今天的消息（修复：检查每条消息是否为今天，而不是只看第一条）
        today_user_messages = [m for m in user_messages if m['timestamp'].date() == today]
        recent_user_messages = [m for m in user_messages if m['timestamp'].date() >= week_ago]
        
        is_today = len(today_user_messages) > 0
        has_recent = len(recent_user_messages) > 0
        
        # 按用户统计
        for username in session_users:
            user_questions = len([m for m in user_messages if m['username'] == username])
            
            user_stats[username]['total_sessions'] += 1
            user_stats[username]['total_questions'] += user_questions
            user_stats[username]['total_duration'] += duration_smart
            user_stats[username]['total_lifespan'] += duration_lifespan
            
            # 为每个用户单独计算时长（修复重复计算问题）
            user_ts = user_timestamps[username]
            user_recent_ts = [ts for ts in user_ts if ts.date() >= week_ago]
            user_today_ts = [ts for ts in user_ts if ts.date() == today]
            
            # 最近一周统计（修复：使用用户自己的时间戳计算时长）
            user_recent_questions = len([m for m in user_messages if m['username'] == username and m['timestamp'].date() >= week_ago])
            if user_recent_questions > 0:
                user_stats[username]['recent_sessions'] += 1
                user_stats[username]['recent_questions'] += user_recent_questions
                user_stats[username]['recent_duration'] += calculate_duration_smart(user_recent_ts, gap_minutes) if len(user_recent_ts) >= 2 else 0
                user_stats[username]['recent_lifespan'] += calculate_session_lifespan(user_recent_ts) if len(user_recent_ts) >= 2 else 0
            
            # 今日统计（修复：使用用户自己的时间戳计算时长）
            user_today_questions = len([m for m in user_messages if m['username'] == username and m['timestamp'].date() == today])
            if user_today_questions > 0:
                user_stats[username]['today_sessions'] += 1
                user_stats[username]['today_questions'] += user_today_questions
                user_stats[username]['today_duration'] += calculate_duration_smart(user_today_ts, gap_minutes) if len(user_today_ts) >= 2 else 0
                user_stats[username]['today_lifespan'] += calculate_session_lifespan(user_today_ts) if len(user_today_ts) >= 2 else 0
        
        # 全局统计
        stats['global']['total_sessions'] += 1
        stats['global']['total_questions'] += len(user_messages)
        stats['global']['total_duration'] += duration_smart
        stats['global']['total_lifespan'] += duration_lifespan
        
        if has_recent:
            stats['global']['recent_sessions'] += 1
            stats['global']['recent_questions'] += len(recent_user_messages)
            stats['global']['recent_duration'] += recent_duration_smart
            stats['global']['recent_lifespan'] += recent_duration_lifespan
        
        if is_today:
            stats['global']['today_sessions'] += 1
            stats['global']['today_questions'] += len(today_user_messages)
            stats['global']['today_duration'] += today_duration_smart
            stats['global']['today_lifespan'] += today_duration_lifespan
    
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
    gap_minutes = g.get('gap_minutes', 30)
    target_date_str = g.get('target_date', str(datetime.now().date()))
    
    # 判断是否是今天
    is_today = target_date_str == str(datetime.now().date())
    date_label = "今日" if is_today else f"日期 ({target_date_str})"
    
    print("\n" + "="*80)
    print("OpenClaw 使用情况统计报告（智能分段统计）")
    print("="*80)
    print(f"服务器: {g.get('server_ip', '未知')}")
    print(f"分析时间: {g.get('analysis_time', '未知')}")
    print(f"总用户数: {g['user_count']}")
    print(f"分段阈值: {gap_minutes}分钟（超过此时间无活动则自动分割）")
    print()
    
    print("【全局统计】")
    print("-"*60)
    print(f"总会话总数: {g['total_sessions']}")
    print(f"总提问总数: {g['total_questions']}")
    print(f"实际使用时长: {format_time(g['total_duration'])}  ✓（智能分段统计）")
    print(f"会话存活时间: {format_time(g['total_lifespan'])}  （会话时间跨度）")
    print()
    print(f"最近一周会话总数: {g['recent_sessions']}")
    print(f"最近一周提问总数: {g['recent_questions']}")
    print(f"最近一周实际使用时长: {format_time(g['recent_duration'])}")
    print()
    print(f"{date_label}会话总数: {g['today_sessions']}")
    print(f"{date_label}提问总数: {g['today_questions']}")
    print(f"{date_label}实际使用时长: {format_time(g['today_duration'])}")
    print()
    
    print("【按用户统计】")
    print("-"*60)
    print(f"{'用户名':<20} {'总会话':<8} {'总提问':<8} {'使用时长':<12} {'近7天会话':<10} {'近7天提问':<10} {date_label+'会话':<10} {date_label+'提问':<10}")
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
    parser = argparse.ArgumentParser(description='OpenClaw使用情况统计 - 智能分段统计版本')
    parser.add_argument('--json', action='store_true', help='输出JSON格式')
    parser.add_argument('--sessions-dir', default='/root/.openclaw/agents/main/sessions',
                       help='会话目录路径')
    parser.add_argument('--gap-minutes', type=int, default=30,
                       help='分段阈值（分钟），默认30分钟')
    parser.add_argument('--date', type=str, default=None,
                       help='统计日期，格式 YYYY-MM-DD，默认为今天')
    
    args = parser.parse_args()
    
    # 自动检测会话目录
    sessions_dir = args.sessions_dir
    if not os.path.exists(sessions_dir):
        home_dir = os.path.expanduser('~')
        sessions_dir = os.path.join(home_dir, '.openclaw/agents/main/sessions')
        
        if not os.path.exists(sessions_dir):
            print(f"错误: 会话目录不存在: {sessions_dir}", file=sys.stderr)
            sys.exit(1)
    
    stats = analyze_stats(sessions_dir, args.gap_minutes, args.date)
    
    if args.json:
        # 输出JSON格式
        print(json.dumps(stats, ensure_ascii=False, indent=2, default=str))
    else:
        # 输出文本报告
        print_report(stats)

if __name__ == "__main__":
    main()
