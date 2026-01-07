from flask import Flask, render_template, jsonify
import requests, json, os
from datetime import datetime

app = Flask(__name__)

GSHEET_ID = "1z8sWAjtDtdMNxqS41QejImOXBmPQtEszRP249ewf5es"
GSHEET_GID = "0"
GSHEET_URL = f"https://docs.google.com/spreadsheets/d/{GSHEET_ID}/gviz/tq?tqx=out:json&gid={GSHEET_GID}"

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
# Data Layer
# =========================
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

        if not c[0] or not c[3]:
            continue

        prices.append({
            "date": format_gsheet_date(c[0]["v"]),
            "market": c[1]["v"] if c[1] else "-",
            "size": int(c[2]["v"]) if c[2] else "-",
            "price": c[3]["v"]
        })

    return prices


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


# =========================
# Routes
# =========================
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

