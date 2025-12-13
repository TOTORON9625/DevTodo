from flask import Blueprint, request, jsonify
from datetime import datetime
from database import get_db, dict_from_row

tasks_bp = Blueprint('tasks', __name__)

@tasks_bp.route('/tasks', methods=['GET'])
def get_tasks():
    """全タスクを取得"""
    conn = get_db()
    cursor = conn.cursor()
    
    # フィルタリングパラメータ
    status = request.args.get('status')
    project_id = request.args.get('project_id')
    tag_id = request.args.get('tag_id')
    
    query = '''
        SELECT t.*, p.name as project_name,
               GROUP_CONCAT(tg.id || ':' || tg.name || ':' || tg.color) as tags
        FROM tasks t
        LEFT JOIN projects p ON t.project_id = p.id
        LEFT JOIN task_tags tt ON t.id = tt.task_id
        LEFT JOIN tags tg ON tt.tag_id = tg.id
    '''
    
    conditions = []
    params = []
    
    if status:
        conditions.append('t.status = ?')
        params.append(status)
    
    if project_id:
        conditions.append('t.project_id = ?')
        params.append(project_id)
    
    if tag_id:
        conditions.append('t.id IN (SELECT task_id FROM task_tags WHERE tag_id = ?)')
        params.append(tag_id)
    
    if conditions:
        query += ' WHERE ' + ' AND '.join(conditions)
    
    query += ' GROUP BY t.id ORDER BY t.priority DESC, t.created_at DESC'
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    
    tasks = []
    for row in rows:
        task = dict_from_row(row)
        # タグをパース
        if task['tags']:
            tag_list = []
            for tag_str in task['tags'].split(','):
                parts = tag_str.split(':')
                if len(parts) >= 3:
                    tag_list.append({
                        'id': int(parts[0]),
                        'name': parts[1],
                        'color': parts[2]
                    })
            task['tags'] = tag_list
        else:
            task['tags'] = []
        tasks.append(task)
    
    conn.close()
    return jsonify(tasks)

@tasks_bp.route('/tasks', methods=['POST'])
def create_task():
    """新規タスクを作成"""
    data = request.json
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO tasks (title, description, color, status, priority, project_id, due_date)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (
        data.get('title'),
        data.get('description', ''),
        data.get('color', '#6750A4'),
        data.get('status', 'todo'),
        data.get('priority', 0),
        data.get('project_id'),
        data.get('due_date')
    ))
    
    task_id = cursor.lastrowid
    
    # タグを紐付け
    if 'tag_ids' in data and data['tag_ids']:
        for tag_id in data['tag_ids']:
            cursor.execute(
                'INSERT OR IGNORE INTO task_tags (task_id, tag_id) VALUES (?, ?)',
                (task_id, tag_id)
            )
    
    conn.commit()
    
    # 作成したタスクを取得
    cursor.execute('SELECT * FROM tasks WHERE id = ?', (task_id,))
    task = dict_from_row(cursor.fetchone())
    
    conn.close()
    return jsonify(task), 201

@tasks_bp.route('/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
    """タスクを取得"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT t.*, p.name as project_name
        FROM tasks t
        LEFT JOIN projects p ON t.project_id = p.id
        WHERE t.id = ?
    ''', (task_id,))
    
    task = dict_from_row(cursor.fetchone())
    
    if not task:
        conn.close()
        return jsonify({'error': 'Task not found'}), 404
    
    # タグを取得
    cursor.execute('''
        SELECT tg.* FROM tags tg
        JOIN task_tags tt ON tg.id = tt.tag_id
        WHERE tt.task_id = ?
    ''', (task_id,))
    
    task['tags'] = [dict_from_row(row) for row in cursor.fetchall()]
    
    conn.close()
    return jsonify(task)

@tasks_bp.route('/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    """タスクを更新"""
    data = request.json
    conn = get_db()
    cursor = conn.cursor()
    
    # 現在のタスクを取得
    cursor.execute('SELECT * FROM tasks WHERE id = ?', (task_id,))
    task = cursor.fetchone()
    
    if not task:
        conn.close()
        return jsonify({'error': 'Task not found'}), 404
    
    # ステータスがdoneに変わった場合、completed_atを設定
    completed_at = None
    if data.get('status') == 'done' and task['status'] != 'done':
        completed_at = datetime.now().isoformat()
    
    cursor.execute('''
        UPDATE tasks SET
            title = COALESCE(?, title),
            description = COALESCE(?, description),
            color = COALESCE(?, color),
            status = COALESCE(?, status),
            priority = COALESCE(?, priority),
            project_id = ?,
            due_date = ?,
            updated_at = CURRENT_TIMESTAMP,
            completed_at = COALESCE(?, completed_at)
        WHERE id = ?
    ''', (
        data.get('title'),
        data.get('description'),
        data.get('color'),
        data.get('status'),
        data.get('priority'),
        data.get('project_id', task['project_id']),
        data.get('due_date', task['due_date']),
        completed_at,
        task_id
    ))
    
    # タグを更新
    if 'tag_ids' in data:
        cursor.execute('DELETE FROM task_tags WHERE task_id = ?', (task_id,))
        for tag_id in data['tag_ids']:
            cursor.execute(
                'INSERT OR IGNORE INTO task_tags (task_id, tag_id) VALUES (?, ?)',
                (task_id, tag_id)
            )
    
    conn.commit()
    
    # 更新したタスクを取得
    cursor.execute('SELECT * FROM tasks WHERE id = ?', (task_id,))
    updated_task = dict_from_row(cursor.fetchone())
    
    conn.close()
    return jsonify(updated_task)

@tasks_bp.route('/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    """タスクを削除"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM tasks WHERE id = ?', (task_id,))
    task = cursor.fetchone()
    
    if not task:
        conn.close()
        return jsonify({'error': 'Task not found'}), 404
    
    cursor.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
    conn.commit()
    conn.close()
    
    return jsonify({'message': 'Task deleted successfully'})
