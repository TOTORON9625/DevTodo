from flask import Blueprint, request, jsonify
from database import get_db, dict_from_row

ideas_bp = Blueprint('ideas', __name__)

@ideas_bp.route('/ideas', methods=['GET'])
def get_ideas():
    """全アイデアを取得"""
    conn = get_db()
    cursor = conn.cursor()
    
    search = request.args.get('search', '')
    
    if search:
        cursor.execute('''
            SELECT * FROM ideas
            WHERE title LIKE ? OR content LIKE ?
            ORDER BY is_pinned DESC, updated_at DESC
        ''', (f'%{search}%', f'%{search}%'))
    else:
        cursor.execute('''
            SELECT * FROM ideas
            ORDER BY is_pinned DESC, updated_at DESC
        ''')
    
    ideas = [dict_from_row(row) for row in cursor.fetchall()]
    conn.close()
    
    return jsonify(ideas)

@ideas_bp.route('/ideas', methods=['POST'])
def create_idea():
    """新規アイデアを作成"""
    data = request.json
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO ideas (title, content, color, is_pinned)
        VALUES (?, ?, ?, ?)
    ''', (
        data.get('title'),
        data.get('content', ''),
        data.get('color', '#6750A4'),
        data.get('is_pinned', 0)
    ))
    
    idea_id = cursor.lastrowid
    conn.commit()
    
    cursor.execute('SELECT * FROM ideas WHERE id = ?', (idea_id,))
    idea = dict_from_row(cursor.fetchone())
    
    conn.close()
    return jsonify(idea), 201

@ideas_bp.route('/ideas/<int:idea_id>', methods=['GET'])
def get_idea(idea_id):
    """アイデアを取得"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM ideas WHERE id = ?', (idea_id,))
    idea = dict_from_row(cursor.fetchone())
    
    if not idea:
        conn.close()
        return jsonify({'error': 'Idea not found'}), 404
    
    conn.close()
    return jsonify(idea)

@ideas_bp.route('/ideas/<int:idea_id>', methods=['PUT'])
def update_idea(idea_id):
    """アイデアを更新"""
    data = request.json
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM ideas WHERE id = ?', (idea_id,))
    if not cursor.fetchone():
        conn.close()
        return jsonify({'error': 'Idea not found'}), 404
    
    cursor.execute('''
        UPDATE ideas SET
            title = COALESCE(?, title),
            content = COALESCE(?, content),
            color = COALESCE(?, color),
            is_pinned = COALESCE(?, is_pinned),
            updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
    ''', (
        data.get('title'),
        data.get('content'),
        data.get('color'),
        data.get('is_pinned'),
        idea_id
    ))
    
    conn.commit()
    
    cursor.execute('SELECT * FROM ideas WHERE id = ?', (idea_id,))
    idea = dict_from_row(cursor.fetchone())
    
    conn.close()
    return jsonify(idea)

@ideas_bp.route('/ideas/<int:idea_id>', methods=['DELETE'])
def delete_idea(idea_id):
    """アイデアを削除"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM ideas WHERE id = ?', (idea_id,))
    if not cursor.fetchone():
        conn.close()
        return jsonify({'error': 'Idea not found'}), 404
    
    cursor.execute('DELETE FROM ideas WHERE id = ?', (idea_id,))
    conn.commit()
    conn.close()
    
    return jsonify({'message': 'Idea deleted successfully'})

@ideas_bp.route('/ideas/<int:idea_id>/convert', methods=['POST'])
def convert_to_task(idea_id):
    """アイデアをタスクに変換"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM ideas WHERE id = ?', (idea_id,))
    idea = dict_from_row(cursor.fetchone())
    
    if not idea:
        conn.close()
        return jsonify({'error': 'Idea not found'}), 404
    
    # タスクを作成
    cursor.execute('''
        INSERT INTO tasks (title, description, color, status)
        VALUES (?, ?, ?, 'todo')
    ''', (
        idea['title'],
        idea['content'],
        idea['color']
    ))
    
    task_id = cursor.lastrowid
    
    # アイデアを削除
    cursor.execute('DELETE FROM ideas WHERE id = ?', (idea_id,))
    
    conn.commit()
    
    cursor.execute('SELECT * FROM tasks WHERE id = ?', (task_id,))
    task = dict_from_row(cursor.fetchone())
    
    conn.close()
    return jsonify(task), 201
