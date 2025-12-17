import os
from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return "✅ Thai Shrimp Industry 2026 is running"

@app.route("/healthz")
def healthz():
    return {"status": "ok"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
