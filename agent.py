# agent/agent.py
import time
import subprocess
import shlex
import sys
import os
import signal
from pathlib import Path
import threading

from db import init_db, insert_event

# Config
POLL_SEC = 5
IDLE_THRESHOLD = 60  # segundos para considerar idle

def get_active_window_title():
    """
    Simples: usa xdotool (X11). Em Wayland esse método pode falhar.
    Requer: sudo apt install xdotool wmctrl
    """
    try:
        p = subprocess.run(shlex.split("xdotool getactivewindow getwindowname"),
                           capture_output=True, text=True, timeout=1)
        title = p.stdout.strip()
        if title:
            return title
    except Exception:
        pass
    return None

def get_active_window_pid():
    try:
        p = subprocess.run(shlex.split("xdotool getactivewindow getwindowpid"),
                           capture_output=True, text=True, timeout=1)
        pid = p.stdout.strip()
        return int(pid) if pid else None
    except Exception:
        return None

def get_idle_seconds_x11():
    """
    Usa xprintidle (milliseconds). sudo apt install xprintidle
    """
    try:
        p = subprocess.run(shlex.split("xprintidle"), capture_output=True, text=True, timeout=1)
        ms = int(p.stdout.strip())
        return ms / 1000.0
    except Exception:
        return 0

stop_flag = False

def signal_handler(sig, frame):
    global stop_flag
    stop_flag = True

def main_loop():
    init_db()
    last_title = None
    last_ts = int(time.time())
    last_active = time.time()
    while not stop_flag:
        ts = int(time.time())
        idle = get_idle_seconds_x11()
        if idle >= IDLE_THRESHOLD:
            # record idle event if not already idle
            if last_title != "__idle__":
                insert_event(ts, "idle", title="idle", detail=f"idle_seconds:{int(idle)}")
                last_title = "__idle__"
            time.sleep(POLL_SEC)
            continue

        title = get_active_window_title() or "unknown"
        pid = get_active_window_pid()
        detail = f"pid:{pid}"
        if title != last_title:
            # close previous with duration
            if last_title and last_title != "__idle__":
                dur = ts - last_ts
                insert_event(ts, "window", title=last_title, detail="ended", duration=dur)
            # new event start
            insert_event(ts, "window", title=title, detail=detail, duration=0)
            last_title = title
            last_ts = ts
        else:
            # update heartbeat by optionally writing no new row or update last row duration
            pass
        time.sleep(POLL_SEC)

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    print("Starting activity-tracker agent...")
    main_loop()
    print("Agent stopped.")
