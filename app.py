from flask import Flask, render_template, redirect, url_for

app = Flask(__name__)
import requests, json
def get_price_from_gsheet():
    url = "https://docs.google.com/spreadsheets/d/1z8sWAjtDtdMNxqS41QejImOXBmPQtEszRP249ewf5es/gviz/tq?tqx=out:json&gid=1530942221"
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
