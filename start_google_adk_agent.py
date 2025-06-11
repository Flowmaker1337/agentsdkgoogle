#!/usr/bin/env python3
"""
Launcher dla Google ADK Business Agent
Sprawdza zależności, instaluje Google ADK i uruchamia agenta
"""

import os
import sys
import subprocess
import json
from pathlib import Path

def check_python_version():
    """Sprawdź wersję Pythona"""
    if sys.version_info < (3, 9):
        print("❌ Wymagany Python 3.9 lub nowszy")
        print(f"   Obecna wersja: {sys.version}")
        return False
    
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    return True

def check_google_adk():
    """Sprawdź czy Google ADK jest dostępne"""
    adk_path = Path("adk-python")
    
    if not adk_path.exists():
        print("❌ Google ADK nie znalezione")
        print("   Klonowanie repozytorium...")
        
        try:
            subprocess.run([
                "git", "clone", 
                "https://github.com/google/adk-python.git"
            ], check=True)
            print("✅ Google ADK sklonowane pomyślnie")
        except subprocess.CalledProcessError:
            print("❌ Błąd klonowania Google ADK")
            return False
    
    # Sprawdź czy ADK jest zainstalowane
    adk_src = adk_path / "src"
    if adk_src.exists():
        print("✅ Google ADK dostępne")
        return True
    else:
        print("❌ Google ADK nieprawidłowo zainstalowane")
        return False

def install_requirements():
    """Zainstaluj wymagane pakiety"""
    requirements_file = "requirements_google_adk.txt"
    
    if not Path(requirements_file).exists():
        print(f"❌ Brak pliku {requirements_file}")
        return False
    
    print("📦 Instalowanie zależności...")
    try:
        subprocess.run([
            sys.executable, "-m", "pip", "install", 
            "-r", requirements_file
        ], check=True)
        print("✅ Zależności zainstalowane")
        return True
    except subprocess.CalledProcessError:
        print("❌ Błąd instalacji zależności")
        return False

def check_environment():
    """Sprawdź Google Cloud credentials"""
    # Sprawdź czy istnieje plik credentials
    credentials_path = "google_cloud_credentials.json"
    
    if os.path.exists(credentials_path):
        print("✅ Google Cloud Service Account credentials znalezione")
        # Ustaw zmienną środowiskową
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path
        
        # Sprawdź czy credentials są prawidłowe
        try:
            with open(credentials_path, 'r') as f:
                creds = json.load(f)
                project_id = creds.get('project_id')
                if project_id:
                    print(f"✅ Project ID: {project_id}")
                    os.environ["GOOGLE_CLOUD_PROJECT"] = project_id
                    return True
                else:
                    print("❌ Nieprawidłowy format credentials")
                    return False
        except Exception as e:
            print(f"❌ Błąd odczytywania credentials: {e}")
            return False
    else:
        print("❌ Brak pliku google_cloud_credentials.json")
        print("📝 Potrzebujesz:")
        print("   - Plik google_cloud_credentials.json z Service Account")
        print("   - Domain-Wide Delegation skonfigurowane w Google Admin Console")
        return False

def create_env_file():
    """Stwórz opcjonalny plik .env dla dodatkowej konfiguracji"""
    env_content = """# Google ADK Business Agent - Opcjonalna konfiguracja
# ======================================================
# Agent używa google_cloud_credentials.json jako główne źródło credentials

# Gmail Configuration (dla Domain-Wide Delegation)
GMAIL_DELEGATED_USER=kdunowski@district.org

# Vertex AI RAG Configuration (opcjonalne)
VERTEX_AI_RAG_CORPUS_NAME=business-knowledge-corpus
VERTEX_AI_RAG_REGION=us-central1

# WebSocket Server Configuration
WEBSOCKET_HOST=localhost
WEBSOCKET_PORT=8765

# Logging Configuration
LOG_LEVEL=INFO

# Opcjonalne: Google Search Engine ID (jeśli używasz Google Search)
GOOGLE_SEARCH_ENGINE_ID=your-search-engine-id

# MCP Tools Configuration
MCP_GMAIL_ENABLED=true
MCP_CALENDAR_ENABLED=true
"""
    
    env_file = Path(".env")
    if not env_file.exists():
        with open(env_file, "w") as f:
            f.write(env_content)
        print("✅ Utworzono opcjonalny plik .env")
    else:
        print("ℹ️  Plik .env już istnieje")

def test_google_adk_import():
    """Testuj import Google ADK"""
    try:
        # Dodaj ścieżkę do ADK
        adk_path = os.path.join(os.path.dirname(__file__), 'adk-python', 'src')
        if adk_path not in sys.path:
            sys.path.insert(0, adk_path)
        
        # Testuj import
        from google.adk.agents import LlmAgent
        from google.adk.models import Gemini
        from google.adk.tools import FunctionTool
        print("✅ Google ADK importuje się poprawnie")
        print(f"   - LlmAgent: {LlmAgent}")
        print(f"   - Gemini: {Gemini}")
        return True
    except ImportError as e:
        print(f"❌ Błąd importu Google ADK: {e}")
        return False

def main():
    """Główna funkcja launchera"""
    print("""
🤖 Google ADK Business Agent Launcher
====================================
    """)
    
    # Sprawdzenia
    checks = [
        ("Python Version", check_python_version),
        ("Google ADK", check_google_adk),
        ("Dependencies", install_requirements),
        ("Google Cloud Credentials", check_environment),
        ("ADK Import", test_google_adk_import)
    ]
    
    for name, check_func in checks:
        print(f"\n🔍 Sprawdzanie: {name}")
        if not check_func():
            print(f"\n❌ {name} - sprawdzenie nieudane")
            create_env_file()
            return False
    
    print("\n✅ Wszystkie sprawdzenia przeszły pomyślnie!")
    
    # Uruchom agenta
    print("\n🚀 Uruchamianie Google ADK Business Agent...")
    try:
        from google_adk_business_agent import main as agent_main
        import asyncio
        asyncio.run(agent_main())
    except KeyboardInterrupt:
        print("\n⏹️  Agent zatrzymany przez użytkownika")
    except Exception as e:
        print(f"\n❌ Błąd uruchamiania agenta: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        print("\n❌ Sprawdź błędy powyżej i spróbuj ponownie")
        sys.exit(1)
    else:
        print("\n✅ Google ADK Business Agent zakończył pracę") 