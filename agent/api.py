#!/usr/bin/env python3
# agent/api.py
from flask import Flask, jsonify, send_from_directory, request
from flask_cors import CORS
from db import fetch_events, insert_event, init_db
import time
from pathlib import Path
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

app = Flask(__name__, static_folder="static", template_folder="static")
CORS(app)  # Permite requisições da extensão do navegador
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

@app.route("/api/log_event", methods=["POST"])
def log_event():
    """Endpoint para extensão do navegador e outros clientes enviarem eventos"""
    try:
        data = request.get_json()
        ts = data.get("ts", int(time.time()))
        typ = data.get("type", "unknown")
        title = data.get("title", "")
        detail = data.get("detail", "")
        duration = data.get("duration", 0)
        
        event_id = insert_event(ts, typ, title, detail, duration)
        logging.info(f"Event logged: {typ} - {title}")
        
        return jsonify({"success": True, "event_id": event_id}), 200
    except Exception as e:
        logging.error(f"Error logging event: {e}")
        return jsonify({"success": False, "error": str(e)}), 400

@app.route("/api/stats")
def stats():
    """Estatísticas do dia"""
    now = int(time.time())
    day_start = now - (now % 86400)
    rows = fetch_events(day_start, now, limit=10000)
    
    total_time = 0
    by_type = {}
    by_title = {}
    
    for r in rows:
        typ = r[2]
        title = r[3] or "unknown"
        dur = r[5] or 0
        
        total_time += dur
        by_type[typ] = by_type.get(typ, 0) + dur
        
        if typ in ["window", "website", "whatsapp", "telegram", "facebook", "twitter", "youtube"]:
            by_title[title] = by_title.get(title, 0) + dur
    
    # Top 10 atividades
    top_activities = sorted(by_title.items(), key=lambda x: x[1], reverse=True)[:10]
    
    return jsonify({
        "total_seconds": total_time,
        "by_type": by_type,
        "top_activities": [{"title": t, "seconds": s} for t, s in top_activities]
    })

@app.route("/api/summary")
def daily_summary():
    """Gera resumo inteligente do dia usando IA"""
    try:
        from ai_summarizer import ActivitySummarizer
        
        use_ollama = request.args.get("ollama", "true").lower() == "true"
        summarizer = ActivitySummarizer(use_ollama=use_ollama)
        summary = summarizer.generate_daily_summary()
        
        return summary, 200, {"Content-Type": "text/markdown; charset=utf-8"}
    except Exception as e:
        logging.error(f"Error generating summary: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/categories")
def categories():
    """Retorna atividades categorizadas"""
    try:
        from ai_summarizer import ActivitySummarizer
        
        summarizer = ActivitySummarizer()
        activities = summarizer.get_daily_activities()
        categories = summarizer.categorize_activities(activities)
        
        return jsonify(categories)
    except Exception as e:
        logging.error(f"Error getting categories: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    logging.info("Starting Activity Tracker API on port 5001")
    app.run(host="0.0.0.0", port=5001, debug=False)
