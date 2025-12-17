from flask import Flask, render_template, request
import json

app = Flask(__name__)

with open("data/shrimp_2026.json", encoding="utf-8") as f:
    data = json.load(f)

@app.route("/")
def index():
    lang = request.args.get("lang", "th")
    return render_template("index.html", data=data, lang=lang)

if __name__ == "__main__":
    app.run()
