#!/usr/bin/env python3
"""
🚀 Prosty starter dla Google ADK Business Agent

Szybkie uruchomienie systemu:
    python start.py
"""

import subprocess
import sys
import time
import webbrowser
from pathlib import Path

def main():
    print("🚀 Uruchamianie Google ADK Business Agent...")
    
    # Sprawdź czy pliki istnieją
    if not Path("session_api.py").exists():
        print("❌ Brak pliku session_api.py")
        sys.exit(1)
    
    if not Path("google_adk_business_agent.py").exists():
        print("❌ Brak pliku google_adk_business_agent.py")
        sys.exit(1)
    
    try:
        # Uruchom Session API w tle
        print("📡 Uruchamianie Session API...")
        session_process = subprocess.Popen([sys.executable, "session_api.py"])
        
        # Poczekaj chwilę
        time.sleep(3)
        
        # Uruchom Business Agent w tle
        print("🤖 Uruchamianie Business Agent...")
        agent_process = subprocess.Popen([sys.executable, "google_adk_business_agent.py"])
        
        # Poczekaj na uruchomienie
        time.sleep(5)
        
        # Otwórz przeglądarkę
        print("🌐 Otwieranie przeglądarki...")
        webbrowser.open("http://localhost:8000")
        
        print("\n" + "="*50)
        print("✅ System uruchomiony!")
        print("📡 Session API: http://localhost:8000")
        print("🤖 Business Agent: ws://localhost:8765")
        print("🛑 Zatrzymanie: Ctrl+C w obu terminalach")
        print("="*50)
        
    except KeyboardInterrupt:
        print("\n🛑 Zatrzymywanie...")
    except Exception as e:
        print(f"❌ Błąd: {e}")

if __name__ == "__main__":
    main() 