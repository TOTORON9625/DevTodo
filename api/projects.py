from flask import Blueprint, request, jsonify
from database import get_db, dict_from_row

projects_bp = Blueprint('projects', __name__)

@projects_bp.route('/projects', methods=['GET'])
def get_projects():
    """全プロジェクトを取得"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT p.*, COUNT(t.id) as task_count,
               SUM(CASE WHEN t.status = 'done' THEN 1 ELSE 0 END) as completed_count
        FROM projects p
        LEFT JOIN tasks t ON p.id = t.project_id
        GROUP BY p.id
        ORDER BY p.created_at DESC
    ''')
    
    projects = [dict_from_row(row) for row in cursor.fetchall()]
    conn.close()
    
    return jsonify(projects)

@projects_bp.route('/projects', methods=['POST'])
def create_project():
    """新規プロジェクトを作成"""
    data = request.json
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO projects (name, description, color)
        VALUES (?, ?, ?)
    ''', (
        data.get('name'),
        data.get('description', ''),
        data.get('color', '#6750A4')
    ))
    
    project_id = cursor.lastrowid
    conn.commit()
    
    cursor.execute('SELECT * FROM projects WHERE id = ?', (project_id,))
    project = dict_from_row(cursor.fetchone())
    
    conn.close()
    return jsonify(project), 201

@projects_bp.route('/projects/<int:project_id>', methods=['GET'])
def get_project(project_id):
    """プロジェクトを取得"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT p.*, COUNT(t.id) as task_count,
               SUM(CASE WHEN t.status = 'done' THEN 1 ELSE 0 END) as completed_count
        FROM projects p
        LEFT JOIN tasks t ON p.id = t.project_id
        WHERE p.id = ?
        GROUP BY p.id
    ''', (project_id,))
    
    project = dict_from_row(cursor.fetchone())
    
    if not project:
        conn.close()
        return jsonify({'error': 'Project not found'}), 404
    
    conn.close()
    return jsonify(project)

@projects_bp.route('/projects/<int:project_id>', methods=['PUT'])
def update_project(project_id):
    """プロジェクトを更新"""
    data = request.json
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM projects WHERE id = ?', (project_id,))
    if not cursor.fetchone():
        conn.close()
        return jsonify({'error': 'Project not found'}), 404
    
    cursor.execute('''
        UPDATE projects SET
            name = COALESCE(?, name),
            description = COALESCE(?, description),
            color = COALESCE(?, color),
            updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
    ''', (
        data.get('name'),
        data.get('description'),
        data.get('color'),
        project_id
    ))
    
    conn.commit()
    
    cursor.execute('SELECT * FROM projects WHERE id = ?', (project_id,))
    project = dict_from_row(cursor.fetchone())
    
    conn.close()
    return jsonify(project)

@projects_bp.route('/projects/<int:project_id>', methods=['DELETE'])
def delete_project(project_id):
    """プロジェクトを削除"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM projects WHERE id = ?', (project_id,))
    if not cursor.fetchone():
        conn.close()
        return jsonify({'error': 'Project not found'}), 404
    
    cursor.execute('DELETE FROM projects WHERE id = ?', (project_id,))
    conn.commit()
    conn.close()
    
    return jsonify({'message': 'Project deleted successfully'})
