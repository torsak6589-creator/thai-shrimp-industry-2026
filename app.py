from flask import Flask, render_template, jsonify
import requests, json, os

app = Flask(__name__)

GSHEET_ID = "1z8sWAjtDtdMNxqS41QejImOXBmPQtEszRP249ewf5es"
GSHEET_GID = "0"
GSHEET_URL = f"https://docs.google.com/spreadsheets/d/{GSHEET_ID}/gviz/tq?tqx=out:json&gid={GSHEET_GID}"
import datetime

from datetime import datetime

def format_gsheet_date(v):
    """
    แปลง Date(2026,0,2) → 02-01-2026
    """
    if isinstance(v, str) and v.startswith("Date"):
        parts = v.replace("Date(", "").replace(")", "").split(",")
        year = int(parts[0])
        month = int(parts[1]) + 1   # Google Sheet เดือนเริ่มที่ 0
        day = int(parts[2])
        return f"{day:02d}-{month:02d}-{year}"
    return v


def get_price_from_gsheet():
    r = requests.get(GSHEET_URL, timeout=15)
    text = r.text
    json_str = text[text.find("{"):text.rfind("}")+1]
    data = json.loads(json_str)

    prices = []

    for row in data["table"]["rows"]:
        c = row["c"]
        if not c or len(c) < 4:
            continue

        date_raw = c[0]["v"] if c[0] else None
        price = c[3]["v"] if c[3] else None

        if date_raw is None or price is None:
            continue

        prices.append({
            "date": format_gsheet_date(date_raw),   # ✅ แปลงตรงนี้
            "market": c[1]["v"] if c[1] else "-",
            "size": int(c[2]["v"]) if c[2] else "-",  # ไม่มีทศนิยม
            "price": price
        })

    return prices
def market_overview(prices):
    if not prices:
        return {}

    latest = prices[-1]
    avg_price = sum(p["price"] for p in prices) / len(prices)

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
        "avg_price": round(avg_price, 2),
        "trend": trend
    }

        
@app.route("/")
def dashboard():
    return render_template("dashboard.html", prices=get_price_from_gsheet())
@app.route("/")
def dashboard():
    prices = get_price_from_gsheet()
    overview = market_overview(prices)

    return render_template(
        "dashboard.html",
        prices=prices,
        overview=overview
    )

@app.route("/api/prices")
def api_prices():
    return jsonify(get_price_from_gsheet())

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

