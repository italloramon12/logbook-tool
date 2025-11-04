# agent/api.py
from flask import Flask, jsonify, send_from_directory, request
from db import fetch_events, insert_event, init_db
import time
from pathlib import Path

app = Flask(__name__, static_folder="static", template_folder="static")
init_db()

@app.route("/")
def index():
    return send_from_directory("static", "index.html")

@app.route("/api/events")
def events():
    start = request.args.get("start", type=int)
    end = request.args.get("end", type=int)
    rows = fetch_events(start, end, limit=5000)
    out = []
    for r in rows:
        out.append({
            "id": r[0],
            "ts": r[1],
            "type": r[2],
            "title": r[3],
            "detail": r[4],
            "duration": r[5]
        })
    return jsonify(out)

@app.route("/api/export_markdown")
def export_md():
    # Gera um markdown simples do dia atual
    now = int(time.time())
    day_start = now - (now % 86400)
    rows = fetch_events(day_start, now, limit=10000)
    lines = ["# Logbook diário\n"]
    for r in rows:
        ts = r[1]
        tstr = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(ts))
        typ = r[2]
        title = r[3] or ""
        detail = r[4] or ""
        dur = r[5] or 0
        lines.append(f"- **{tstr}** [{typ}] {title} — {detail} — {dur}s")
    md = "\n".join(lines)
    return md, 200, {"Content-Type": "text/markdown; charset=utf-8"}

if __name__ == "__main__":
    app.run(port=5001)
