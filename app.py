from flask import Flask, render_template, jsonify
import requests, json, os
from datetime import datetime
from time import time

app = Flask(__name__)
import time

CACHE = {
    "data": None,
    "timestamp": 0
}
CACHE_TTL = 300  # 5 นาที

# =========================
# Google Sheet Config
# =========================
GSHEET_ID = "1z8sWAjtDtdMNxqS41QejImOXBmPQtEszRP249ewf5es"
GSHEET_GID = "0"
GSHEET_URL = f"https://docs.google.com/spreadsheets/d/{GSHEET_ID}/gviz/tq?tqx=out:json&gid={GSHEET_GID}"

# =========================
# Cache Config  ✅ (NEW)
# =========================
CACHE_TTL = 300  # วินาที (5 นาที)

CACHE = {
    "prices": None,
    "timestamp": 0
}

# =========================
# Utility
# =========================
def format_gsheet_date(v):
    """Date(2026,0,2) → 02-01-2026"""
    if isinstance(v, str) and v.startswith("Date"):
        y, m, d = v.replace("Date(", "").replace(")", "").split(",")
        return f"{int(d):02d}-{int(m)+1:02d}-{y}"
    return v

# =========================
# Data Layer (Google Sheet)
# =========================
def get_price_from_gsheet():
    now = time.time()

    if CACHE["data"] and now - CACHE["timestamp"] < CACHE_TTL:
        return CACHE["data"]

    r = requests.get(GSHEET_URL, timeout=15)
    text = r.text
    json_str = text[text.find("{"):text.rfind("}")+1]
    data = json.loads(json_str)

    prices = []
    for row in data["table"]["rows"]:
        c = row["c"]
        if not c or len(c) < 4 or not c[0] or not c[3]:
            continue

        prices.append({
            "date": format_gsheet_date(c[0]["v"]),
            "market": c[1]["v"] if c[1] else "-",
            "size": int(c[2]["v"]) if c[2] else "-",
            "price": c[3]["v"]
        })

    CACHE["data"] = prices
    CACHE["timestamp"] = now
    return prices


# =========================
# Cache Wrapper  ✅ (NEW)
# =========================
def get_cached_prices():
    now = time()

    # ใช้ cache ถ้ายังไม่หมดอายุ
    if CACHE["prices"] and (now - CACHE["timestamp"] < CACHE_TTL):
        return CACHE["prices"]

    # ดึงใหม่
    prices = get_price_from_gsheet()
    CACHE["prices"] = prices
    CACHE["timestamp"] = now
    return prices

# =========================
# Business Logic
# =========================
def market_overview(prices):
    if not prices:
        return {}

    avg_price = sum(p["price"] for p in prices) / len(prices)

    trend = "→"
    if len(prices) >= 2:
        if prices[-1]["price"] > prices[-2]["price"]:
            trend = "↑"
        elif prices[-1]["price"] < prices[-2]["price"]:
            trend = "↓"

    latest = prices[-1]

    return {
        "date": latest["date"],
        "market": latest["market"],
        "size": latest["size"],
        "avg_price": round(avg_price, 2),
        "trend": trend
    }

def compare_last_14_days(prices):
    if len(prices) < 14:
        return None

    last_7 = prices[-7:]
    prev_7 = prices[-14:-7]

    avg_last = sum(p["price"] for p in last_7) / 7
    avg_prev = sum(p["price"] for p in prev_7) / 7

    diff = round(avg_last - avg_prev, 2)
    pct = round((diff / avg_prev) * 100, 2) if avg_prev else 0

    trend = "→"
    if diff > 0:
        trend = "↑"
    elif diff < 0:
        trend = "↓"

    return {
        "avg_last_7": round(avg_last, 2),
        "avg_prev_7": round(avg_prev, 2),
        "diff": diff,
        "pct": pct,
        "trend": trend
    }
def executive_summary(prices, overview):
    if not prices or not overview:
        return ""

    trend = overview["trend"]
    avg_price = overview["avg_price"]

    if trend == "↑":
        level = "ตลาดร้อนแรง"
        decision = "ชะลอการซื้อ และควบคุมต้นทุน"
        note = "ราคาเร่งตัวต่อเนื่อง"
    elif trend == "↓":
        level = "ตลาดผ่อนคลาย"
        decision = "สามารถทยอยเข้าซื้อ"
        note = "ราคาอ่อนตัวลง"
    else:
        level = "ตลาดทรงตัว"
        decision = "ซื้อแบบระมัดระวัง"
        note = "ราคาแกว่งตัวในกรอบแคบ"

    return f"""
ตลาดกุ้งล่าสุดอยู่ในภาวะ <strong>{level}</strong> 
ราคาเฉลี่ยประมาณ <strong>{avg_price} บาท/กก.</strong> 
แนวโน้ม {note} แนะนำให้ <strong>{decision}</strong>
เพื่อบริหารความเสี่ยงด้านต้นทุนในระยะสั้น
"""

# =========================
# Routes
# =========================
@app.route("/")
def dashboard():
    prices = get_cached_prices()   # ✅ เปลี่ยนจุดนี้
    overview = market_overview(prices)
    compare_7d = compare_last_14_days(prices)

    return render_template(
        "dashboard.html",
        prices=prices,
        overview=overview,
        compare_7d=compare_7d
    )

@app.route("/api/prices")
def api_prices():
    return jsonify(get_cached_prices())  # ✅ ใช้ cache เช่นกัน

# =========================
# Run
# =========================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

