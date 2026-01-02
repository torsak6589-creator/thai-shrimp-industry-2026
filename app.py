from flask import Flask, render_template, jsonify
import requests, json

app = Flask(__name__)

GSHEET_ID = "1z8sWAjtDtdMNxqS41QejImOXBmPQtEszRP249ewf5es"
GSHEET_URL = f"https://docs.google.com/spreadsheets/d/{GSHEET_ID}/gviz/tq?tqx=out:json"

def get_price_from_gsheet():
    r = requests.get(GSHEET_URL)
    text = r.text
    json_str = text[text.find("{"):text.rfind("}")+1]
    data = json.loads(json_str)

    prices = []
    rows = data["table"]["rows"]

    for r in rows[-10:]:
        if r["c"] and r["c"][2]:
            prices.append({
                "date": r["c"][0]["v"],
                "size": r["c"][1]["v"],
                "price": r["c"][2]["v"]
            })

    return prices


@app.route("/")
def home():
    return "Thai Shrimp Industry 2026 API is running"


@app.route("/dashboard")
def dashboard():
    prices = get_price_from_gsheet()
    return render_template("dashboard.html", prices=prices)


@app.route("/api/prices")
def api_prices():
    return jsonify(get_price_from_gsheet())


if __name__ == "__main__":
    app.run(debug=True)



