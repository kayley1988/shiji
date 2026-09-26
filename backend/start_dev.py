"""
诗语雅集 - 开发环境启动脚本
"""
import sys
sys.path.insert(0, '.')

from app import app, socketio, init_data

if __name__ == '__main__':
    init_data()
    print("=" * 50)
    print("诗语雅集服务启动中...")
    print("API: http://localhost:5000/")
    print("=" * 50)
    socketio.run(app, host='0.0.0.0', port=5000, debug=False, use_reloader=False)
