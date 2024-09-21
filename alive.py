import os
from flask import Flask
from threading import Thread

app = Flask(__name__)

@app.route('/')
def home():
    return "TEST"

def run():
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8000)))

def alive():
    t = Thread(target=run)
    t.start()