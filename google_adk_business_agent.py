#!/usr/bin/env python3
"""
Google ADK Business Agent - Prawdziwy agent biznesowy używający Google ADK Framework
Obsługuje zadania biznesowe, kalendarz, email, notatki i analizy
"""

import os
import sys
import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import websockets
from websockets.server import WebSocketServerProtocol
import pytz
import traceback

# Dodaj ścieżkę do Google ADK
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'adk-python', 'src'))

# Import Google ADK
from google.adk.agents import LlmAgent
from google.adk.models import Gemini
from google.adk.tools import FunctionTool, BaseTool, google_search
from google.adk.tools.google_api_tool import GmailToolset, CalendarToolset
# OAuth2 credentials będą automatycznie wykryte z pliku oauth2_credentials.json
# RAG imports - opcjonalne
try:
    from google.adk.tools.retrieval import VertexAiRagRetrieval
    from google.adk.memory import VertexAiRagMemoryService
    RAG_AVAILABLE = True
except ImportError:
    RAG_AVAILABLE = False
    logger.warning("⚠️ Vertex AI RAG niedostępne - kontynuuję bez RAG")
from google.adk.sessions import Session
from google.genai import types
from google.adk.agents.run_config import RunConfig
from google.adk.runners import InMemoryRunner
from google.adk.sessions.in_memory_session_service import InMemorySessionService
from google.adk.agents.invocation_context import InvocationContext, new_invocation_context_id
from google.adk.artifacts.in_memory_artifact_service import InMemoryArtifactService
from google.adk.memory.in_memory_memory_service import InMemoryMemoryService

# Konfiguracja logowania
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Funkcje biznesowe jako zwykłe funkcje (będą opakowane w FunctionTool)

async def get_current_datetime() -> Dict[str, Any]:
    """Pobierz aktualną datę i czas w Polsce oraz informacje o dniu"""
    poland_tz = pytz.timezone('Europe/Warsaw')
    now = datetime.now(poland_tz)
    
    # Polskie nazwy dni tygodnia
    days_polish = {
        0: "poniedziałek", 1: "wtorek", 2: "środa", 3: "czwartek",
        4: "piątek", 5: "sobota", 6: "niedziela"
    }
    
    # Polskie nazwy miesięcy
    months_polish = {
        1: "stycznia", 2: "lutego", 3: "marca", 4: "kwietnia",
        5: "maja", 6: "czerwca", 7: "lipca", 8: "sierpnia",
        9: "września", 10: "października", 11: "listopada", 12: "grudnia"
    }
    
    day_name = days_polish[now.weekday()]
    month_name = months_polish[now.month]
    
    return {
        "current_date": now.strftime("%Y-%m-%d"),
        "current_time": now.strftime("%H:%M:%S"),
        "day_of_week": day_name,
        "formatted_date": f"{day_name}, {now.day} {month_name} {now.year} roku",
        "timezone": "Europe/Warsaw (CET/CEST)",
        "timestamp": now.isoformat(),
        "is_weekend": now.weekday() >= 5,
        "hour": now.hour,
        "minute": now.minute
    }

async def schedule_meeting(title: str, date: str, time: str, 
                         participants: List[str], description: str = "") -> Dict[str, Any]:
    """Zaplanuj spotkanie biznesowe"""
    logger.info(f"Planowanie spotkania: {title} na {date} {time}")
    
    meeting = {
        "id": f"meeting_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "title": title,
        "date": date,
        "time": time,
        "participants": participants,
        "description": description,
        "status": "scheduled",
        "created_at": datetime.now().isoformat()
    }
    
    return {
        "success": True,
        "meeting": meeting,
        "message": f"Spotkanie '{title}' zostało zaplanowane na {date} o {time}"
    }

async def analyze_email(emails: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Analizuj wiadomości email pod kątem priorytetów"""
    logger.info(f"Analizowanie {len(emails)} emaili")
    
    high_priority = []
    medium_priority = []
    low_priority = []
    
    for email in emails:
        subject = email.get('subject', '').lower()
        sender = email.get('sender', '').lower()
        
        # Priorytyzacja na podstawie słów kluczowych
        if any(word in subject for word in ['urgent', 'pilne', 'asap', 'natychmiast']):
            high_priority.append(email)
        elif any(word in subject for word in ['meeting', 'spotkanie', 'projekt', 'deadline']):
            medium_priority.append(email)
        else:
            low_priority.append(email)
    
    return {
        "high_priority": high_priority,
        "medium_priority": medium_priority,
        "low_priority": low_priority,
        "total_analyzed": len(emails),
        "recommendations": [
            "Najpierw odpowiedz na emaile wysokiego priorytetu",
            "Zaplanuj czas na spotkania z emaili średniego priorytetu",
            "Emaile niskiego priorytetu można przetworzyć w czasie wolnym"
        ]
    }

async def create_business_report(report_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """Stwórz raport biznesowy"""
    logger.info(f"Tworzenie raportu: {report_type}")
    
    report = {
        "id": f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "type": report_type,
        "created_at": datetime.now().isoformat(),
        "data": data,
        "summary": f"Raport {report_type} wygenerowany automatycznie",
        "recommendations": [],
        "charts": []
    }
    
    if report_type == "sales":
        report["summary"] = "Analiza wyników sprzedażowych"
        report["recommendations"] = [
            "Zwiększ aktywność marketingową w Q2",
            "Skup się na najlepiej sprzedających się produktach",
            "Popraw konwersję w kanale online"
        ]
    elif report_type == "financial":
        report["summary"] = "Przegląd sytuacji finansowej"
        report["recommendations"] = [
            "Zoptymalizuj koszty operacyjne",
            "Rozważ nowe źródła przychodów",
            "Monitoruj cash flow"
        ]
    
    return {
        "success": True,
        "report": report,
        "message": f"Raport {report_type} został wygenerowany"
    }

async def task_management(action: str, task_data: Dict[str, Any]) -> Dict[str, Any]:
    """Zarządzaj zadaniami i projektami"""
    logger.info(f"Zarządzanie zadaniami: {action}")
    
    if action == "create":
        task = {
            "id": f"task_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "title": task_data.get("title"),
            "priority": task_data.get("priority", "medium"),
            "deadline": task_data.get("deadline"),
            "assigned_to": task_data.get("assigned_to"),
            "status": "pending",
            "created_at": datetime.now().isoformat()
        }
        return {"success": True, "task": task, "message": "Zadanie zostało utworzone"}
    
    elif action == "list":
        # Symulacja listy zadań
        tasks = [
            {"id": "task_001", "title": "Przygotuj prezentację Q1", "priority": "high", "status": "in_progress"},
            {"id": "task_002", "title": "Spotkanie z klientem ABC", "priority": "medium", "status": "pending"},
            {"id": "task_003", "title": "Aktualizuj dokumentację", "priority": "low", "status": "pending"}
        ]
        return {"success": True, "tasks": tasks, "count": len(tasks)}
    
    return {"success": False, "message": "Nieznana akcja"}

async def financial_analysis(analysis_type: str, period: str, 
                           data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Wykonaj analizę finansową"""
    logger.info(f"Analiza finansowa: {analysis_type} za okres {period}")
    
    analysis = {
        "type": analysis_type,
        "period": period,
        "created_at": datetime.now().isoformat(),
        "metrics": {},
        "trends": [],
        "recommendations": []
    }
    
    if analysis_type == "revenue":
        analysis["metrics"] = {
            "total_revenue": 125000,
            "growth_rate": 15.2,
            "avg_deal_size": 2500
        }
        analysis["trends"] = ["Wzrost przychodów o 15%", "Stabilny wzrost klientów"]
        analysis["recommendations"] = [
            "Kontynuuj obecną strategię sprzedażową",
            "Rozważ ekspansję na nowe rynki"
        ]
    elif analysis_type == "costs":
        analysis["metrics"] = {
            "total_costs": 85000,
            "operational_costs": 60000,
            "marketing_costs": 25000
        }
        analysis["trends"] = ["Koszty operacyjne stabilne", "Wzrost kosztów marketingu"]
        analysis["recommendations"] = [
            "Zoptymalizuj procesy operacyjne",
            "Zmierz ROI kampanii marketingowych"
        ]
    
    return {
        "success": True,
        "analysis": analysis,
        "message": f"Analiza {analysis_type} została wykonana"
    }

async def analyze_and_store_email(
    email_content: str,
    sender: str = "unknown",
    subject: str = "no subject"
) -> Dict[str, Any]:
    """
    Automatyczna klasyfikacja i analiza emaili do bazy wiedzy RAG
    
    Args:
        email_content: Treść emaila
        sender: Nadawca emaila  
        subject: Temat emaila
    """
    logger.info(f"🧠 Analizuję email od {sender}: {subject}")
    
    # Klasyfikacja biznesowa emaila
    categories = []
    priority = "medium"
    
    content_lower = email_content.lower()
    
    # Kategoryzacja
    if any(word in content_lower for word in ["projekt", "zadanie", "deadline", "termin"]):
        categories.append("zarządzanie_projektami")
    if any(word in content_lower for word in ["sprzedaż", "klient", "oferta", "zamówienie"]):
        categories.append("sprzedaż")
    if any(word in content_lower for word in ["finanse", "budżet", "płatność", "faktura"]):
        categories.append("finanse")
    if any(word in content_lower for word in ["spotkanie", "meeting", "konferencja"]):
        categories.append("spotkania")
    if any(word in content_lower for word in ["pilne", "urgent", "asap", "natychmiast"]):
        priority = "high"
        categories.append("pilne")
    
    # Wyciągnij kluczowe informacje
    key_entities = []
    if "@" in email_content:
        key_entities.append("kontakt_email")
    if "zł" in email_content or "$" in email_content or "EUR" in email_content:
        key_entities.append("kwoty_finansowe")
    
    result = {
        "sender": sender,
        "subject": subject,
        "categories": categories or ["inne"],
        "priority": priority,
        "key_entities": key_entities,
        "processed_at": datetime.now().isoformat(),
        "summary": f"Email od {sender} w kategoriach: {', '.join(categories or ['inne'])}",
        "action_required": priority == "high" or "spotkanie" in content_lower,
        "rag_ready": True  # Oznacza że email jest gotowy do dodania do RAG
    }
    
    logger.info(f"📧 Email sklasyfikowany: {result}")
    
    return {
        "success": True,
        "classification": result,
        "message": f"Email od {sender} został przeanalizowany i sklasyfikowany"
    }

# Dodaj callbacks dla bezpieczeństwa i logowania
def business_before_model_callback(callback_context, llm_request):
    """Callback wykonywany przed każdym wywołaniem LLM"""
    logger.info(f"🧠 LLM Call dla agenta: {callback_context.agent_name}")
    
    # Dodaj business context do każdego zapytania
    business_prefix = f"[BUSINESS AGENT | AGENT: {callback_context.agent_name}] "
    
    # Modyfikuj system instruction
    original_instruction = llm_request.config.system_instruction or types.Content(role="system", parts=[])
    if not isinstance(original_instruction, types.Content):
        original_instruction = types.Content(role="system", parts=[types.Part(text=str(original_instruction))])
    if not original_instruction.parts:
        original_instruction.parts.append(types.Part(text=""))
    
    # Dodaj business context
    modified_text = business_prefix + (original_instruction.parts[0].text or "")
    original_instruction.parts[0].text = modified_text
    llm_request.config.system_instruction = original_instruction
    
    logger.info(f"🧠 System instruction wzbogacony o business context")
    return None

def business_before_tool_callback(**kwargs):
    """Callback wykonywany przed każdym wywołaniem narzędzia"""
    # Obsługa różnych sygnatur callback funkcji
    callback_context = kwargs.get('callback_context')
    tool = kwargs.get('tool')
    function_call_id = kwargs.get('function_call_id')
    args = kwargs.get('args')
    
    if tool and hasattr(tool, 'name'):
        tool_name = tool.name
    elif 'tool' in kwargs and isinstance(kwargs['tool'], str):
        tool_name = kwargs['tool']
    else:
        tool_name = "unknown_tool"
    
    if callback_context and hasattr(callback_context, 'agent_name'):
        agent_name = callback_context.agent_name
    else:
        agent_name = "unknown_agent"
    
    logger.info(f"🔧 Tool Call: {tool_name} dla agenta: {agent_name}")
    
    # Bezpieczeństwo - nie pozwól usuwać wszystkich wydarzeń
    if tool_name == "delete_calendar_event":
        logger.warning("🚫 Sprawdzenie bezpieczeństwa dla delete_calendar_event")
    
    # Loguj użycie narzędzi Google API
    if tool_name in ["create_calendar_event", "get_gmail_messages", "get_calendar_events", "create_google_doc", "list_google_docs"]:
        if callback_context and hasattr(callback_context, 'state'):
            tools_used = callback_context.state.get("google_tools_used", [])
            tools_used.append({
                "tool": tool_name,
                "timestamp": datetime.now().isoformat(),
                "agent": agent_name,
                "function_call_id": function_call_id,
                "args": str(args) if args else None
            })
            callback_context.state["google_tools_used"] = tools_used
    
    return None

def business_after_tool_callback(**kwargs):
    """Callback wykonywany po każdym wywołaniu narzędzia"""
    # Obsługa różnych sygnatur callback funkcji
    callback_context = kwargs.get('callback_context')
    tool = kwargs.get('tool')
    function_call_id = kwargs.get('function_call_id')
    tool_response = kwargs.get('tool_response')
    
    if tool and hasattr(tool, 'name'):
        tool_name = tool.name
    elif 'tool' in kwargs and isinstance(kwargs['tool'], str):
        tool_name = kwargs['tool']
    else:
        tool_name = "unknown_tool"
    
    logger.info(f"🔧 Tool Response: {tool_name} - Response: {str(tool_response)[:100]}...")
    
    # Zlicz statystyki użycia narzędzi
    if callback_context and hasattr(callback_context, 'state'):
        tool_stats = callback_context.state.get("tool_statistics", {})
        tool_stats[tool_name] = tool_stats.get(tool_name, 0) + 1
        callback_context.state["tool_statistics"] = tool_stats
        
        # Specjalna obróbka dla Google Calendar events
        if tool_name == "create_calendar_event":
            if isinstance(tool_response, dict) and tool_response.get('success'):
                logger.info(f"✅ Utworzono wydarzenie w Google Calendar: {tool_response.get('event_id', 'N/A')}")
                
                # Zapisz ID utworzonego wydarzenia w sesji
                created_events = callback_context.state.get("created_events", [])
                created_events.append({
                    "event_id": tool_response.get('event_id'),
                    "title": tool_response.get('title', 'Bez tytułu'),
                    "created_at": datetime.now().isoformat()
                })
                callback_context.state["created_events"] = created_events
    
    return None

def business_after_agent_callback(callback_context):
    """Callback wykonywany po zakończeniu pracy agenta"""
    
    # Podsumowanie sesji
    tool_stats = callback_context.state.get("tool_statistics", {})
    google_tools = callback_context.state.get("google_tools_used", [])
    created_events = callback_context.state.get("created_events", [])
    
    logger.info(f"📊 Agent {callback_context.agent_name} - Statystyki:")
    logger.info(f"📊 Użyte narzędzia: {tool_stats}")
    logger.info(f"📊 Google API calls: {len(google_tools)}")
    logger.info(f"📊 Utworzone wydarzenia: {len(created_events)}")
    
    return None

class GoogleADKBusinessAgent:
    """Główny agent biznesowy używający Google ADK"""
    
    def __init__(self):
        self.agent = None
        self.server = None
        self.connected_clients = set()
        
        # POPRAWKA: Globalny session service i runner zgodnie z dokumentacją Google ADK
        self.session_service = None
        self.runner = None
        
        # NOWE: Mapa WebSocket -> session_id dla utrzymania kontekstu
        self.websocket_sessions = {}  # websocket -> {"session_id": str, "user_id": str}
    
    async def setup_agent(self):
        """Konfiguracja Google ADK Agent"""
        logger.info("Konfigurowanie Google ADK Agent...")
        
        # PRIORYTET: Vertex AI z Google Cloud Service Account credentials
        credentials_path = "google_cloud_credentials.json"
        if os.path.exists(credentials_path):
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path
            logger.info("✅ Ustawiono Google Application Default Credentials")
            
            # Wymuś użycie Vertex AI
            os.environ['GOOGLE_GENAI_USE_VERTEXAI'] = 'true'
            logger.info("✅ Priorytet: Używam Vertex AI z Service Account")
        
        # Ustaw projekt Google Cloud
        if not os.getenv('GOOGLE_CLOUD_PROJECT'):
            os.environ['GOOGLE_CLOUD_PROJECT'] = 'districtagent'
            logger.info("✅ Ustawiono GOOGLE_CLOUD_PROJECT na 'districtagent'")
            
        if not os.getenv('GOOGLE_CLOUD_LOCATION'):
            os.environ['GOOGLE_CLOUD_LOCATION'] = 'us-central1'
            logger.info("✅ Ustawiono GOOGLE_CLOUD_LOCATION na 'us-central1'")

        # Sprawdź Google AI Studio API jako fallback (ale nie jest potrzebny)
        api_key = os.getenv('GOOGLE_AI_API_KEY') or os.getenv('GOOGLE_API_KEY')
        if api_key and api_key != 'your_google_ai_studio_key_here':
            # Użyj Google AI API jako backup
            os.environ['GOOGLE_AI_API_KEY'] = api_key
            logger.info("✅ Google AI Studio API dostępny jako fallback")
        else:
            logger.info("📝 Google AI Studio API nie skonfigurowany - używam tylko Vertex AI")
        
        try:
            # Konfiguracja modelu Gemini dla Vertex AI
            logger.info("🔧 Konfiguracja modelu Gemini dla Vertex AI...")
            
            # POPRAWKA: Używaj wyłącznie Vertex AI z Twoimi credentials
            logger.info("🎯 Używam Vertex AI z Google Cloud Service Account")
            model = Gemini(
                model="gemini-2.0-flash-001",
                # Vertex AI wymaga project_id i location
                project_id=os.getenv('GOOGLE_CLOUD_PROJECT', 'districtagent'),
                location=os.getenv('GOOGLE_CLOUD_LOCATION', 'us-central1')
            )
            
            logger.info("✅ Model Gemini skonfigurowany dla Vertex AI")
            
            # POPRAWKA: Tworzymy prostego agenta z podstawowymi narzędziami i optymalnymi ustawieniami
            logger.info("🛠️ Tworzę agenta z podstawowymi narzędziami biznesowymi...")
            
            # Przygotuj podstawowe narzędzia biznesowe (BEZ schedule_meeting - mamy create_calendar_event)
            business_tools = [
                get_current_datetime,
                analyze_email,
                create_business_report,
                task_management,
                financial_analysis,
                analyze_and_store_email
            ]
            
            # PRZYWRACAM PEŁNE NARZĘDZIA GMAIL I CALENDAR z OAuth2! 🎉
            oauth2_credentials_file = "oauth2_credentials.json"
            if os.path.exists(oauth2_credentials_file):
                logger.info("📱 Ładowanie OAuth2 credentials...")
                with open(oauth2_credentials_file, 'r') as f:
                    oauth2_data = json.load(f)
                    # Obsługuj zarówno format "installed" jak i "web"
                    if 'installed' in oauth2_data:
                        client_id = oauth2_data['installed']['client_id']
                        client_secret = oauth2_data['installed']['client_secret']
                    elif 'web' in oauth2_data:
                        client_id = oauth2_data['web']['client_id']
                        client_secret = oauth2_data['web']['client_secret']
                    else:
                        raise ValueError("Nieprawidłowy format oauth2_credentials.json")
                    logger.info(f"✅ OAuth2 Client ID: {client_id[:20]}...")
                
                # Sprawdź czy istnieje plik z tokenami
                token_file = "token.json"
                access_token = None
                refresh_token = None
                
                if os.path.exists(token_file):
                    logger.info("🔑 Ładowanie istniejących tokenów OAuth2...")
                    with open(token_file, 'r') as f:
                        token_data = json.load(f)
                        access_token = token_data.get('token')
                        refresh_token = token_data.get('refresh_token')
                        logger.info(f"✅ Token dostępny: {access_token[:20] if access_token else 'brak'}...")
                        logger.info(f"✅ Refresh token: {'dostępny' if refresh_token else 'brak'}")
                else:
                    logger.info("⚠️ Brak pliku token.json - będzie wymagana autoryzacja")
                
                logger.info("📧 Ładowanie narzędzi Gmail...")
                gmail_tools = GmailToolset(
                    client_id=client_id,
                    client_secret=client_secret
                )
                
                # EKSPERYMENT: Skonfiguruj tokeny dla wszystkich narzędzi Gmail
                if access_token and refresh_token:
                    logger.info("🔑 Konfiguracja tokenów OAuth2 dla Gmail tools...")
                    gmail_tools_list = await gmail_tools.get_tools()
                    for tool in gmail_tools_list:
                        if hasattr(tool, 'configure_auth'):
                            # Dodaj tokeny do OAuth2Auth
                            tool.configure_auth(client_id, client_secret)
                            if hasattr(tool, '_rest_api_tool') and hasattr(tool._rest_api_tool, 'auth_credential'):
                                if tool._rest_api_tool.auth_credential and tool._rest_api_tool.auth_credential.oauth2:
                                    tool._rest_api_tool.auth_credential.oauth2.access_token = access_token
                                    tool._rest_api_tool.auth_credential.oauth2.refresh_token = refresh_token
                                    logger.info(f"✅ Skonfigurowano tokeny dla: {tool.name}")
                
                logger.info("✅ Załadowano Gmail Toolset")
                
                logger.info("📅 Ładowanie narzędzi Calendar...")
                calendar_tools = CalendarToolset(
                    client_id=client_id,
                    client_secret=client_secret
                )
                
                # EKSPERYMENT: Skonfiguruj tokeny dla wszystkich narzędzi Calendar
                if access_token and refresh_token:
                    logger.info("🔑 Konfiguracja tokenów OAuth2 dla Calendar tools...")
                    calendar_tools_list = await calendar_tools.get_tools()
                    for tool in calendar_tools_list:
                        if hasattr(tool, 'configure_auth'):
                            # Dodaj tokeny do OAuth2Auth
                            tool.configure_auth(client_id, client_secret)
                            if hasattr(tool, '_rest_api_tool') and hasattr(tool._rest_api_tool, 'auth_credential'):
                                if tool._rest_api_tool.auth_credential and tool._rest_api_tool.auth_credential.oauth2:
                                    tool._rest_api_tool.auth_credential.oauth2.access_token = access_token
                                    tool._rest_api_tool.auth_credential.oauth2.refresh_token = refresh_token
                                    logger.info(f"✅ Skonfigurowano tokeny dla: {tool.name}")
                
                logger.info("✅ Załadowano Calendar Toolset")
                
                if access_token and refresh_token:
                    logger.info("🎉 Wszystkie narzędzia skonfigurowane z istniejącymi tokenami OAuth2!")
                else:
                    logger.info("⚠️ Brak tokenów - narzędzia będą wymagać autoryzacji")
            else:
                logger.error("❌ Brak pliku oauth2_credentials.json")
                raise FileNotFoundError("Potrzebny plik oauth2_credentials.json dla Gmail i Calendar")
            
            # EKSPERYMENT: Użyj niestandardowych narzędzi Google zamiast problematycznych toolsetów
            logger.info("🔧 Próba z niestandardowymi narzędziami Google...")
            try:
                from custom_google_tools import (
                    get_calendar_events, get_gmail_messages, get_gmail_message_content, 
                    create_calendar_event, update_calendar_event, delete_calendar_event,
                    create_google_doc, get_google_doc_content, update_google_doc, list_google_docs
                )
                custom_google_tools = [
                    get_calendar_events, get_gmail_messages, get_gmail_message_content, 
                    create_calendar_event, update_calendar_event, delete_calendar_event,
                    create_google_doc, get_google_doc_content, update_google_doc, list_google_docs
                ]
                logger.info("✅ Załadowano niestandardowe narzędzia Google (w tym Google Docs)!")
                
                # Łączymy wszystkie narzędzia
                all_tools = business_tools + custom_google_tools
                logger.info("🎯 Używam niestandardowych narzędzi Google API zamiast Google ADK toolsetów")
                
            except ImportError as e:
                logger.warning(f"⚠️ Nie można załadować niestandardowych narzędzi: {e}")
                # Fallback do Google ADK toolsetów
                all_tools = business_tools + [gmail_tools, calendar_tools]
                logger.info("🔄 Używam standardowych Google ADK toolsetów jako fallback")
            
            logger.info("🎯 Agent będzie działać z OAuth2 authorization flow")
            logger.info(f"🛠️ Łącznie załadowano {len(business_tools)} podstawowych narzędzi + Gmail Toolset + Calendar Toolset")
            
            # Stwórz agenta z callbacks
            self.agent = LlmAgent(
                name="GoogleADKBusinessAgent",
                model=model,
                tools=all_tools,  # POPRAWKA: Dodano narzędzia!
                instruction="""Jesteś profesjonalnym asystentem biznesowym Google ADK. 
                
Odpowiadaj zwięźle i konkretnie. Używaj polskiego języka.
Gdy pytają o datę/czas - wykorzystaj narzędzie get_current_datetime().
Dla prostych pytań nie używaj niepotrzebnych narzędzi.

KRYTYCZNE: Gdy użytkownik prosi o "treść emaila" lub "przywołaj treść":
1. Znajdź email używając get_gmail_messages()
2. Weź message_id z pierwszego wyniku  
3. ZAWSZE wywołaj get_gmail_message_content(message_id) dla pełnej treści
4. NIE pokazuj tylko snippet - pokaż pełną treść!

WAŻNE dla Calendar API:
- Do sprawdzania wydarzeń używaj get_calendar_events() z calendar_id="primary"
- Do tworzenia wydarzeń używaj create_calendar_event()
- Do aktualizacji wydarzeń używaj update_calendar_event()
- Do usuwania wydarzeń używaj delete_calendar_event()
- "primary" oznacza główny kalendarz użytkownika

WAŻNE dla Google Docs API:
- Do tworzenia dokumentów używaj create_google_doc(title, content)
- Do czytania dokumentów używaj get_google_doc_content(document_id)
- Do aktualizacji dokumentów używaj update_google_doc(document_id, new_content, append)
- Do listy dokumentów używaj list_google_docs(max_results, search_query)
- append=True dodaje treść na końcu, append=False zastępuje całość

KRYTYCZNE - TWORZENIE WYDARZEŃ:
Gdy użytkownik chce dodać/zaplanować wydarzenie:
1. ZAWSZE najpierw sprawdź datę: get_current_datetime()
2. Stwórz wydarzenie z WSZYSTKIMI podanymi informacjami od razu
3. Format czasu ISO: "2025-06-11T15:00:00"
4. Jeśli brak godziny → domyślnie 14:00-15:00
5. Jeśli brak daty → jutro

KRYTYCZNE - ZARZĄDZANIE DUPLIKATAMI:
Gdy użytkownik chce dodać uczestników do istniejącego wydarzenia:
1. NIE twórz nowego wydarzenia!
2. Użyj update_calendar_event(event_id, attendees=[lista_emaili])
3. Pamiętaj event_id z poprzedniego create_calendar_event
4. Możesz usunąć duplikaty używając delete_calendar_event(event_id)

WAŻNE dla Gmail API:
- Do czytania emaili używaj get_gmail_messages() z user_id="me"
- Do pobierania treści konkretnego emaila używaj get_gmail_message_content(message_id)
- "me" oznacza konto aktualnego użytkownika
- Dla emaili od konkretnej osoby użyj query="from:email@domain.com"
- ZAWSZE gdy użytkownik prosi o "treść" emaila - użyj get_gmail_message_content()!
- get_gmail_messages zwraca tylko snippet (skrót) - NIE pełną treść!

KRYTYCZNE - WYŚWIETLANIE LISTY EMAILI:
Gdy otrzymasz wyniki z get_gmail_messages(), ZAWSZE wyświetl je w czytelnej formie:
1. Pokaż każdy email z numerem (1, 2, 3...)
2. Wyświetl: ID, temat, nadawcę, datę
3. Dzięki temu użytkownik może wybrać email po ID
4. Format: "1. ID: abc123 | Temat: xyz | Od: sender@email.com | Data: 2025-06-10"

Przykłady:
- "sprawdź moje spotkania na jutro" → get_calendar_events(calendar_id="primary") 
- "sprawdź moje emaile" → get_gmail_messages(user_id="me")
- "emaile od Aureliusza" → get_gmail_messages(user_id="me", query="from:aureliusz")
- "treść emaila od Aureliusza" → PIERWSZE get_gmail_messages + POTEM get_gmail_message_content(message_id)
- "przywołaj treść emaila" → get_gmail_message_content(message_id="ID_z_poprzedniego_wyszukiwania")
- "jakie mam spotkania jutro" → get_calendar_events(calendar_id="primary")
- "dodaj spotkanie z Markiem jutro o 15:00" → create_calendar_event()
- "zaplanuj prezentację na piątek" → create_calendar_event()
- "stwórz dokument o nazwie Raport" → create_google_doc(title="Raport", content="Treść...")
- "pokaż moje dokumenty" → list_google_docs(max_results=10)
- "przeczytaj dokument o ID xyz" → get_google_doc_content(document_id="xyz")
- "dodaj tekst do dokumentu xyz" → update_google_doc(document_id="xyz", new_content="tekst", append=True)""",
                description="Profesjonalny asystent biznesowy z dostępem do Gmail, Calendar i narzędzi analitycznych",
                
                # OPTYMALIZACJA: Ustawienia dla szybkości
                disallow_transfer_to_parent=True,
                disallow_transfer_to_peers=True,
                generate_content_config=types.GenerateContentConfig(
                    temperature=0.1,  # Mniej kreatywności, więcej precyzji
                    max_output_tokens=500,  # Krótsze odpowiedzi
                    candidate_count=1  # Jedna odpowiedź
                ),
                # Dodaj callbacks
                before_model_callback=business_before_model_callback,
                before_tool_callback=business_before_tool_callback, 
                after_tool_callback=business_after_tool_callback,
                after_agent_callback=business_after_agent_callback
            )
            
            logger.info(f"🛠️ Łącznie załadowano {len(all_tools)} narzędzi")
            
            # POPRAWKA: Tworzymy globalny runner zgodnie z API Google ADK
            logger.info("🔧 Tworzenie globalnego session service i runner...")
            
            # InMemoryRunner automatycznie tworzy swoje własne services!
            self.runner = InMemoryRunner(
                agent=self.agent,
                app_name="BusinessAgent"
            )
            
            # Session service jest dostępny przez runner.session_service
            self.session_service = self.runner.session_service
            
            logger.info("✅ Globalny runner i session service utworzone pomyślnie!")
            logger.info(f"📋 Session service: {type(self.session_service).__name__}")
            logger.info(f"📋 Runner: {type(self.runner).__name__}")
            
            logger.info("Google ADK Agent skonfigurowany pomyślnie!")
            
        except Exception as e:
            logger.error(f"Błąd konfiguracji agenta: {e}")
            raise
    
    async def process_message(self, message: str, websocket: WebSocketServerProtocol):
        """Przetwarzanie wiadomości przez Google ADK Agent"""
        try:
            logger.info(f"🔄 Rozpoczynam przetwarzanie wiadomości: {message}")
            
            # Sprawdź czy agent jest skonfigurowany
            if not self.agent or not self.runner or not self.session_service:
                logger.error("❌ Agent, runner lub session_service nie są skonfigurowane!")
                await websocket.send(json.dumps({
                    "type": "error",
                    "message": "Agent nie jest skonfigurowany",
                    "timestamp": datetime.now().isoformat()
                }))
                return
            
            # POPRAWKA: Utrzymuj tę samą sesję dla całego WebSocket connection
            logger.info("🚀 Uruchamiam runner.run_async() - OFICJALNY Google ADK pattern")
            
            # 1. Pobierz lub stwórz sesję dla tego WebSocket
            if websocket in self.websocket_sessions:
                # Użyj istniejącej sesji
                session_data = self.websocket_sessions[websocket]
                session_id = session_data["session_id"]
                user_id = session_data["user_id"]
                logger.info(f"🔄 Używam istniejącej sesji: {session_id}")
                
                session = await self.session_service.get_session(
                    app_name="BusinessAgent",
                    user_id=user_id,
                    session_id=session_id
                )
            else:
                # Stwórz nową sesję dla nowego WebSocket
                session_id = f"session_{int(datetime.now().timestamp())}"
                user_id = "default_user"
                
                logger.info(f"🔧 Tworzę NOWĄ sesję z ID: {session_id}")
                
                session = await self.session_service.create_session(
                    app_name="BusinessAgent",
                    user_id=user_id,
                    session_id=session_id
                )
                
                # Zapisz sesję dla tego WebSocket
                self.websocket_sessions[websocket] = {
                    "session_id": session_id,
                    "user_id": user_id
                }
                logger.info(f"💾 Zapisano sesję {session_id} dla WebSocket")
            
            logger.info(f"✅ Sesja gotowa: {session_id}")
            logger.info(f"📋 Session object: {session}")
            logger.info(f"🧠 Session state: {session.state}")
            logger.info(f"📚 Session events count: {len(session.events)}")
            
            # 2. Stwórz user message - OFICJALNY format
            user_message = types.Content(
                role='user',
                parts=[types.Part(text=message)]
            )
            
            logger.info(f"📨 Utworzona wiadomość użytkownika: {user_message}")
            
            # 3. RunConfig - używam domyślnych ustawień  
            run_config = RunConfig(
                response_modalities=["TEXT"]
            )
            
            logger.info(f"🎯 Wywołuję runner.run_async() z session_id: {session_id}")
            logger.info(f"🎯 Session object ID: {session.id if hasattr(session, 'id') else 'brak atrybutu id'}")
            
            # 4. OFICJALNY wzorzec: runner.run_async() z new_message
            collected_responses = []
            async for event in self.runner.run_async(
                user_id=user_id,
                session_id=session.id if hasattr(session, 'id') else session_id,
                new_message=user_message,
                run_config=run_config
            ):
                logger.info(f"📡 Otrzymano event: {event.author} - {type(event).__name__}")
                
                # Sprawdzamy czy to końcowa odpowiedź
                if event.is_final_response():
                    logger.info("✅ To jest końcowa odpowiedź!")
                    if event.content and event.content.parts:
                        final_text = event.content.parts[0].text
                        logger.info(f"💬 Końcowy tekst odpowiedzi: {final_text}")
                        collected_responses.append(final_text)
                
                # Również zbieramy zwykłe odpowiedzi
                elif event.content and event.content.parts:
                    event_text = event.content.parts[0].text
                    if event_text:
                        logger.info(f"📝 Tekst wydarzenia: {event_text}")
                        collected_responses.append(event_text)
            
            logger.info(f"✅ Runner zakończył pracę po {len(collected_responses)} eventach")
            
            if not collected_responses:
                collected_responses = ["Agent otrzymał wiadomość, ale nie wygenerował odpowiedzi."]
            
            # POPRAWKA: Użyj ostatnią (końcową) odpowiedź zamiast pierwszej
            final_response = collected_responses[-1] if collected_responses[-1] else "Brak odpowiedzi"
            logger.info(f"📝 Wysyłam końcową odpowiedź: {final_response[:100]}...")
            logger.info(f"🎯 Wszystkie zebrane odpowiedzi: {len(collected_responses)}")
            
            # Wyślij odpowiedź
            await websocket.send(json.dumps({
                "type": "response_chunk", 
                "content": final_response,
                "timestamp": datetime.now().isoformat()
            }))
            
            await websocket.send(json.dumps({
                "type": "response_complete",
                "timestamp": datetime.now().isoformat()
            }))
            
        except Exception as e:
            logger.error(f"❌ Błąd przetwarzania wiadomości: {e}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            
            # Prosty fallback z timestamp
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            error_response = f"Dziś jest {current_time}. Wystąpił błąd: {str(e)}"
            
            await websocket.send(json.dumps({
                "type": "response_chunk",
                "content": error_response,
                "timestamp": datetime.now().isoformat()
            }))
    
    async def handle_websocket(self, websocket: WebSocketServerProtocol):
        """Obsługa połączeń WebSocket"""
        try:
            logger.info(f"Nowe połączenie WebSocket: {websocket.remote_address}")
            self.connected_clients.add(websocket)
            
            # Wiadomość powitalna
            logger.info("Próba wysłania wiadomości powitalnej...")
            await websocket.send(json.dumps({
                "type": "welcome",
                "message": "🤖 Google ADK Business Agent gotowy do pracy!",
                "timestamp": datetime.now().isoformat()
            }))
            logger.info("✅ Wiadomość powitalna wysłana pomyślnie")
            
            # Główna pętla obsługi wiadomości
            logger.info("📨 Rozpoczynam nasłuchiwanie wiadomości...")
            async for message in websocket:
                try:
                    logger.info(f"📥 Otrzymano surową wiadomość: {message}")
                    data = json.loads(message)
                    logger.info(f"📝 Sparsowane dane: {data}")
                    
                    # Obsługa różnych formatów wiadomości
                    if data.get("type") == "message":
                        user_message = data.get("content", "")
                        logger.info(f"💬 Przetwarzam wiadomość chat (format type): {user_message}")
                        await self.process_message(user_message, websocket)
                    
                    elif data.get("message"):  # Format z nowego UI
                        user_message = data.get("message", "")
                        logger.info(f"💬 Przetwarzam wiadomość chat (format message): {user_message}")
                        await self.process_message(user_message, websocket)
                    
                    elif data.get("type") == "ping":
                        logger.info("🏓 Otrzymano ping, wysyłam pong")
                        await websocket.send(json.dumps({
                            "type": "pong",
                            "timestamp": datetime.now().isoformat()
                        }))
                    
                    else:
                        logger.warning(f"⚠️ Nieznany format wiadomości: {data}")
                        # Próbuj traktować jako zwykłą wiadomość tekstową
                        if isinstance(data, dict) and len(data) > 0:
                            # Weź pierwszą wartość string-ową jako wiadomość
                            for key, value in data.items():
                                if isinstance(value, str) and value.strip():
                                    logger.info(f"🔄 Traktuję jako wiadomość: {value}")
                                    await self.process_message(value, websocket)
                                    break
                
                except json.JSONDecodeError as e:
                    logger.error(f"❌ Błąd parsowania JSON: {e}")
                    # Traktuj jako zwykłą wiadomość tekstową
                    logger.info("📝 Traktuję jako zwykłą wiadomość tekstową")
                    await self.process_message(message, websocket)
                    
                except Exception as e:
                    logger.error(f"❌ Błąd obsługi wiadomości: {e}")
                    logger.error(f"Traceback: {traceback.format_exc()}")
                    try:
                        await websocket.send(json.dumps({
                            "type": "error",
                            "message": f"Błąd: {str(e)}",
                            "timestamp": datetime.now().isoformat()
                        }))
                    except Exception as send_error:
                        logger.error(f"Nie można wysłać komunikatu o błędzie: {send_error}")
        
        except websockets.exceptions.ConnectionClosed:
            logger.info("Połączenie WebSocket zamknięte normalnie")
        except Exception as e:
            logger.error(f"Nieoczekiwany błąd w handle_websocket: {e}")
            logger.error(f"Traceback: {traceback.format_exc()}")
        
        finally:
            self.connected_clients.discard(websocket)
            # NOWE: Usuń sesję WebSocket przy rozłączeniu
            if websocket in self.websocket_sessions:
                session_data = self.websocket_sessions[websocket]
                logger.info(f"🗑️ Usuwam sesję {session_data['session_id']} dla rozłączonego WebSocket")
                del self.websocket_sessions[websocket]
            logger.info(f"Usunięto klienta z listy: {websocket.remote_address if hasattr(websocket, 'remote_address') else 'unknown'}")
    
    async def start_server(self, host: str = "localhost", port: int = 8765):
        """Uruchomienie serwera WebSocket"""
        logger.info(f"Uruchamianie Google ADK Business Agent na {host}:{port}")
        
        # Inicjalizuj agenta jeśli jeszcze nie jest
        if not self.agent:
            await self.setup_agent()
        
        self.server = await websockets.serve(
            self.handle_websocket,
            host,
            port,
            ping_interval=20,
            ping_timeout=60
        )
        
        logger.info(f"🚀 Google ADK Business Agent działa na ws://{host}:{port}")
        logger.info("Gotowy do obsługi klientów biznesowych!")
        
        # Trzymaj serwer włączony
        await self.server.wait_closed()
    
    def stop_server(self):
        """Zatrzymanie serwera"""
        if self.server:
            self.server.close()
            logger.info("Serwer zatrzymany")

async def main():
    """Główna funkcja uruchamiająca"""
    # Sprawdź dostęp do Google Cloud
    credentials_path = "google_cloud_credentials.json"
    if not os.path.exists(credentials_path):
        logger.error("Brak pliku google_cloud_credentials.json!")
        return
    
    # Ustaw zmienną środowiskową dla Google Cloud
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path
    logger.info("✅ Używam Google Cloud Service Account credentials")
    
    # Utwórz i uruchom agenta
    agent = GoogleADKBusinessAgent()
    
    try:
        await agent.start_server()
    except KeyboardInterrupt:
        logger.info("Otrzymano sygnał przerwania...")
        agent.stop_server()
    except Exception as e:
        logger.error(f"Błąd serwera: {e}")
        agent.stop_server()

if __name__ == "__main__":
    print("""
    🤖 Google ADK Business Agent z Gmail
    ====================================
    
    Funkcje:
    • 📅 Google Calendar - zarządzanie spotkaniami
    • 📧 Gmail - czytanie, wysyłanie, analiza emaili  
    • 📊 Raporty biznesowe i analizy
    • ✅ Zarządzanie zadaniami i projektami
    • 💰 Analiza finansowa i KPI
    • 🔍 Wyszukiwanie informacji Google
    
    🔗 Połącz się przez WebSocket: ws://localhost:8765
    """)
    
    asyncio.run(main()) 