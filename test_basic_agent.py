#!/usr/bin/env python3
"""
Test podstawowej funkcjonalności Business Avatar Agent
Bez zewnętrznych API keys - tylko podstawowe funkcje
"""

import asyncio
from google.adk.agents import LlmAgent
from google.adk.tools.function_tool import function_tool

class SimpleBusinessAgent:
    """Uproszczony agent do testów"""
    
    def __init__(self):
        self.setup_agent()
    
    def setup_agent(self):
        """Konfiguruje agenta z podstawowymi funkcjami"""
        
        # Podstawowe business funkcje (offline)
        basic_tools = [
            function_tool(self.get_current_time),
            function_tool(self.create_task_summary),
            function_tool(self.schedule_meeting),
            function_tool(self.analyze_productivity),
        ]
        
        self.agent = LlmAgent(
            model="gemini-2.0-flash",
            name="Simple_Business_Assistant",
            instruction="""
            Jesteś asystentem biznesowym MetaHuman w UE5.
            
            Możesz:
            - Sprawdzać czas i planować
            - Tworzyć podsumowania zadań  
            - Planować spotkania
            - Analizować produktywność
            
            Odpowiadaj krótko i konkretnie (dla avatar speech).
            Bądź profesjonalny ale przyjazny.
            """,
            tools=basic_tools
        )
    
    async def get_current_time(self) -> str:
        """Zwraca aktualny czas"""
        from datetime import datetime
        now = datetime.now()
        return f"⏰ Aktualny czas: {now.strftime('%H:%M:%S')}, data: {now.strftime('%d.%m.%Y')}"
    
    async def create_task_summary(self, project_name: str) -> str:
        """Tworzy podsumowanie zadań"""
        return f"""
        📋 PROJEKT: {project_name}
        
        Status: ✅ W realizacji
        Postęp: 75% ukończone
        Deadline: Za 3 dni
        
        Następne kroki:
        1. Finalizacja dokumentów
        2. Review zespołowy
        3. Prezentacja klientowi
        """
    
    async def schedule_meeting(self, title: str, duration: int = 60) -> str:
        """Planuje spotkanie"""
        return f"""
        📅 SPOTKANIE: {title}
        
        ⏰ Czas: {duration} minut
        📍 Status: Zaplanowane
        🔔 Przypomnienie: 15 min przed
        
        Czy potrzebujesz przygotować agenda?
        """
    
    async def analyze_productivity(self, period: str = "tydzień") -> str:
        """Analizuje produktywność"""
        return f"""
        📊 ANALIZA PRODUKTYWNOŚCI ({period}):
        
        ✅ Ukończone zadania: 12
        📞 Spotkania: 8  
        ⏱️  Średni czas fokus: 2.5h
        
        🎯 Rekomendacja: 
        Optymalizuj przerwy między spotkaniami
        """
    
    async def chat(self, message: str) -> str:
        """Podstawowa rozmowa z agentem"""
        try:
            # Tu będzie integracja z Google ADK
            # Na razie symulujemy odpowiedź
            if "czas" in message.lower():
                return await self.get_current_time()
            elif "spotkanie" in message.lower():
                return await self.schedule_meeting("Nowe spotkanie")
            elif "zadania" in message.lower():
                return await self.create_task_summary("Aktualny projekt")
            elif "produktywność" in message.lower():
                return await self.analyze_productivity()
            else:
                return f"👋 Witaj! Jestem Twoim asystentem biznesowym. Mogę pomóc z:\n- Planowaniem czasu\n- Zarządzaniem zadaniami\n- Analizą produktywności\n\nCo mogę dla Ciebie zrobić?"
                
        except Exception as e:
            return f"❌ Błąd: {str(e)}"

async def test_agent():
    """Test podstawowy agenta"""
    print("🤖 Uruchamiam Simple Business Agent...")
    
    agent = SimpleBusinessAgent()
    
    test_messages = [
        "Witaj!",
        "Jaki jest aktualny czas?", 
        "Zaplanuj spotkanie z zespołem",
        "Pokaż zadania dla projektu Alpha",
        "Przeanalizuj moją produktywność"
    ]
    
    for message in test_messages:
        print(f"\n👤 Użytkownik: {message}")
        response = await agent.chat(message)
        print(f"🤖 Assistant: {response}")
        print("-" * 50)

if __name__ == "__main__":
    asyncio.run(test_agent()) 