from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from database import get_db, dict_from_row

reports_bp = Blueprint('reports', __name__)

@reports_bp.route('/reports/weekly', methods=['GET'])
def get_weekly_report():
    """週次レポートを取得"""
    conn = get_db()
    cursor = conn.cursor()
    
    # 今週の開始日（月曜日）と終了日（日曜日）を計算
    today = datetime.now()
    week_start = today - timedelta(days=today.weekday())
    week_end = week_start + timedelta(days=6)
    
    week_start_str = week_start.strftime('%Y-%m-%d')
    week_end_str = week_end.strftime('%Y-%m-%d')
    
    # 今週完了したタスク
    cursor.execute('''
        SELECT * FROM tasks
        WHERE date(completed_at) BETWEEN ? AND ?
        ORDER BY completed_at DESC
    ''', (week_start_str, week_end_str))
    completed_tasks = [dict_from_row(row) for row in cursor.fetchall()]
    
    # 今週作成されたタスク
    cursor.execute('''
        SELECT COUNT(*) as count FROM tasks
        WHERE date(created_at) BETWEEN ? AND ?
    ''', (week_start_str, week_end_str))
    created_count = cursor.fetchone()['count']
    
    # 現在進行中のタスク
    cursor.execute('''
        SELECT COUNT(*) as count FROM tasks
        WHERE status = 'in_progress'
    ''')
    in_progress_count = cursor.fetchone()['count']
    
    # ステータス別のタスク数
    cursor.execute('''
        SELECT status, COUNT(*) as count FROM tasks
        GROUP BY status
    ''')
    status_counts = {row['status']: row['count'] for row in cursor.fetchall()}
    
    # 日別完了タスク数（今週）
    cursor.execute('''
        SELECT date(completed_at) as date, COUNT(*) as count
        FROM tasks
        WHERE date(completed_at) BETWEEN ? AND ?
        GROUP BY date(completed_at)
        ORDER BY date
    ''', (week_start_str, week_end_str))
    daily_completed = {row['date']: row['count'] for row in cursor.fetchall()}
    
    # 全日付のデータを生成
    daily_data = []
    for i in range(7):
        day = week_start + timedelta(days=i)
        day_str = day.strftime('%Y-%m-%d')
        daily_data.append({
            'date': day_str,
            'day_name': ['月', '火', '水', '木', '金', '土', '日'][i],
            'count': daily_completed.get(day_str, 0)
        })
    
    conn.close()
    
    return jsonify({
        'period': {
            'start': week_start_str,
            'end': week_end_str
        },
        'completed_tasks': completed_tasks,
        'completed_count': len(completed_tasks),
        'created_count': created_count,
        'in_progress_count': in_progress_count,
        'status_counts': status_counts,
        'daily_data': daily_data
    })

@reports_bp.route('/reports/monthly', methods=['GET'])
def get_monthly_report():
    """月次レポートを取得"""
    conn = get_db()
    cursor = conn.cursor()
    
    # 指定月またはデフォルトで今月
    year = request.args.get('year', datetime.now().year, type=int)
    month = request.args.get('month', datetime.now().month, type=int)
    
    month_start = datetime(year, month, 1)
    month_end = month_start + relativedelta(months=1) - timedelta(days=1)
    
    month_start_str = month_start.strftime('%Y-%m-%d')
    month_end_str = month_end.strftime('%Y-%m-%d')
    
    # 今月完了したタスク数
    cursor.execute('''
        SELECT COUNT(*) as count FROM tasks
        WHERE date(completed_at) BETWEEN ? AND ?
    ''', (month_start_str, month_end_str))
    completed_count = cursor.fetchone()['count']
    
    # 今月作成されたタスク数
    cursor.execute('''
        SELECT COUNT(*) as count FROM tasks
        WHERE date(created_at) BETWEEN ? AND ?
    ''', (month_start_str, month_end_str))
    created_count = cursor.fetchone()['count']
    
    # プロジェクト別完了タスク数
    cursor.execute('''
        SELECT p.id, p.name, p.color, COUNT(t.id) as completed_count
        FROM projects p
        LEFT JOIN tasks t ON p.id = t.project_id 
            AND date(t.completed_at) BETWEEN ? AND ?
        GROUP BY p.id
        ORDER BY completed_count DESC
    ''', (month_start_str, month_end_str))
    project_stats = [dict_from_row(row) for row in cursor.fetchall()]
    
    # タグ別完了タスク数
    cursor.execute('''
        SELECT tg.id, tg.name, tg.color, COUNT(DISTINCT t.id) as completed_count
        FROM tags tg
        LEFT JOIN task_tags tt ON tg.id = tt.tag_id
        LEFT JOIN tasks t ON tt.task_id = t.id 
            AND date(t.completed_at) BETWEEN ? AND ?
        GROUP BY tg.id
        ORDER BY completed_count DESC
    ''', (month_start_str, month_end_str))
    tag_stats = [dict_from_row(row) for row in cursor.fetchall()]
    
    # 週別完了タスク数
    cursor.execute('''
        SELECT strftime('%W', completed_at) as week, COUNT(*) as count
        FROM tasks
        WHERE date(completed_at) BETWEEN ? AND ?
        GROUP BY week
        ORDER BY week
    ''', (month_start_str, month_end_str))
    weekly_data = [dict_from_row(row) for row in cursor.fetchall()]
    
    # 色別完了タスク数
    cursor.execute('''
        SELECT color, COUNT(*) as count
        FROM tasks
        WHERE date(completed_at) BETWEEN ? AND ?
        GROUP BY color
        ORDER BY count DESC
    ''', (month_start_str, month_end_str))
    color_stats = [dict_from_row(row) for row in cursor.fetchall()]
    
    conn.close()
    
    return jsonify({
        'period': {
            'year': year,
            'month': month,
            'start': month_start_str,
            'end': month_end_str
        },
        'completed_count': completed_count,
        'created_count': created_count,
        'project_stats': project_stats,
        'tag_stats': tag_stats,
        'weekly_data': weekly_data,
        'color_stats': color_stats
    })

@reports_bp.route('/reports/summary', methods=['GET'])
def get_summary():
    """全体サマリーを取得"""
    conn = get_db()
    cursor = conn.cursor()
    
    # 総タスク数
    cursor.execute('SELECT COUNT(*) as count FROM tasks')
    total_tasks = cursor.fetchone()['count']
    
    # ステータス別
    cursor.execute('''
        SELECT status, COUNT(*) as count FROM tasks GROUP BY status
    ''')
    status_counts = {row['status']: row['count'] for row in cursor.fetchall()}
    
    # プロジェクト数
    cursor.execute('SELECT COUNT(*) as count FROM projects')
    total_projects = cursor.fetchone()['count']
    
    # タグ数
    cursor.execute('SELECT COUNT(*) as count FROM tags')
    total_tags = cursor.fetchone()['count']
    
    # アイデア数
    cursor.execute('SELECT COUNT(*) as count FROM ideas')
    total_ideas = cursor.fetchone()['count']
    
    # 完了率
    completed = status_counts.get('done', 0)
    completion_rate = (completed / total_tasks * 100) if total_tasks > 0 else 0
    
    conn.close()
    
    return jsonify({
        'total_tasks': total_tasks,
        'status_counts': status_counts,
        'total_projects': total_projects,
        'total_tags': total_tags,
        'total_ideas': total_ideas,
        'completion_rate': round(completion_rate, 1)
    })
