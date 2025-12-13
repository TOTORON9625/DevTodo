from flask import Flask, send_from_directory
from flask_cors import CORS
from database import init_db

# Blueprintsをインポート
from api.tasks import tasks_bp
from api.projects import projects_bp
from api.tags import tags_bp
from api.ideas import ideas_bp
from api.reports import reports_bp

app = Flask(__name__, static_folder='static')
CORS(app)

# データベース初期化
init_db()

# APIエンドポイントを登録
app.register_blueprint(tasks_bp, url_prefix='/api')
app.register_blueprint(projects_bp, url_prefix='/api')
app.register_blueprint(tags_bp, url_prefix='/api')
app.register_blueprint(ideas_bp, url_prefix='/api')
app.register_blueprint(reports_bp, url_prefix='/api')

@app.route('/')
def index():
    """メインページを返す"""
    return send_from_directory('static', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    """静的ファイルを配信"""
    return send_from_directory('static', path)

if __name__ == '__main__':
    print("Todo App Server starting...")
    print("Open http://localhost:5000 in your browser")
    app.run(debug=True, port=5000)
