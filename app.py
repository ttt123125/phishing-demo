import os
import sys
import traceback
from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    try:
        # 显示环境信息
        return f"""
        <h1>✅ Flask 运行正常</h1>
        <p>Python 版本: {sys.version}</p>
        <p>当前目录: {os.getcwd()}</p>
        <p>文件列表: {os.listdir('.')}</p>
        """
    except Exception as e:
        return f"<h1>❌ 错误</h1><pre>{traceback.format_exc()}</pre>"