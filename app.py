from flask import Flask
app = Flask(__name__)

@app.route('/')
def home():
    return "<h1>✅ Vercel 部署成功！</h1><p>Flask 后端运行正常。</p>"