#!/usr/bin/env python3

import asyncio
import websockets
import json

async def test_agent():
    """Test agenta przez WebSocket"""
    uri = "ws://localhost:8765"
    
    try:
        print(f"🔌 Łączę z {uri}...")
        async with websockets.connect(uri) as websocket:
            print("✅ Połączono z agentem!")
            
            # Czekaj na wiadomość powitalną
            welcome = await websocket.recv()
            print(f"📨 Wiadomość powitalna: {welcome}")
            
            # Test 1: Poproś o emaile od Aureliusza
            print("\n🧪 Test 1: Prośba o emaile od Aureliusza...")
            message1 = {
                "type": "message",
                "content": "szukaj emaili od Aureliusza Górskiego"
            }
            
            await websocket.send(json.dumps(message1))
            print("📤 Wysłano: szukaj emaili od Aureliusza Górskiego")
            
            # Odbierz odpowiedzi
            responses = []
            while True:
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=30.0)
                    data = json.loads(response)
                    print(f"📨 Odpowiedź: {data}")
                    
                    if data.get('type') == 'response_complete':
                        print("✅ Odpowiedź zakończona!")
                        break
                    elif data.get('type') == 'response_chunk':
                        responses.append(data.get('content', ''))
                        
                except asyncio.TimeoutError:
                    print("⏰ Timeout - kończę odbieranie")
                    break
                except Exception as e:
                    print(f"❌ Błąd odbioru: {e}")
                    break
            
            print(f"\n📋 Wszystkie odpowiedzi:")
            for i, resp in enumerate(responses):
                print(f"{i+1}. {resp}")
            
            # Test 2: Prośba o treść konkretnego emaila (jeśli agent zwróci ID)
            print("\n🧪 Test 2: Pytanie o kontekst...")
            message2 = {
                "type": "message", 
                "content": "pokaż treść najnowszego emaila od Aureliusza"
            }
            
            await websocket.send(json.dumps(message2))
            print("📤 Wysłano: pokaż treść najnowszego emaila od Aureliusza")
            
            # Odbierz odpowiedzi
            responses2 = []
            while True:
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=30.0)
                    data = json.loads(response)
                    print(f"📨 Odpowiedź 2: {data}")
                    
                    if data.get('type') == 'response_complete':
                        print("✅ Druga odpowiedź zakończona!")
                        break
                    elif data.get('type') == 'response_chunk':
                        responses2.append(data.get('content', ''))
                        
                except asyncio.TimeoutError:
                    print("⏰ Timeout - kończę odbieranie")
                    break
                except Exception as e:
                    print(f"❌ Błąd odbioru: {e}")
                    break
            
            print(f"\n📋 Drugie odpowiedzi:")
            for i, resp in enumerate(responses2):
                print(f"{i+1}. {resp}")
                
    except Exception as e:
        print(f"❌ Błąd połączenia: {e}")

if __name__ == "__main__":
    asyncio.run(test_agent()) 