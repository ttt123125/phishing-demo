from flask import Flask
app = Flask(__name__)

@app.route('/')
def home():
    return "Hello from Vercel! Flask is working."

# Vercel 需要这个 'app' 实例