from flask import Flask, render_template, redirect, url_for

app = Flask(__name__)
import requests, json

def get_price_from_gsheet():
    url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vT6x4gRN0oCi3gUzWQsAFl4BdefiaRg2EsSahflCpfCT7l4Ahokeq5vV2PCEtMJvrilljmVdVQOMLZO/gviz/tq?tqx=out:json&gid=1530942221"

    r = requests.get(url, timeout=15)
    text = r.text
    json_data = text[text.find("{"):text.rfind("}")+1]
    data = json.loads(json_data)

    rows = data["table"]["rows"]
    prices = []

    for row in rows[-7:]:
        c = row["c"]
        prices.append({
            "date": c[0]["v"],
            "size": c[1]["v"],
            "price": c[2]["v"]
        })

    return prices

@app.route("/")
def home():
    return redirect(url_for("dashboard"))

@app.route("/dashboard")
def dashboard():
    prices = get_price_from_gsheet()
    return render_template("dashboard.html", prices=prices)

