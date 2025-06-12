#!/usr/bin/env python3
"""
🚀 Agent Launcher - Uruchamia wszystkie komponenty systemu Google ADK Business Agent

Uruchamia:
1. Session API (port 8000) - zarządzanie sesjami i Glass UI
2. Google ADK Business Agent (port 8765) - główny agent biznesowy

Użycie:
    python AgentLauncher.py

Zatrzymanie:
    Ctrl+C (zatrzyma wszystkie procesy)
"""

import subprocess
import sys
import time
import signal
import os
from pathlib import Path

class AgentLauncher:
    def __init__(self):
        self.processes = []
        self.running = True
        
    def log(self, message, level="INFO"):
        """Logowanie z kolorami"""
        colors = {
            "INFO": "\033[94m",    # Niebieski
            "SUCCESS": "\033[92m", # Zielony
            "WARNING": "\033[93m", # Żółty
            "ERROR": "\033[91m",   # Czerwony
            "RESET": "\033[0m"     # Reset
        }
        
        timestamp = time.strftime("%H:%M:%S")
        color = colors.get(level, colors["INFO"])
        reset = colors["RESET"]
        print(f"{color}[{timestamp}] {level}: {message}{reset}")
    
    def check_dependencies(self):
        """Sprawdza czy wszystkie wymagane pliki istnieją"""
        self.log("🔍 Sprawdzanie zależności...")
        
        required_files = [
            "session_api.py",
            "google_adk_business_agent.py",
            "modern_glass_agent_ui.html"
        ]
        
        missing_files = []
        for file in required_files:
            if not Path(file).exists():
                missing_files.append(file)
        
        if missing_files:
            self.log(f"❌ Brakujące pliki: {', '.join(missing_files)}", "ERROR")
            return False
        
        self.log("✅ Wszystkie wymagane pliki znalezione", "SUCCESS")
        return True
    
    def check_ports(self):
        """Sprawdza czy porty są wolne"""
        self.log("🔍 Sprawdzanie portów...")
        
        import socket
        
        def is_port_free(port):
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.bind(('localhost', port))
                    return True
            except OSError:
                return False
        
        ports_to_check = [8000, 8765]
        busy_ports = []
        
        for port in ports_to_check:
            if not is_port_free(port):
                busy_ports.append(port)
        
        if busy_ports:
            self.log(f"⚠️ Porty zajęte: {', '.join(map(str, busy_ports))}", "WARNING")
            self.log("💡 Spróbuj: pkill -f session_api.py && pkill -f google_adk_business_agent.py", "INFO")
            return False
        
        self.log("✅ Wszystkie porty wolne", "SUCCESS")
        return True
    
    def start_session_api(self):
        """Uruchamia Session API"""
        self.log("🚀 Uruchamianie Session API (port 8000)...")
        
        try:
            process = subprocess.Popen(
                [sys.executable, "session_api.py"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            self.processes.append(("Session API", process))
            self.log("✅ Session API uruchomione", "SUCCESS")
            return process
            
        except Exception as e:
            self.log(f"❌ Błąd uruchamiania Session API: {e}", "ERROR")
            return None
    
    def start_business_agent(self):
        """Uruchamia Google ADK Business Agent"""
        self.log("🤖 Uruchamianie Google ADK Business Agent (port 8765)...")
        
        try:
            process = subprocess.Popen(
                [sys.executable, "google_adk_business_agent.py"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            self.processes.append(("Business Agent", process))
            self.log("✅ Business Agent uruchomiony", "SUCCESS")
            return process
            
        except Exception as e:
            self.log(f"❌ Błąd uruchamiania Business Agent: {e}", "ERROR")
            return None
    
    def wait_for_services(self):
        """Czeka aż serwisy będą gotowe"""
        self.log("⏳ Czekam na uruchomienie serwisów...")
        
        # Czekaj na Session API
        for i in range(30):  # 30 sekund timeout
            try:
                import requests
                response = requests.get("http://localhost:8000/api/health", timeout=1)
                if response.status_code == 200:
                    self.log("✅ Session API gotowe", "SUCCESS")
                    break
            except:
                pass
            time.sleep(1)
        else:
            self.log("⚠️ Session API może nie być gotowe", "WARNING")
        
        # Krótka pauza dla Business Agent
        time.sleep(3)
        self.log("✅ Business Agent powinien być gotowy", "SUCCESS")
    
    def show_status(self):
        """Pokazuje status uruchomionych serwisów"""
        self.log("📊 Status serwisów:", "INFO")
        print("\n" + "="*60)
        print("🎯 GOOGLE ADK BUSINESS AGENT - SYSTEM URUCHOMIONY")
        print("="*60)
        print("📡 Session API:          http://localhost:8000")
        print("🎨 Glass UI:             http://localhost:8000")
        print("📖 API Docs:             http://localhost:8000/docs")
        print("🤖 Business Agent:       ws://localhost:8765")
        print("="*60)
        print("💡 Otwórz przeglądarkę: http://localhost:8000")
        print("🛑 Zatrzymanie: Ctrl+C")
        print("="*60 + "\n")
    
    def monitor_processes(self):
        """Monitoruje procesy i wyświetla logi"""
        self.log("👀 Rozpoczynam monitorowanie procesów...")
        
        while self.running:
            try:
                # Sprawdź czy procesy nadal działają
                for name, process in self.processes:
                    if process.poll() is not None:
                        self.log(f"❌ Proces {name} zakończył się nieoczekiwanie", "ERROR")
                        self.cleanup()
                        return
                
                time.sleep(1)
                
            except KeyboardInterrupt:
                self.log("🛑 Otrzymano sygnał zatrzymania", "WARNING")
                break
    
    def cleanup(self):
        """Zatrzymuje wszystkie procesy"""
        self.log("🧹 Zatrzymywanie procesów...")
        self.running = False
        
        for name, process in self.processes:
            if process.poll() is None:  # Proces nadal działa
                self.log(f"🛑 Zatrzymywanie {name}...")
                try:
                    process.terminate()
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    self.log(f"⚡ Wymuszam zatrzymanie {name}...")
                    process.kill()
                except Exception as e:
                    self.log(f"❌ Błąd zatrzymywania {name}: {e}", "ERROR")
        
        self.log("✅ Wszystkie procesy zatrzymane", "SUCCESS")
    
    def signal_handler(self, signum, frame):
        """Obsługa sygnałów (Ctrl+C)"""
        self.log("🛑 Otrzymano sygnał zatrzymania...", "WARNING")
        self.cleanup()
        sys.exit(0)
    
    def run(self):
        """Główna funkcja uruchamiająca system"""
        # Rejestruj obsługę sygnałów
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        print("\n" + "="*60)
        print("🚀 GOOGLE ADK BUSINESS AGENT LAUNCHER")
        print("="*60)
        
        # Sprawdź zależności
        if not self.check_dependencies():
            sys.exit(1)
        
        # Sprawdź porty
        if not self.check_ports():
            sys.exit(1)
        
        # Uruchom serwisy
        session_api = self.start_session_api()
        if not session_api:
            sys.exit(1)
        
        # Krótka pauza między uruchomieniami
        time.sleep(2)
        
        business_agent = self.start_business_agent()
        if not business_agent:
            self.cleanup()
            sys.exit(1)
        
        # Czekaj na gotowość serwisów
        self.wait_for_services()
        
        # Pokaż status
        self.show_status()
        
        # Otwórz przeglądarkę
        try:
            import webbrowser
            time.sleep(2)
            webbrowser.open("http://localhost:8000")
            self.log("🌐 Otwarto przeglądarkę", "SUCCESS")
        except Exception as e:
            self.log(f"⚠️ Nie można otworzyć przeglądarki: {e}", "WARNING")
        
        # Monitoruj procesy
        try:
            self.monitor_processes()
        except KeyboardInterrupt:
            pass
        finally:
            self.cleanup()

def main():
    """Punkt wejścia"""
    launcher = AgentLauncher()
    launcher.run()

if __name__ == "__main__":
    main() 