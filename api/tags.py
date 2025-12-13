from flask import Blueprint, request, jsonify
from database import get_db, dict_from_row

tags_bp = Blueprint('tags', __name__)

@tags_bp.route('/tags', methods=['GET'])
def get_tags():
    """全タグを取得"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT t.*, COUNT(tt.task_id) as usage_count
        FROM tags t
        LEFT JOIN task_tags tt ON t.id = tt.tag_id
        GROUP BY t.id
        ORDER BY usage_count DESC, t.name ASC
    ''')
    
    tags = [dict_from_row(row) for row in cursor.fetchall()]
    conn.close()
    
    return jsonify(tags)

@tags_bp.route('/tags', methods=['POST'])
def create_tag():
    """新規タグを作成"""
    data = request.json
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            INSERT INTO tags (name, color)
            VALUES (?, ?)
        ''', (
            data.get('name'),
            data.get('color', '#6750A4')
        ))
        
        tag_id = cursor.lastrowid
        conn.commit()
        
        cursor.execute('SELECT * FROM tags WHERE id = ?', (tag_id,))
        tag = dict_from_row(cursor.fetchone())
        
        conn.close()
        return jsonify(tag), 201
    except Exception as e:
        conn.close()
        return jsonify({'error': 'Tag already exists'}), 400

@tags_bp.route('/tags/<int:tag_id>', methods=['PUT'])
def update_tag(tag_id):
    """タグを更新"""
    data = request.json
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM tags WHERE id = ?', (tag_id,))
    if not cursor.fetchone():
        conn.close()
        return jsonify({'error': 'Tag not found'}), 404
    
    cursor.execute('''
        UPDATE tags SET
            name = COALESCE(?, name),
            color = COALESCE(?, color)
        WHERE id = ?
    ''', (
        data.get('name'),
        data.get('color'),
        tag_id
    ))
    
    conn.commit()
    
    cursor.execute('SELECT * FROM tags WHERE id = ?', (tag_id,))
    tag = dict_from_row(cursor.fetchone())
    
    conn.close()
    return jsonify(tag)

@tags_bp.route('/tags/<int:tag_id>', methods=['DELETE'])
def delete_tag(tag_id):
    """タグを削除"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM tags WHERE id = ?', (tag_id,))
    if not cursor.fetchone():
        conn.close()
        return jsonify({'error': 'Tag not found'}), 404
    
    cursor.execute('DELETE FROM tags WHERE id = ?', (tag_id,))
    conn.commit()
    conn.close()
    
    return jsonify({'message': 'Tag deleted successfully'})
