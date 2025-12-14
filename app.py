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
    import socket
    
    # ローカルIPアドレスを取得
    def get_local_ip():
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception:
            return "localhost"
    
    local_ip = get_local_ip()
    print("Todo App Server starting...")
    print(f"Local:   http://localhost:5000")
    print(f"Network: http://{local_ip}:5000")
    print("Smartphone: Connect to the same Wi-Fi and open the Network URL")
    app.run(debug=True, host='0.0.0.0', port=5000)
