#!/usr/bin/env python3
"""
Test script dla funkcji wysyłania maili w agencie
"""
import asyncio
import websockets
import json
import time

async def test_email_sending():
    """Test funkcji wysyłania maili przez WebSocket"""
    
    # URL agenta WebSocket
    agent_url = "ws://localhost:8765"
    
    # Testy do wykonania
    test_cases = [
        {
            "name": "Test funkcji wysyłania maili - lista funkcji",
            "message": "jakie funkcje mailerów masz dostępne?",
            "expected": "send_gmail_message"
        },
        {
            "name": "Test wysyłania testowego maila",
            "message": "wyślij testowy email do kdunowski@district.org z tematem 'Test Agent Mail' i treścią 'To jest test wysyłania maili przez agenta. Funkcja działa poprawnie!'",
            "expected": "success"
        },
        {
            "name": "Test sprawdzenia funkcji",
            "message": "czy masz możliwość wysyłania emaili?",
            "expected": "send_gmail_message"
        }
    ]
    
    try:
        print(f"🔌 Łączenie z agentem: {agent_url}")
        
        async with websockets.connect(agent_url) as websocket:
            print("✅ Połączono z agentem WebSocket")
            
            # Poczekaj na wiadomość powitalną
            try:
                welcome_msg = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                print(f"📨 Otrzymano wiadomość powitalną: {welcome_msg}")
            except asyncio.TimeoutError:
                print("⚠️ Nie otrzymano wiadomości powitalnej (timeout)")
            
            # Wykonaj testy
            for i, test_case in enumerate(test_cases, 1):
                print(f"\n🧪 Test {i}/{len(test_cases)}: {test_case['name']}")
                print(f"💬 Pytanie: {test_case['message']}")
                
                # Wyślij wiadomość
                message_data = {
                    "message": test_case['message'],
                    "timestamp": time.time()
                }
                
                await websocket.send(json.dumps(message_data))
                print("📤 Wiadomość wysłana")
                
                # Oczekuj odpowiedzi (z timeoutem)
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=30.0)
                    print(f"📥 Odpowiedź otrzymana: {response[:200]}...")
                    
                    # Parsuj odpowiedź
                    try:
                        response_data = json.loads(response)
                        if response_data.get("type") == "response":
                            print(f"✅ Odpowiedź agenta: {response_data.get('message', 'Brak treści')}")
                            
                            # Sprawdź czy odpowiedź zawiera oczekiwane słowa kluczowe
                            response_text = response_data.get('message', '').lower()
                            if test_case['expected'].lower() in response_text:
                                print(f"✅ Test ZALICZONY - znaleziono: '{test_case['expected']}'")
                            else:
                                print(f"⚠️ Test może być niepełny - nie znaleziono: '{test_case['expected']}'")
                        else:
                            print(f"📝 Odebrano inny typ wiadomości: {response_data.get('type', 'unknown')}")
                    
                    except json.JSONDecodeError:
                        print(f"📝 Odpowiedź (raw text): {response}")
                
                except asyncio.TimeoutError:
                    print(f"❌ Timeout - brak odpowiedzi w ciągu 30 sekund")
                
                # Pauza między testami
                if i < len(test_cases):
                    print("⏳ Czekam 3 sekundy przed następnym testem...")
                    await asyncio.sleep(3)
            
            print(f"\n🎉 Ukończono wszystkie testy!")
            
    except ConnectionRefusedError:
        print(f"❌ Nie można połączyć się z agentem na {agent_url}")
        print("💡 Sprawdź czy agent działa: python google_adk_business_agent.py")
    except Exception as e:
        print(f"❌ Błąd testu: {e}")

if __name__ == "__main__":
    print("🚀 Rozpoczynam test funkcji wysyłania maili agenta...")
    asyncio.run(test_email_sending()) 