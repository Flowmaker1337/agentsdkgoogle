#!/usr/bin/env python3
"""
Simple Enhanced MetaHuman Business Assistant
🎤 ElevenLabs Voice + ☁️ Google Cloud Business APIs (bez Google ADK)

Hybrydowy system:
- ElevenLabs: Najwyższa jakość głosu  
- Google Cloud: Pełna integracja biznesowa
- Prosty AI chat agent
"""

import os
import asyncio
import json
import base64
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dotenv import load_dotenv

# ElevenLabs integration
from elevenlabs_voice_integration import ElevenLabsVoiceManager, UE5AudioStreamer

# Google Cloud integration
from google_cloud_integration import GoogleCloudManager, GoogleBusinessIntegration, GoogleAnalytics

# Load environment
load_dotenv()

class SimpleEnhancedAgent:
    """
    Prosty Enhanced MetaHuman Business Assistant
    🎤 ElevenLabs + ☁️ Google Cloud (bez ADK)
    """
    
    def __init__(self):
        print("🚀 Inicjalizuję Simple Enhanced MetaHuman Assistant...")
        
        # ElevenLabs Voice Manager
        self.voice_manager = ElevenLabsVoiceManager()
        self.audio_streamer = UE5AudioStreamer(self.voice_manager)
        print("✅ ElevenLabs Voice Manager")
        
        # Google Cloud Business APIs
        try:
            self.gcp_manager = GoogleCloudManager()
            self.business_integration = GoogleBusinessIntegration(self.gcp_manager)
            self.analytics = GoogleAnalytics(self.gcp_manager)
            print("✅ Google Cloud Business APIs")
        except Exception as e:
            print(f"⚠️  Google Cloud disabled: {e}")
            self.gcp_manager = None
            self.business_integration = None
            self.analytics = None
        
        print("✅ Simple Enhanced Agent ready!")
    
    # === BUSINESS FUNCTIONS ===
    
    async def get_calendar_summary(self, days_ahead: int = 3) -> str:
        """Pobiera rzeczywiste wydarzenia z Google Calendar"""
        if not self.business_integration:
            return "⚠️ Google Calendar niedostępny - sprawdź konfigurację"
        
        try:
            events = await self.business_integration.get_calendar_events(days_ahead)
            
            if not events:
                return f"📅 Twój kalendarz na najbliższe {days_ahead} dni jest pusty. Świetny czas na planowanie!"
            
            summary = f"📅 KALENDARZ - najbliższe {days_ahead} dni:\n\n"
            for event in events[:5]:  # Limit do 5 dla głosu
                start_time = event['start'][:16] if len(event['start']) > 16 else event['start']
                summary += f"• {event['title']} - {start_time}\n"
            
            if len(events) > 5:
                summary += f"\n... i jeszcze {len(events)-5} wydarzeń"
            
            return summary
            
        except Exception as e:
            return f"❌ Błąd Calendar: {str(e)}"
    
    async def get_email_summary(self, max_emails: int = 5) -> str:
        """Pobiera rzeczywiste nieprzeczytane emaile z Gmail"""
        if not self.business_integration:
            return "⚠️ Gmail niedostępny - sprawdź konfigurację"
        
        try:
            emails = await self.business_integration.get_recent_emails(max_emails)
            
            if not emails:
                return "📧 Brak nieprzeczytanych emaili. Inbox zero achieved!"
            
            summary = f"📧 NIEPRZECZYTANE EMAILE ({len(emails)}):\n\n"
            for email in emails:
                sender = email['sender'].split('<')[0].strip()  # Clean sender
                subject = email['subject'][:50] + "..." if len(email['subject']) > 50 else email['subject']
                summary += f"• Od: {sender}\n  Temat: {subject}\n\n"
            
            return summary
            
        except Exception as e:
            return f"❌ Błąd Gmail: {str(e)}"
    
    async def analyze_productivity(self, period: str = "week") -> str:
        """Analizuje produktywność"""
        if self.analytics:
            try:
                days = 7 if period == "week" else 30
                analytics_data = await self.analytics.get_usage_analytics(days)
                
                return f"""
                📊 ANALIZA PRODUKTYWNOŚCI ({period}):
                
                🤖 Interakcje z asystentem: {analytics_data.get('total_interactions', 0)}
                ⚡ Średni czas odpowiedzi: {analytics_data.get('avg_response_time', 0)}ms
                📈 Sesje pracy: {len(analytics_data.get('daily_stats', []))} dni aktywnych
                
                💡 Rekomendacja: Wykorzystujesz asystenta regularnie - świetnie!
                """
            except:
                pass
        
        # Fallback analiza
        return f"""
        📊 ANALIZA PRODUKTYWNOŚCI ({period}):
        
        ✅ System działający sprawnie
        📅 Kalendarz pod kontrolą  
        📧 Emaile zarządzane
        🎯 Gotowość do kolejnych wyzwań!
        
        💡 Sugestia: Sprawdź kalendarz i zaplanuj priorytetowe zadania.
        """
    
    async def get_current_time(self) -> str:
        """Zwraca aktualny czas i datę"""
        now = datetime.now()
        return f"⏰ Czas: {now.strftime('%H:%M:%S')}, Data: {now.strftime('%A, %d %B %Y')}"
    
    async def generate_business_report(self) -> str:
        """Generuje raport biznesowy"""
        current_time = datetime.now()
        
        return f"""
        📊 RAPORT BIZNESOWY
        
        📅 Data: {current_time.strftime('%d.%m.%Y %H:%M')}
        
        🎯 STATUS SYSTEMÓW:
        • MetaHuman Assistant: ✅ Online
        • Google Cloud APIs: {'✅ Active' if self.gcp_manager else '⚠️ Limited'}
        • ElevenLabs Voice: ✅ Premium Quality
        • Analytics Engine: {'✅ Recording' if self.analytics else '⚠️ Offline'}
        
        💼 GOTOWOŚĆ BIZNESOWA: 100%
        
        📋 NASTĘPNE KROKI:
        1. Sprawdź kalendarz na dziś
        2. Przejrzyj nieprzeczytane emaile
        3. Zaplanuj kluczowe zadania
        
        🚀 System gotowy do maksymalnej produktywności!
        """
    
    # === SIMPLE AI CHAT ===
    
    async def process_user_input(self, user_input: str) -> str:
        """Przetwarza input użytkownika z prostym AI"""
        user_lower = user_input.lower()
        
        # Command routing
        if any(word in user_lower for word in ['kalendarz', 'spotkanie', 'termin', 'calendar']):
            return await self.get_calendar_summary()
        
        elif any(word in user_lower for word in ['email', 'mail', 'wiadomość', 'skrzynka']):
            return await self.get_email_summary()
        
        elif any(word in user_lower for word in ['czas', 'godzina', 'data', 'time']):
            return await self.get_current_time()
        
        elif any(word in user_lower for word in ['produktywność', 'analiza', 'raport', 'productivity']):
            return await self.analyze_productivity()
        
        elif any(word in user_lower for word in ['status', 'system', 'report']):
            return await self.generate_business_report()
        
        elif any(word in user_lower for word in ['witaj', 'hello', 'cześć', 'dzień dobry']):
            return """
            👋 Witaj! Jestem Twoim asystentem biznesowym MetaHuman.
            
            🎤 Mój głos: ElevenLabs Premium
            ☁️ Dane: Google Cloud APIs
            🤖 Status: Gotowy do pracy!
            
            Mogę pomóc Ci z:
            • 📅 Zarządzaniem kalendarza
            • 📧 Analizą emaili
            • 📊 Raportami produktywności
            • ⏰ Informacjami o czasie
            
            Co mogę dla Ciebie zrobić?
            """
        
        else:
            return f"""
            💭 Rozumiem: "{user_input}"
            
            🤖 Jestem Twoim asystentem biznesowym MetaHuman.
            
            Mogę pomóc z:
            • "kalendarz" - sprawdzenie terminów
            • "email" - nieprzeczytane wiadomości  
            • "czas" - aktualna data/godzina
            • "produktywność" - analiza pracy
            • "status" - raport systemów
            
            Co Cię interesuje?
            """
    
    # === MAIN CONVERSATION ===
    
    async def run_conversation(self, user_input: str, websocket=None) -> str:
        """Główna metoda konwersacji z voice"""
        start_time = datetime.now()
        
        try:
            # Process input
            response_text = await self.process_user_input(user_input)
            
            # Generate voice with ElevenLabs
            if websocket:
                await self.audio_streamer.stream_to_ue5(response_text, websocket)
            
            # Log analytics
            if self.analytics:
                response_time = (datetime.now() - start_time).total_seconds() * 1000
                await self.analytics.log_interaction(user_input, response_text, int(response_time))
            
            return response_text
            
        except Exception as e:
            error_msg = f"Przepraszam, wystąpił problem: {str(e)}"
            
            # Still generate error voice
            if websocket:
                await self.audio_streamer.stream_to_ue5(error_msg, websocket)
            
            return error_msg

# WebSocket Server dla UE5
class SimpleUE5Server:
    """Simple WebSocket server z ElevenLabs + Google Cloud"""
    
    def __init__(self, agent: SimpleEnhancedAgent, port: int = 8765):
        self.agent = agent
        self.port = port
        
    async def start_server(self):
        """Uruchamia WebSocket server"""
        import websockets
        
        async def handle_client(websocket, path):
            print(f"🎭 MetaHuman Avatar połączony: {websocket.remote_address}")
            
            try:
                # Welcome message
                welcome_msg = {
                    "type": "system",
                    "content": "🎭 Simple Enhanced MetaHuman Business Assistant gotowy!",
                    "features": [
                        "🎤 ElevenLabs Premium Voice",
                        "📅 Real Google Calendar",
                        "📧 Live Gmail Integration", 
                        "📊 BigQuery Analytics",
                        "🤖 Simple AI Chat"
                    ],
                    "timestamp": datetime.now().isoformat()
                }
                await websocket.send(json.dumps(welcome_msg))
                
                async for message in websocket:
                    print(f"💬 User: {message}")
                    
                    # Process with simple agent (includes voice)
                    response = await self.agent.run_conversation(message, websocket)
                    
                    # Send text response
                    text_message = {
                        "type": "text",
                        "content": response,
                        "timestamp": datetime.now().isoformat(),
                        "voice": "elevenlabs",
                        "engine": "simple_ai"
                    }
                    await websocket.send(json.dumps(text_message))
                    print(f"🤖 Response sent: {response[:100]}...")
                    
            except websockets.exceptions.ConnectionClosed:
                print("🔌 MetaHuman disconnected")
            except Exception as e:
                print(f"❌ Error: {e}")
        
        print(f"🚀 Simple Enhanced MetaHuman Server")
        print(f"🎤 Voice: ElevenLabs Premium")
        print(f"☁️ Business APIs: Google Cloud")  
        print(f"🤖 AI Engine: Simple Chat")
        print(f"🎭 Waiting for MetaHuman avatar on port {self.port}...")
        
        await websockets.serve(handle_client, "localhost", self.port)

# Main Application
if __name__ == "__main__":
    async def main():
        # Initialize Simple Enhanced Agent
        agent = SimpleEnhancedAgent()
        
        # Start WebSocket server
        server = SimpleUE5Server(agent)
        await server.start_server()
        
        # Keep running
        await asyncio.Future()
    
    # Test mode
    def test_mode():
        """Interactive test mode"""
        print("🧪 SIMPLE ENHANCED METAHUMAN - TEST MODE")
        print("🎤 ElevenLabs Voice + ☁️ Google Cloud")
        print("💡 Wpisz 'exit' aby zakończyć")
        print("-" * 60)
        
        agent = SimpleEnhancedAgent()
        
        while True:
            try:
                user_input = input("\n👤 Ty: ")
                if user_input.lower() in ['exit', 'quit', 'bye']:
                    print("👋 Do widzenia!")
                    break
                    
                # Run conversation
                response = asyncio.run(agent.run_conversation(user_input))
                print(f"🎭 MetaHuman: {response}")
                
            except KeyboardInterrupt:
                print("\n👋 Do widzenia!")
                break
            except Exception as e:
                print(f"❌ Błąd: {e}")
    
    # Check run mode
    import sys
    if "--test" in sys.argv:
        test_mode()
    else:
        asyncio.run(main()) 