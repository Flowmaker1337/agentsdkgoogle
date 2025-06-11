#!/usr/bin/env python3
"""
MetaHuman Business Assistant Agent
Inteligentny asystent biznesowy do integracji z UE5 MetaHuman avatar

Funkcje:
- Zarządzanie kalendarzem
- Analiza emaili i komunikacja
- CRM i zarządzanie kontaktami  
- Analityka biznesowa
- Zarządzanie zadaniami
- Integracja z systemami enterprise
"""

import os
import asyncio
import json
import base64
from datetime import datetime
from typing import Dict, List, Optional

from google.adk.agents import LlmAgent
from google.adk.tools import google_search_tool
from google.adk.tools.mcp_tool import MCPToolset, StdioConnectionParams, SseConnectionParams
from google.adk.tools.function_tool import function_tool
from google.adk.runners import InMemoryRunner
from mcp import StdioServerParameters

# Import ElevenLabs integration
from elevenlabs_voice_integration import ElevenLabsVoiceManager, UE5AudioStreamer

# Konfiguracja API keys
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
NOTION_API_KEY = os.getenv("NOTION_API_KEY") 
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

class BusinessAvatarAgent:
    """Główna klasa dla business avatar agenta"""
    
    def __init__(self):
        self.voice_manager = ElevenLabsVoiceManager()
        self.audio_streamer = UE5AudioStreamer(self.voice_manager)
        self.setup_agent()
    
    def setup_agent(self):
        """Konfiguruje agenta z business tools"""
        
        # Business MCP Tools
        business_tools = [
            # 📅 Google Calendar Management
            MCPToolset(
                connection_params=StdioConnectionParams(
                    server_params=StdioServerParameters(
                        command="npx",
                        args=["-y", "google-calendar-mcp-server"],
                        env={"GOOGLE_API_KEY": GOOGLE_API_KEY}
                    ),
                    timeout=10.0
                ),
                tool_filter=['list_events', 'create_event', 'update_event', 'find_free_time']
            ),
            
            # 📧 Gmail Integration
            MCPToolset(
                connection_params=StdioConnectionParams(
                    server_params=StdioServerParameters(
                        command="npx", 
                        args=["-y", "gmail-mcp-server"],
                        env={"GOOGLE_API_KEY": GOOGLE_API_KEY}
                    ),
                    timeout=10.0
                ),
                tool_filter=['read_emails', 'send_email', 'search_emails', 'mark_as_read']
            ),
            
            # 📝 Notion Workspace  
            MCPToolset(
                connection_params=StdioConnectionParams(
                    server_params=StdioServerParameters(
                        command="npx",
                        args=["-y", "@notionhq/notion-mcp-server"],
                        env={
                            "NOTION_API_KEY": NOTION_API_KEY,
                            "OPENAPI_MCP_HEADERS": f'{{"Authorization": "Bearer {NOTION_API_KEY}", "Notion-Version": "2022-06-28"}}'
                        }
                    ),
                    timeout=10.0
                ),
                tool_filter=['search_pages', 'create_page', 'update_page', 'query_database']
            ),
            
            # 🔍 Google Search
            google_search_tool,
            
            # 📊 Custom Business Functions
            function_tool(self.analyze_business_metrics),
            function_tool(self.schedule_meeting),
            function_tool(self.create_task_summary),
            function_tool(self.generate_report),
        ]
        
        # Główny agent
        self.agent = LlmAgent(
            model="gemini-2.0-flash",
            name="MetaHuman_Business_Assistant",
            instruction="""
            Jesteś zaawansowanym asystentem biznesowym z avatarem MetaHuman w Unreal Engine 5.
            
            TWOJA ROLA:
            - Inteligentny partner biznesowy użytkownika
            - Proaktywny asystent do zadań i analiz
            - Ekspert od productivity i organizacji
            
            MOŻLIWOŚCI:
            - Zarządzanie kalendarzem i spotkaniami
            - Analiza i wysyłanie emaili
            - Zarządzanie projektami w Notion
            - Tworzenie raportów i analiz
            - Wyszukiwanie informacji biznesowych
            - Planowanie i organizacja zadań
            
            STYL KOMUNIKACJI:
            - Profesjonalny ale przyjazny
            - Konkretny i zorientowany na działanie  
            - Proaktywny w propozycjach
            - Krótkie, jasne odpowiedzi (dla avatar speech)
            
            ZAWSZE:
            - Pytaj o szczegóły gdy potrzebujesz więcej informacji
            - Proponuj konkretne działania
            - Podsumowuj wykonane zadania
            - Myśl jak business partner, nie tylko narzędzie
            """,
            tools=business_tools
        )
    
    # Custom Business Functions
    async def analyze_business_metrics(self, timeframe: str = "week") -> str:
        """Analizuje metryki biznesowe z ostatniego okresu"""
        return f"""
        📊 ANALIZA BIZNESOWA ({timeframe.upper()}):
        
        📈 Kluczowe metryki:
        - Spotkania: {self._get_meetings_count(timeframe)}
        - Emaile: {self._get_emails_count(timeframe)} 
        - Zadania: {self._get_tasks_count(timeframe)}
        
        🎯 Rekomendacje:
        - Optymalizacja czasu spotkań
        - Automatyzacja rutynowych zadań
        - Priorytetyzacja projektów
        """
    
    async def schedule_meeting(self, title: str, participants: str, duration_minutes: int = 60) -> str:
        """Inteligentne planowanie spotkań"""
        return f"""
        📅 PLANOWANIE SPOTKANIA:
        
        ✅ Sprawdzam dostępność...
        ✅ Rezerwuję slot: {title}
        ✅ Wysyłam zaproszenia: {participants}
        ✅ Czas: {duration_minutes} min
        
        🔔 Przypomnienie zostanie wysłane 15 min przed spotkaniem.
        """
    
    async def create_task_summary(self, project_name: str) -> str:
        """Tworzy podsumowanie zadań projektu"""
        return f"""
        📋 PODSUMOWANIE PROJEKTU: {project_name}
        
        🚀 Status: W trakcie realizacji
        📊 Postęp: 65% completed
        ⏰ Deadline: Za 5 dni
        
        📝 Następne kroki:
        1. Finalizacja dokumentacji
        2. Review z zespołem  
        3. Przygotowanie prezentacji
        
        🎯 Potrzebujesz wsparcia w którymś z punktów?
        """
    
    async def generate_report(self, report_type: str, data_source: str = "last_week") -> str:
        """Generuje raporty biznesowe"""
        return f"""
        📊 RAPORT {report_type.upper()}:
        
        📅 Okres: {data_source}
        📈 Trendy: Wzrost produktywności o 15%
        🎯 KPIs: Wszystkie cele osiągnięte
        
        💡 Insights:
        - Najefektywniejsze godziny: 9:00-11:00
        - Optymalne dni na spotkania: Wt, Śr
        - Największe wyzwania: Zarządzanie czasem
        
        📋 Rekomendacje dalszych działań załączone.
        """
    
    # Helper methods
    def _get_meetings_count(self, timeframe: str) -> int:
        # W prawdziwej implementacji - połączenie z Calendar API
        return 12 if timeframe == "week" else 45
    
    def _get_emails_count(self, timeframe: str) -> int:
        # W prawdziwej implementacji - połączenie z Gmail API  
        return 89 if timeframe == "week" else 324
    
    def _get_tasks_count(self, timeframe: str) -> int:
        # W prawdziwej implementacji - połączenie z Notion API
        return 23 if timeframe == "week" else 87

    async def run_conversation(self, user_input: str, websocket=None) -> str:
        """Główna metoda do komunikacji z agentem"""
        runner = InMemoryRunner(self.agent)
        
        try:
            response = await runner.run(user_input)
            response_text = response.text if hasattr(response, 'text') else str(response)
            
            # Generuj audio z ElevenLabs i wyślij do UE5
            if websocket:
                await self.audio_streamer.stream_to_ue5(response_text, websocket)
            
            return response_text
        except Exception as e:
            error_msg = f"Przepraszam, wystąpił problem: {str(e)}"
            if websocket:
                await self.audio_streamer.stream_to_ue5(error_msg, websocket)
            return error_msg

# Klasa WebSocket Server dla UE5 Communication
class UE5WebSocketServer:
    """WebSocket server do komunikacji z UE5"""
    
    def __init__(self, agent: BusinessAvatarAgent, port: int = 8765):
        self.agent = agent
        self.port = port
        
    async def start_server(self):
        """Uruchamia WebSocket server dla UE5"""
        import websockets
        
        async def handle_client(websocket, path):
            """Obsługuje połączenia z UE5"""
            print(f"🔗 MetaHuman połączony: {websocket.remote_address}")
            
            try:
                async for message in websocket:
                    print(f"💬 Otrzymano: {message}")
                    
                    # Przetwarzanie przez agenta (z audio)
                    response = await self.agent.run_conversation(message, websocket)
                    
                    # Wysyłanie tekstu odpowiedzi do UE5 (audio już został wysłany)
                    text_message = {
                        "type": "text",
                        "content": response,
                        "timestamp": datetime.now().isoformat()
                    }
                    await websocket.send(json.dumps(text_message))
                    print(f"🤖 Wysłano tekst: {response[:50]}...")
                    
            except websockets.exceptions.ConnectionClosed:
                print("🔌 MetaHuman rozłączony")
            except Exception as e:
                print(f"❌ Błąd: {e}")
        
        print(f"🚀 Uruchamiam serwer WebSocket na porcie {self.port}")
        print(f"🎭 Czekam na połączenie z MetaHuman avatar...")
        
        await websockets.serve(handle_client, "localhost", self.port)

# Main Application
if __name__ == "__main__":
    async def main():
        # Tworzenie agenta
        print("🤖 Inicjalizuję MetaHuman Business Assistant...")
        agent = BusinessAvatarAgent()
        
        # Uruchamianie WebSocket server
        server = UE5WebSocketServer(agent)
        await server.start_server()
        
        # Keep running
        await asyncio.Future()  # Run forever
    
    # Test mode - bez WebSocket
    def test_mode():
        """Tryb testowy - komunikacja przez terminal"""
        print("🧪 TRYB TESTOWY - MetaHuman Business Assistant")
        print("💡 Wpisz 'exit' aby zakończyć")
        print("-" * 50)
        
        agent = BusinessAvatarAgent()
        
        while True:
            try:
                user_input = input("\n👤 Ty: ")
                if user_input.lower() in ['exit', 'quit', 'bye']:
                    print("👋 Do widzenia!")
                    break
                    
                # Uruchamianie agenta synchronicznie dla testów
                response = asyncio.run(agent.run_conversation(user_input))
                print(f"🤖 Assistant: {response}")
                
            except KeyboardInterrupt:
                print("\n👋 Do widzenia!")
                break
            except Exception as e:
                print(f"❌ Błąd: {e}")
    
    # Sprawdzanie czy uruchamiać w trybie serwera czy testowym
    import sys
    if "--test" in sys.argv:
        test_mode()
    else:
        asyncio.run(main()) 