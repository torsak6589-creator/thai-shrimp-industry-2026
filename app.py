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
from flask import render_template

@app.route("/dashboard")
def dashboard():
    mock_data = {
        "year": 2026,
        "export_volume_tons": 580000,
        "export_value_usd": 4200000000,
        "top_markets": ["USA", "Japan", "China", "UAE", "EU"]
    }
    return render_template("dashboard.html", data=mock_data)
