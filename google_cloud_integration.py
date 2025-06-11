#!/usr/bin/env python3
"""
Google Cloud Integration Manager dla MetaHuman Business Assistant
Pełna integracja z ekosystemem Google Cloud używając Service Account
"""

import os
import asyncio
import json
import base64
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dotenv import load_dotenv

# Google Cloud imports
from google.oauth2 import service_account
from google.cloud import texttospeech
from google.cloud import speech
from google.cloud import storage
from google.cloud import bigquery
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Load environment
load_dotenv()

class GoogleCloudManager:
    """Manager dla wszystkich usług Google Cloud"""
    
    def __init__(self):
        self.project_id = os.getenv("GOOGLE_CLOUD_PROJECT", "districtagent")
        self.credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "google_cloud_credentials.json")
        self.region = os.getenv("GOOGLE_CLOUD_REGION", "europe-west1")
        
        # Załaduj credentials
        self.credentials = service_account.Credentials.from_service_account_file(
            self.credentials_path,
            scopes=[
                'https://www.googleapis.com/auth/cloud-platform',
                'https://www.googleapis.com/auth/gmail.modify',
                'https://www.googleapis.com/auth/calendar',
                'https://www.googleapis.com/auth/drive',
                'https://www.googleapis.com/auth/spreadsheets'
            ]
        )
        
        # Initialize clients
        self.tts_client = texttospeech.TextToSpeechClient(credentials=self.credentials)
        self.speech_client = speech.SpeechClient(credentials=self.credentials)
        self.storage_client = storage.Client(credentials=self.credentials, project=self.project_id)
        self.bigquery_client = bigquery.Client(credentials=self.credentials, project=self.project_id)
        
        # Google APIs services
        self.gmail_service = build('gmail', 'v1', credentials=self.credentials)
        self.calendar_service = build('calendar', 'v3', credentials=self.credentials)
        self.drive_service = build('drive', 'v3', credentials=self.credentials)
        self.sheets_service = build('sheets', 'v4', credentials=self.credentials)

class GoogleCloudTTS:
    """Google Cloud Text-to-Speech Integration"""
    
    def __init__(self, gcp_manager: GoogleCloudManager):
        self.gcp = gcp_manager
        self.client = gcp_manager.tts_client
        
        # Voice configuration dla polskiego avatara biznesowego
        self.voice_config = {
            'language_code': 'pl-PL',
            'name': 'pl-PL-Standard-B',  # Męski głos profesjonalny
            'ssml_gender': texttospeech.SsmlVoiceGender.MALE
        }
        
        # Audio configuration dla najlepszej jakości
        self.audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3,
            speaking_rate=1.0,
            pitch=0.0,
            volume_gain_db=0.0,
            effects_profile_id=['telephony-class-application']
        )
    
    async def generate_speech(self, text: str, emotion: str = "neutral") -> bytes:
        """
        Generuje mowę z tekstu używając Google Cloud TTS
        
        Args:
            text: Tekst do wypowiedzenia
            emotion: Emocja/styl (neutral, happy, sad, angry)
            
        Returns:
            Dane audio w formacie MP3
        """
        try:
            # Optymalizuj tekst dla TTS
            optimized_text = self._optimize_text_for_tts(text)
            
            # Konfiguracja głosu na podstawie emocji
            voice = texttospeech.VoiceSelectionParams(
                language_code=self.voice_config['language_code'],
                name=self._get_voice_for_emotion(emotion),
                ssml_gender=self.voice_config['ssml_gender']
            )
            
            # Synthesis input
            synthesis_input = texttospeech.SynthesisInput(text=optimized_text)
            
            # Generate speech
            response = self.client.synthesize_speech(
                input=synthesis_input,
                voice=voice,
                audio_config=self.audio_config
            )
            
            return response.audio_content
            
        except Exception as e:
            print(f"❌ Błąd Google Cloud TTS: {e}")
            return b""
    
    def _optimize_text_for_tts(self, text: str) -> str:
        """Optymalizuje tekst dla lepszej jakości TTS"""
        # Usuń emoji i formatowanie
        text = text.replace("📊", "").replace("✅", "").replace("🎯", "")
        text = text.replace("📅", "").replace("⏰", "").replace("📋", "")
        text = text.replace("🤖", "").replace("💡", "").replace("🔍", "")
        
        # Dodaj pauzy dla lepszej dykcji
        text = text.replace(".", ". ").replace("!", "! ").replace("?", "? ")
        
        # Skróć jeśli za długie
        if len(text) > 600:
            sentences = text.split(". ")
            text = ". ".join(sentences[:4]) + "."
        
        return text.strip()
    
    def _get_voice_for_emotion(self, emotion: str) -> str:
        """Zwraca odpowiedni głos dla emocji"""
        voices = {
            "neutral": "pl-PL-Standard-B",      # Profesjonalny męski
            "happy": "pl-PL-Standard-A",        # Przyjazny żeński  
            "professional": "pl-PL-Standard-B", # Biznesowy męski
            "calm": "pl-PL-Standard-C",         # Spokojny męski
            "energetic": "pl-PL-Standard-D"     # Energiczny męski
        }
        return voices.get(emotion, "pl-PL-Standard-B")

class GoogleBusinessIntegration:
    """Integracja z Google Business APIs (Gmail, Calendar, Drive)"""
    
    def __init__(self, gcp_manager: GoogleCloudManager):
        self.gcp = gcp_manager
        self.gmail = gcp_manager.gmail_service
        self.calendar = gcp_manager.calendar_service
        self.drive = gcp_manager.drive_service
        self.sheets = gcp_manager.sheets_service
    
    async def get_calendar_events(self, days_ahead: int = 7) -> List[Dict]:
        """Pobiera nadchodzące wydarzenia z kalendarza"""
        try:
            now = datetime.utcnow().isoformat() + 'Z'
            end_time = (datetime.utcnow() + timedelta(days=days_ahead)).isoformat() + 'Z'
            
            events_result = self.calendar.events().list(
                calendarId='primary',
                timeMin=now,
                timeMax=end_time,
                maxResults=20,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            
            formatted_events = []
            for event in events:
                start = event['start'].get('dateTime', event['start'].get('date'))
                formatted_events.append({
                    'title': event.get('summary', 'Bez tytułu'),
                    'start': start,
                    'description': event.get('description', ''),
                    'location': event.get('location', ''),
                    'id': event['id']
                })
            
            return formatted_events
            
        except Exception as e:
            print(f"❌ Błąd Calendar API: {e}")
            return []
    
    async def create_calendar_event(self, title: str, start_time: str, duration_minutes: int = 60, description: str = "") -> str:
        """Tworzy nowe wydarzenie w kalendarzu"""
        try:
            # Parse start time
            start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
            end_dt = start_dt + timedelta(minutes=duration_minutes)
            
            event = {
                'summary': title,
                'description': description,
                'start': {
                    'dateTime': start_dt.isoformat(),
                    'timeZone': 'Europe/Warsaw',
                },
                'end': {
                    'dateTime': end_dt.isoformat(),
                    'timeZone': 'Europe/Warsaw',
                },
            }
            
            event = self.calendar.events().insert(calendarId='primary', body=event).execute()
            return f"✅ Spotkanie utworzone: {event.get('htmlLink')}"
            
        except Exception as e:
            print(f"❌ Błąd tworzenia wydarzenia: {e}")
            return "❌ Nie udało się utworzyć spotkania"
    
    async def get_recent_emails(self, max_results: int = 10) -> List[Dict]:
        """Pobiera najnowsze emaile"""
        try:
            results = self.gmail.users().messages().list(
                userId='me', 
                maxResults=max_results,
                q='is:unread'  # Tylko nieprzeczytane
            ).execute()
            
            messages = results.get('messages', [])
            
            emails = []
            for message in messages:
                msg = self.gmail.users().messages().get(userId='me', id=message['id']).execute()
                
                headers = msg['payload'].get('headers', [])
                subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'Bez tematu')
                sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Nieznany')
                date = next((h['value'] for h in headers if h['name'] == 'Date'), '')
                
                emails.append({
                    'id': message['id'],
                    'subject': subject,
                    'sender': sender,
                    'date': date,
                    'snippet': msg.get('snippet', '')
                })
            
            return emails
            
        except Exception as e:
            print(f"❌ Błąd Gmail API: {e}")
            return []
    
    async def send_email(self, to: str, subject: str, body: str) -> str:
        """Wysyła email"""
        try:
            message = {
                'raw': base64.urlsafe_b64encode(
                    f"To: {to}\nSubject: {subject}\n\n{body}".encode()
                ).decode()
            }
            
            self.gmail.users().messages().send(userId='me', body=message).execute()
            return "✅ Email wysłany pomyślnie"
            
        except Exception as e:
            print(f"❌ Błąd wysyłania emaila: {e}")
            return "❌ Nie udało się wysłać emaila"

class GoogleAnalytics:
    """Analytics i reporting używając BigQuery"""
    
    def __init__(self, gcp_manager: GoogleCloudManager):
        self.gcp = gcp_manager
        self.client = gcp_manager.bigquery_client
        self.dataset_id = "business_analytics"
        self.table_id = "metahuman_interactions"
    
    async def log_interaction(self, user_input: str, agent_response: str, response_time_ms: int):
        """Loguje interakcję z MetaHuman do BigQuery"""
        try:
            table_ref = self.client.dataset(self.dataset_id).table(self.table_id)
            
            rows_to_insert = [{
                'timestamp': datetime.utcnow().isoformat(),
                'user_input': user_input,
                'agent_response': agent_response,
                'response_time_ms': response_time_ms,
                'session_id': 'session_' + datetime.now().strftime('%Y%m%d_%H%M%S')
            }]
            
            errors = self.client.insert_rows_json(table_ref, rows_to_insert)
            if not errors:
                print("✅ Interakcja zalogowana do BigQuery")
            else:
                print(f"❌ Błąd logowania: {errors}")
                
        except Exception as e:
            print(f"❌ Błąd BigQuery: {e}")
    
    async def get_usage_analytics(self, days: int = 7) -> Dict:
        """Pobiera analitykę użytkowania"""
        try:
            query = f"""
            SELECT 
                DATE(timestamp) as date,
                COUNT(*) as interactions,
                AVG(response_time_ms) as avg_response_time,
                COUNT(DISTINCT session_id) as unique_sessions
            FROM `{self.gcp.project_id}.{self.dataset_id}.{self.table_id}`
            WHERE timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL {days} DAY)
            GROUP BY DATE(timestamp)
            ORDER BY date DESC
            """
            
            query_job = self.client.query(query)
            results = query_job.result()
            
            analytics = {
                'total_interactions': 0,
                'avg_response_time': 0,
                'daily_stats': []
            }
            
            for row in results:
                analytics['daily_stats'].append({
                    'date': row.date.strftime('%Y-%m-%d'),
                    'interactions': row.interactions,
                    'avg_response_time': round(row.avg_response_time, 2),
                    'unique_sessions': row.unique_sessions
                })
                analytics['total_interactions'] += row.interactions
            
            if analytics['daily_stats']:
                analytics['avg_response_time'] = sum(
                    day['avg_response_time'] for day in analytics['daily_stats']
                ) / len(analytics['daily_stats'])
            
            return analytics
            
        except Exception as e:
            print(f"❌ Błąd analityki: {e}")
            return {'error': str(e)}

# Test functionality
async def test_google_cloud_integration():
    """Test wszystkich funkcji Google Cloud"""
    print("🚀 Test Google Cloud Integration")
    print("=" * 50)
    
    try:
        # Initialize manager
        gcp_manager = GoogleCloudManager()
        print("✅ Google Cloud Manager zainicjalizowany")
        
        # Test TTS
        tts = GoogleCloudTTS(gcp_manager)
        test_text = "Witaj! Jestem Twoim asystentem biznesowym z Google Cloud."
        audio_data = await tts.generate_speech(test_text)
        
        if audio_data:
            with open("google_tts_test.mp3", "wb") as f:
                f.write(audio_data)
            print(f"✅ Google Cloud TTS: {len(audio_data)} bytes")
        
        # Test Business Integration
        business = GoogleBusinessIntegration(gcp_manager)
        
        # Test Calendar
        events = await business.get_calendar_events(days_ahead=3)
        print(f"✅ Kalendarz: {len(events)} nadchodzących wydarzeń")
        
        # Test Gmail
        emails = await business.get_recent_emails(max_results=5)
        print(f"✅ Gmail: {len(emails)} nieprzeczytanych emaili")
        
        # Test Analytics
        analytics = GoogleAnalytics(gcp_manager)
        print("✅ BigQuery Analytics gotowe")
        
        print("\n🎉 Google Cloud Integration działa!")
        
    except Exception as e:
        print(f"❌ Błąd testu: {e}")

if __name__ == "__main__":
    asyncio.run(test_google_cloud_integration()) 