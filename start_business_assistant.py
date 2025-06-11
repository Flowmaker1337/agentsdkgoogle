#!/usr/bin/env python3
"""
MetaHuman Business Assistant Launcher
Prosty skrypt do uruchomienia asystenta biznesowego

Użycie:
    python start_business_assistant.py --test    # Tryb testowy (terminal)
    python start_business_assistant.py           # Tryb serwera (WebSocket dla UE5)
"""

import sys
import os
import asyncio
from pathlib import Path

# Dodaj katalog z agentem do ścieżki Python
current_dir = Path(__file__).parent
sys.path.append(str(current_dir))

def check_dependencies():
    """Sprawdza czy wszystkie wymagane pakiety są zainstalowane"""
    required_packages = [
        'google.adk',
        'websockets',
        'dotenv'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ Brakujące pakiety:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\n💡 Uruchom: pip install -r requirements.txt")
        return False
    
    return True

def check_environment():
    """Sprawdza konfigurację środowiska"""
    env_file = current_dir / '.env'
    
    if not env_file.exists():
        print("⚠️  Brak pliku .env")
        print("💡 Skopiuj env_example.txt jako .env i uzupełnij API keys")
        
        # Automatyczne kopiowanie przykładu
        example_file = current_dir / 'env_example.txt'
        if example_file.exists():
            import shutil
            shutil.copy(example_file, env_file)
            print("✅ Skopiowano env_example.txt -> .env")
        
        return False
    
    # Sprawdź czy są ustawione podstawowe klucze
    from dotenv import load_dotenv
    load_dotenv(env_file)
    
    google_key = os.getenv('GOOGLE_API_KEY')
    if not google_key or google_key == 'your_google_ai_studio_key_here':
        print("⚠️  Brak klucza GOOGLE_API_KEY w pliku .env")
        print("💡 Pobierz klucz z https://makersuite.google.com/app/apikey")
        return False
    
    return True

def check_npm_servers():
    """Sprawdza czy MCP serwery są zainstalowane"""
    required_servers = [
        '@notionhq/notion-mcp-server'
    ]
    
    print("🔍 Sprawdzam MCP serwery...")
    
    for server in required_servers:
        result = os.system(f"npm list -g {server} > /dev/null 2>&1")
        if result != 0:
            print(f"⚠️  Brak serwera: {server}")
            print(f"💡 Zainstaluj: npm install -g {server}")

def main():
    """Główna funkcja launchera"""
    
    print("🚀 MetaHuman Business Assistant Launcher")
    print("=" * 50)
    
    # Sprawdzenie zależności
    print("🔍 Sprawdzam zależności...")
    if not check_dependencies():
        sys.exit(1)
    
    print("✅ Pakiety Python: OK")
    
    # Sprawdzenie konfiguracji
    print("🔍 Sprawdzam konfigurację...")
    if not check_environment():
        print("❌ Popraw konfigurację i uruchom ponownie")
        sys.exit(1)
    
    print("✅ Konfiguracja: OK")
    
    # Sprawdzenie MCP serwerów
    check_npm_servers()
    
    # Import agenta (po sprawdzeniu zależności)
    try:
        from business_avatar_agent import BusinessAvatarAgent, UE5WebSocketServer
        print("✅ Business Agent: Załadowany")
    except ImportError as e:
        print(f"❌ Błąd importu agenta: {e}")
        sys.exit(1)
    
    # Wybór trybu uruchomienia
    if "--test" in sys.argv:
        print("\n🧪 Uruchamiam w trybie testowym...")
        test_mode()
    else:
        print("\n🎭 Uruchamiam serwer WebSocket dla UE5...")
        print("🔗 Adres: ws://localhost:8765")
        print("💡 W UE5 połącz się z tym adresem")
        print("❌ Ctrl+C aby zakończyć")
        asyncio.run(server_mode())

def test_mode():
    """Tryb testowy - komunikacja przez terminal"""
    from business_avatar_agent import BusinessAvatarAgent
    
    print("\n" + "="*50)
    print("🧪 TRYB TESTOWY - MetaHuman Business Assistant")
    print("💡 Przetestuj funkcje agenta przed integracją z UE5")
    print("💬 Wpisz 'help' aby zobaczyć przykłady")
    print("❌ Wpisz 'exit' aby zakończyć")
    print("="*50)
    
    agent = BusinessAvatarAgent()
    
    # Przykłady komend
    examples = [
        "Sprawdź mój kalendarz na dziś",
        "Przygotuj raport sprzedaży z tego tygodnia", 
        "Zaplanuj spotkanie z zespołem na jutro",
        "Napisz email do klienta o projekcie",
        "Pokaż analizę biznesową za ostatni miesiąc"
    ]
    
    while True:
        try:
            user_input = input(f"\n👤 Ty: ").strip()
            
            if user_input.lower() in ['exit', 'quit', 'bye']:
                print("👋 Do widzenia!")
                break
            elif user_input.lower() == 'help':
                print("\n💡 Przykładowe komendy:")
                for i, example in enumerate(examples, 1):
                    print(f"   {i}. {example}")
                continue
            elif not user_input:
                continue
            
            print("🤖 Myślę...")
            
            # Uruchomienie agenta
            response = asyncio.run(agent.run_conversation(user_input))
            print(f"🎭 MetaHuman Assistant: {response}")
            
        except KeyboardInterrupt:
            print("\n👋 Do widzenia!")
            break
        except Exception as e:
            print(f"❌ Błąd: {e}")

async def server_mode():
    """Tryb serwera WebSocket dla UE5"""
    from business_avatar_agent import BusinessAvatarAgent, UE5WebSocketServer
    
    try:
        # Tworzenie agenta
        print("🤖 Inicjalizuję Business Agent...")
        agent = BusinessAvatarAgent()
        
        # Uruchamianie WebSocket server
        print("🔗 Uruchamiam WebSocket serwer...")
        server = UE5WebSocketServer(agent, port=8765)
        await server.start_server()
        
        # Keep running
        print("✅ Serwer uruchomiony!")
        print("🎭 Czekam na połączenie z MetaHuman...")
        await asyncio.Future()  # Run forever
        
    except KeyboardInterrupt:
        print("\n👋 Zamykam serwer...")
    except Exception as e:
        print(f"❌ Błąd serwera: {e}")

if __name__ == "__main__":
    main() 