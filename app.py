from flask import Flask, render_template, jsonify
import requests, json, os

app = Flask(__name__)

GSHEET_ID = "1z8sWAjtDtdMNxqS41QejImOXBmPQtEszRP249ewf5es"
GSHEET_GID = "0"
GSHEET_URL = f"https://docs.google.com/spreadsheets/d/{GSHEET_ID}/gviz/tq?tqx=out:json&gid={GSHEET_GID}"

def get_price_from_gsheet():
    r = requests.get(GSHEET_URL, timeout=15)
    text = r.text
    json_str = text[text.find("{"):text.rfind("}")+1]
    data = json.loads(json_str)

    prices = []
    for row in data["table"]["rows"][-10:]:
        c = row["c"]

        if not c or not c[0] or not c[1] or not c[2] or not c[3]:
            continue

        prices.append({
            "date": c[0]["v"],          # Date
            "market": c[1]["v"],        # Songkhla
            "size": c[2]["v"],          # 60
            "price": c[3]["v"],         # 160
            "type": c[4]["v"] if len(c) > 4 and c[4] else ""
        })

    return prices
        
@app.route("/")
def dashboard():
    return render_template("dashboard.html", prices=get_price_from_gsheet())

@app.route("/api/prices")
def api_prices():
    return jsonify(get_price_from_gsheet())

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

