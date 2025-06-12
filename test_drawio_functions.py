#!/usr/bin/env python3
"""
Test script dla funkcji draw.io w agencie
"""
import asyncio
import websockets
import json
import time

async def test_drawio_functions():
    """Test funkcji draw.io przez WebSocket"""
    
    # URL agenta WebSocket
    agent_url = "ws://localhost:8765"
    
    # Testy do wykonania
    test_cases = [
        {
            "name": "List draw.io files",
            "message": "znajdź pliki draw.io",
            "expected": "list_drawio_files"
        },
        {
            "name": "Search for metaverse in draw.io",
            "message": "pliki draw.io z metaverse",
            "expected": "search_drawio_diagrams"
        },
        {
            "name": "General draw.io search",
            "message": "znajdz diagramy z tekstem metalayers",
            "expected": "search_drawio_diagrams"
        }
    ]
    
    try:
        # Połącz się z agentem
        print("🔗 Łączenie z agentem...")
        async with websockets.connect(agent_url) as websocket:
            
            # Otrzymaj wiadomość powitalną
            welcome = await websocket.recv()
            print(f"📨 Powitanie: {welcome}")
            
            # Wykonaj testy
            for i, test in enumerate(test_cases, 1):
                print(f"\n🧪 Test {i}: {test['name']}")
                print(f"📤 Wysyłam: {test['message']}")
                
                # Wyślij wiadomość testową
                message = {
                    "type": "message",
                    "message": test['message'],
                    "timestamp": time.time()
                }
                
                await websocket.send(json.dumps(message))
                
                # Czekaj na odpowiedź
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=30)
                    print(f"📥 Otrzymano odpowiedź ({len(response)} znaków)")
                    
                    # Sprawdź czy odpowiedź zawiera oczekiwane informacje
                    response_data = json.loads(response) if response.startswith('{') else {"text": response}
                    print(f"✅ Status: {'OK' if 'error' not in str(response_data).lower() else 'ERROR'}")
                    
                    if len(str(response_data)) > 200:
                        print(f"📋 Odpowiedź: {str(response_data)[:200]}...")
                    else:
                        print(f"📋 Odpowiedź: {response_data}")
                    
                except asyncio.TimeoutError:
                    print("⚠️ Timeout - brak odpowiedzi w ciągu 30 sekund")
                
                # Przerwa między testami
                await asyncio.sleep(2)
            
            print("\n✅ Wszystkie testy zakończone!")
            
    except Exception as e:
        print(f"❌ Błąd połączenia z agentem: {e}")
        print("💡 Upewnij się, że agent działa na ws://localhost:8765")

if __name__ == "__main__":
    print("🎨 Test funkcji draw.io w agencie...")
    asyncio.run(test_drawio_functions()) 