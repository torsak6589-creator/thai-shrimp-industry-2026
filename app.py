from flask import Flask, render_template, jsonify
import requests, json, os
from time import time

app = Flask(__name__)

# =========================
# Cache Config
# =========================
CACHE_TTL = 300  # 5 นาที
CACHE = {
    "data": None,
    "timestamp": 0
}

# =========================
# Google Sheet Config
# =========================
GSHEET_ID = "1z8sWAjtDtdMNxqS41QejImOXBmPQtEszRP249ewf5es"
GSHEET_GID = "0"
GSHEET_URL = (
    f"https://docs.google.com/spreadsheets/d/{GSHEET_ID}/gviz/tq"
    f"?tqx=out:json&gid={GSHEET_GID}"
)

# =========================
# Utility
# =========================
def format_gsheet_date(v):
    if isinstance(v, str) and v.startswith("Date"):
        y, m, d = v.replace("Date(", "").replace(")", "").split(",")
        return f"{int(d):02d}-{int(m)+1:02d}-{y}"
    return v or "-"

# =========================
# Data Layer (with cache)
# =========================
def get_prices():
    now = time()

    if CACHE["data"] and now - CACHE["timestamp"] < CACHE_TTL:
        return CACHE["data"]

    try:
        r = requests.get(GSHEET_URL, timeout=10)
        text = r.text
        json_str = text[text.find("{"):text.rfind("}")+1]
        data = json.loads(json_str)

        prices = []

        for row in data["table"]["rows"]:
            c = row["c"]
            if not c or len(c) < 8:
                continue

            prices.append({
                "month": c[0]["v"] if c[0] else "-",
                "week": c[1]["v"] if c[1] else "-",
                "period": c[2]["v"] if c[2] else "-",
                "size": c[3]["v"] if c[3] else "-",
                "white_fresh": c[4]["v"] if c[4] else "-",
                "white_live": c[5]["v"] if c[5] else "-",
                "black_fresh": c[6]["v"] if c[6] else "-",
                "black_live": c[7]["v"] if c[7] else "-",
            })

        CACHE["data"] = prices
        CACHE["timestamp"] = now
        return prices

    except Exception as e:
        print("GSHEET ERROR:", e)
        return CACHE["data"] or []

# =========================
# Business Logic
# =========================
def market_overview(prices):
    if not prices:
        return {}

    avg_price = round(sum(p["price"] for p in prices) / len(prices), 2)
    latest = prices[-1]

    trend = "→"
    if len(prices) >= 2:
        if prices[-1]["price"] > prices[-2]["price"]:
            trend = "↑"
        elif prices[-1]["price"] < prices[-2]["price"]:
            trend = "↓"

    return {
        "date": latest["date"],
        "market": latest["market"],
        "size": latest["size"],
        "avg_price": avg_price,
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

    trend = "↑" if diff > 0 else "↓" if diff < 0 else "→"

    return {
        "avg_last_7": round(avg_last, 2),
        "avg_prev_7": round(avg_prev, 2),
        "diff": diff,
        "pct": pct,
        "trend": trend
    }

def executive_summary(overview):
    if not overview:
        return ""

    if overview["trend"] == "↑":
        level = "ตลาดร้อนแรง"
        decision = "ชะลอการซื้อ"
        note = "ราคาเร่งตัว"
    elif overview["trend"] == "↓":
        level = "ตลาดผ่อนคลาย"
        decision = "ทยอยเข้าซื้อ"
        note = "ราคาอ่อนตัว"
    else:
        level = "ตลาดทรงตัว"
        decision = "ซื้ออย่างระมัดระวัง"
        note = "ราคาแกว่งในกรอบแคบ"

    return f"""
    <strong>{level}</strong><br>
    ราคาเฉลี่ย {overview["avg_price"]} บาท/กก.<br>
    แนวโน้ม: {note}<br>
    🚦 คำแนะนำ: <strong>{decision}</strong>
    """

# =========================
# Routes
# =========================
@app.route("/")
def dashboard():
    prices = get_prices()
    overview = market_overview(prices)
    compare_7d = compare_last_14_days(prices)
    summary = executive_summary(overview)

    return render_template(
        "dashboard.html",
        prices=prices,
        overview=overview,
        compare_7d=compare_7d,
        summary=summary
    )

@app.route("/api/prices")
def api_prices():
    return jsonify(get_prices())

# =========================
# Run
# =========================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=True)


