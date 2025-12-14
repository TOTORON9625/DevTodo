"""
DevTodo - Flask Application
グローバル環境対応版
"""

import os
import socket
from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS

# 環境変数から設定を読み込み
DEBUG = os.environ.get('DEBUG', 'True').lower() == 'true'
PORT = int(os.environ.get('PORT', 5000))
HOST = os.environ.get('HOST', '0.0.0.0')

# Supabase設定（環境変数から読み込み、デフォルト値あり）
SUPABASE_URL = os.environ.get('SUPABASE_URL', 'https://wssphvcahiujcvdobxgy.supabase.co')
SUPABASE_KEY = os.environ.get('SUPABASE_KEY', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Indzc3BodmNhaGl1amN2ZG9ieGd5Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjU3MTQ1NTAsImV4cCI6MjA4MTI5MDU1MH0.G8QeL5BPm49fwwlsNgNVdttBOGYvYvEVJpxcTATHqwE')

app = Flask(__name__, static_folder='static')

# CORS設定（環境変数で許可オリジンを指定可能）
CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '*')
CORS(app, resources={r"/api/*": {"origins": CORS_ORIGINS}})

# 設定をアプリケーションコンテキストに保存
app.config['SUPABASE_URL'] = SUPABASE_URL
app.config['SUPABASE_KEY'] = SUPABASE_KEY

# ===================================
# ヘルスチェックエンドポイント
# ===================================
@app.route('/health')
def health_check():
    """ヘルスチェック用エンドポイント（デプロイ監視用）"""
    return jsonify({
        'status': 'healthy',
        'service': 'DevTodo',
        'version': '1.0.0'
    })

@app.route('/api/config')
def get_config():
    """フロントエンド用の設定を返す"""
    return jsonify({
        'supabase_url': SUPABASE_URL,
        'supabase_key': SUPABASE_KEY
    })

# ===================================
# 静的ファイル配信
# ===================================
@app.route('/')
def index():
    """メインページを返す"""
    return send_from_directory('static', 'index.html')

@app.route('/manifest.json')
def manifest():
    """PWAマニフェスト"""
    return send_from_directory('static', 'manifest.json')

@app.route('/sw.js')
def service_worker():
    """Service Worker"""
    return send_from_directory('static', 'sw.js')

@app.route('/<path:path>')
def serve_static(path):
    """静的ファイルを配信"""
    return send_from_directory('static', path)

# ===================================
# ユーティリティ関数
# ===================================
def get_local_ip():
    """ローカルIPアドレスを取得"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "localhost"

# ===================================
# メインエントリーポイント
# ===================================
if __name__ == '__main__':
    local_ip = get_local_ip()
    
    print("=" * 50)
    print("  DevTodo Server")
    print("=" * 50)
    print(f"  Mode:    {'Development' if DEBUG else 'Production'}")
    print(f"  Local:   http://localhost:{PORT}")
    print(f"  Network: http://{local_ip}:{PORT}")
    print("=" * 50)
    print("  Environment Variables:")
    print(f"    PORT={PORT}")
    print(f"    HOST={HOST}")
    print(f"    DEBUG={DEBUG}")
    print(f"    SUPABASE_URL={SUPABASE_URL[:50]}...")
    print("=" * 50)
    
    if DEBUG:
        # 開発モード
        app.run(debug=True, host=HOST, port=PORT)
    else:
        # 本番モード（gunicornなどのWSGIサーバーで実行推奨）
        app.run(debug=False, host=HOST, port=PORT, threaded=True)
