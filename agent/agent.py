#!/usr/bin/env python3
# agent/agent.py
import time
import subprocess
import shlex
import sys
import os
import signal
import logging
from pathlib import Path
import threading
from datetime import datetime

from db import init_db, insert_event, update_last_event_duration

# Config
POLL_SEC = 5
IDLE_THRESHOLD = 60  # segundos para considerar idle

# Setup logging
LOG_DIR = Path.home() / ".activity_tracker"
LOG_DIR.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / "agent.log"),
        logging.StreamHandler()
    ]
)


def get_active_window_title():
    """
    Detecta janela ativa. Tenta X11 primeiro, depois Wayland.
    Requer: sudo apt install xdotool wmctrl (X11) ou ydotool (Wayland)
    """
    # Tenta X11
    try:
        p = subprocess.run(
            shlex.split("xdotool getactivewindow getwindowname"),
            capture_output=True, text=True, timeout=1, check=False
        )
        if p.returncode == 0:
            title = p.stdout.strip()
            if title:
                return title
    except Exception as e:
        logging.debug(f"X11 window detection failed: {e}")
    
    # Fallback: tenta wmctrl
    try:
        p = subprocess.run(
            shlex.split("wmctrl -l"),
            capture_output=True, text=True, timeout=1, check=False
        )
        if p.returncode == 0:
            lines = p.stdout.strip().split('\n')
            if lines:
                # pega última linha (geralmente a janela ativa)
                parts = lines[-1].split(None, 3)
                if len(parts) >= 4:
                    return parts[3]
    except Exception as e:
        logging.debug(f"wmctrl detection failed: {e}")
    
    # Para Wayland seria necessário usar gdbus ou ferramentas específicas
    # Mas isso varia por compositor (GNOME Shell, Sway, etc.)
    
    return "unknown"

def get_active_window_pid():
    """Obtém PID da janela ativa (X11 apenas)"""
    try:
        p = subprocess.run(
            shlex.split("xdotool getactivewindow getwindowpid"),
            capture_output=True, text=True, timeout=1, check=False
        )
        if p.returncode == 0:
            pid = p.stdout.strip()
            return int(pid) if pid else None
    except Exception:
        pass
    return None


def get_idle_seconds_x11():
    """
    Usa xprintidle (milliseconds). sudo apt install xprintidle
    """
    try:
        p = subprocess.run(
            shlex.split("xprintidle"),
            capture_output=True, text=True, timeout=1, check=False
        )
        if p.returncode == 0:
            ms = int(p.stdout.strip())
            return ms / 1000.0
    except Exception as e:
        logging.debug(f"xprintidle failed: {e}")
    return 0

stop_flag = False
last_event_id = None

def signal_handler(sig, frame):
    global stop_flag
    logging.info(f"Received signal {sig}, stopping agent...")
    stop_flag = True


def main_loop():
    global last_event_id
    init_db()
    logging.info("Activity tracker agent started")
    
    last_title = None
    last_ts = int(time.time())
    
    while not stop_flag:
        try:
            ts = int(time.time())
            idle = get_idle_seconds_x11()
            
            if idle >= IDLE_THRESHOLD:
                # record idle event if not already idle
                if last_title != "__idle__":
                    if last_event_id and last_title and last_title != "__idle__":
                        dur = ts - last_ts
                        update_last_event_duration(last_event_id, dur)
                    
                    last_event_id = insert_event(
                        ts, "idle", 
                        title="Sistema Ocioso", 
                        detail=f"idle_seconds:{int(idle)}"
                    )
                    last_title = "__idle__"
                    last_ts = ts
                    logging.info(f"User idle detected ({int(idle)}s)")
                time.sleep(POLL_SEC)
                continue

            title = get_active_window_title()
            pid = get_active_window_pid()
            detail = f"pid:{pid}" if pid else "no_pid"
            
            if title != last_title:
                # close previous event with duration
                if last_event_id and last_title and last_title != "__idle__":
                    dur = ts - last_ts
                    update_last_event_duration(last_event_id, dur)
                    logging.info(f"Closed: {last_title} (duration: {dur}s)")
                
                # new event start
                last_event_id = insert_event(ts, "window", title=title, detail=detail, duration=0)
                logging.info(f"New window: {title}")
                last_title = title
                last_ts = ts
            else:
                # Atualiza duração do evento atual periodicamente
                if last_event_id:
                    dur = ts - last_ts
                    update_last_event_duration(last_event_id, dur)
                    
        except Exception as e:
            logging.error(f"Error in main loop: {e}", exc_info=True)
        
        time.sleep(POLL_SEC)
    
    # Final cleanup
    if last_event_id and last_title:
        dur = int(time.time()) - last_ts
        update_last_event_duration(last_event_id, dur)
    
    logging.info("Activity tracker agent stopped")

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    print("Starting activity-tracker agent...")
    print(f"Logs: {LOG_DIR / 'agent.log'}")
    main_loop()
    print("Agent stopped.")
