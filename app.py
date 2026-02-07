from flask import Flask, render_template, jsonify
import pandas as pd
import requests
from io import StringIO
import time

app = Flask(__name__)

# ================= CACHE =================
CACHE_DATA = None
CACHE_TIME = 0
CACHE_TTL = 300  # 5 นาที

# ================= GOOGLE SHEET CSV =================
GSHEET_URL = "https://docs.google.com/spreadsheets/d/XXXX/export?format=csv"

# ================= LOAD DATA =================
def load_data():
    global CACHE_DATA, CACHE_TIME

    if CACHE_DATA and time.time() - CACHE_TIME < CACHE_TTL:
        return CACHE_DATA

    try:
        r = requests.get(GSHEET_URL, timeout=10)
        df = pd.read_csv(StringIO(r.text))

        # 🛡 FIX: ขนาดเป็น string ไม่แปลง float
        df["ขนาด"] = df["ขนาด"].astype(str)

        # แปลงราคาที่ต้อง numeric
        price_cols = ["กุ้งขาวสด", "กุ้งขาวมีชีวิต", "กุ้งดำสด", "กุ้งดำมีชีวิต"]
        for c in price_cols:
            df[c] = pd.to_numeric(df[c], errors="coerce")

        CACHE_DATA = df.to_dict(orient="records")
        CACHE_TIME = time.time()
        return CACHE_DATA

    except Exception as e:
        print("GSHEET ERROR:", e)
        return []

# ================= API =================
@app.route("/api/data")
def api_data():
    return jsonify(load_data())

# ================= DASHBOARD =================
@app.route("/")
def dashboard():
    return render_template("dashboard.html")

# ================= RUN =================
if __name__ == "__main__":
    app.run(debug=True)
