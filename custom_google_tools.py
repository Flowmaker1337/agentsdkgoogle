#!/usr/bin/env python3
"""
Niestandardowe narzędzia Google Calendar i Gmail 
używające bezpośrednio Google APIs z tokenami OAuth2
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import base64

class CustomGoogleTools:
    """Niestandardowe narzędzia Google z tokenami OAuth2"""
    
    def __init__(self, token_file: str = "token.json", credentials_file: str = "oauth2_credentials.json"):
        self.token_file = token_file
        self.credentials_file = credentials_file
        self.credentials = None
        self.calendar_service = None
        self.gmail_service = None
        self.docs_service = None
        self.drive_service = None
        self._setup_credentials()
    
    def _setup_credentials(self):
        """Konfiguracja credentials z plików OAuth2"""
        try:
            # Ładuj tokeny z token.json
            if os.path.exists(self.token_file):
                with open(self.token_file, 'r') as f:
                    token_data = json.load(f)
                
                # Stwórz Credentials object
                self.credentials = Credentials(
                    token=token_data.get('token'),
                    refresh_token=token_data.get('refresh_token'),
                    token_uri=token_data.get('token_uri'),
                    client_id=token_data.get('client_id'),
                    client_secret=token_data.get('client_secret'),
                    scopes=token_data.get('scopes', [])
                )
                
                # Odśwież token jeśli potrzeba
                if self.credentials.expired:
                    self.credentials.refresh(Request())
                    # Zapisz odświeżony token
                    self._save_token()
                
                # Inicjalizuj usługi Google APIs
                self.calendar_service = build('calendar', 'v3', credentials=self.credentials)
                self.gmail_service = build('gmail', 'v1', credentials=self.credentials)
                self.docs_service = build('docs', 'v1', credentials=self.credentials)
                self.drive_service = build('drive', 'v3', credentials=self.credentials)
                
                print(f"✅ Google APIs skonfigurowane z tokenami OAuth2")
                
            else:
                raise FileNotFoundError(f"Brak pliku {self.token_file}")
                
        except Exception as e:
            print(f"❌ Błąd konfiguracji Google APIs: {e}")
            raise
    
    def _save_token(self):
        """Zapisz odświeżony token do pliku"""
        try:
            token_data = {
                'token': self.credentials.token,
                'refresh_token': self.credentials.refresh_token,
                'token_uri': self.credentials.token_uri,
                'client_id': self.credentials.client_id,
                'client_secret': self.credentials.client_secret,
                'scopes': self.credentials.scopes,
                'universe_domain': 'googleapis.com',
                'account': '',
                'expiry': self.credentials.expiry.isoformat() if self.credentials.expiry else None
            }
            
            with open(self.token_file, 'w') as f:
                json.dump(token_data, f)
                
        except Exception as e:
            print(f"⚠️ Nie można zapisać odświeżonego tokena: {e}")

async def get_calendar_events(
    calendar_id: str = "primary",
    time_min: Optional[str] = None,
    time_max: Optional[str] = None,
    max_results: int = 10
) -> Dict[str, Any]:
    """
    Pobiera wydarzenia z Google Calendar
    
    Args:
        calendar_id: ID kalendarza (domyślnie "primary")
        time_min: Początek zakresu czasu (RFC3339)
        time_max: Koniec zakresu czasu (RFC3339)
        max_results: Maksymalna liczba wyników
    """
    try:
        tools = CustomGoogleTools()
        
        if not time_min:
            # Domyślnie: od teraz
            time_min = datetime.utcnow().isoformat() + 'Z'
        
        if not time_max:
            # Domyślnie: do końca jutrzejszego dnia
            tomorrow_end = datetime.utcnow().replace(hour=23, minute=59, second=59) + timedelta(days=1)
            time_max = tomorrow_end.isoformat() + 'Z'
        
        print(f"📅 Pobieranie wydarzeń kalendarza {calendar_id} od {time_min} do {time_max}")
        
        events_result = tools.calendar_service.events().list(
            calendarId=calendar_id,
            timeMin=time_min,
            timeMax=time_max,
            maxResults=max_results,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        events = events_result.get('items', [])
        
        formatted_events = []
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            end = event['end'].get('dateTime', event['end'].get('date'))
            
            formatted_events.append({
                'id': event.get('id'),
                'summary': event.get('summary', 'Bez tytułu'),
                'start': start,
                'end': end,
                'description': event.get('description', ''),
                'location': event.get('location', ''),
                'attendees': [att.get('email') for att in event.get('attendees', [])]
            })
        
        return {
            'success': True,
            'events_count': len(formatted_events),
            'events': formatted_events,
            'calendar_id': calendar_id,
            'time_range': f"{time_min} do {time_max}"
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'message': f"Błąd pobierania wydarzeń kalendarza: {e}"
        }

async def get_gmail_messages(
    user_id: str = "me",
    query: str = "",
    max_results: int = 10
) -> Dict[str, Any]:
    """
    Pobiera wiadomości z Gmail
    
    Args:
        user_id: ID użytkownika (domyślnie "me")
        query: Zapytanie Gmail (np. "is:unread", "from:example@gmail.com", "subject:test")
        max_results: Maksymalna liczba wyników
        
    Przykłady query:
    - "from:aureliusz.gorski@example.com" - emaile od konkretnej osoby
    - "is:unread" - nieprzeczytane emaile
    - "subject:spotkanie" - emaile z określonym tematem
    - "" - wszystkie najnowsze emaile
    """
    try:
        tools = CustomGoogleTools()
        
        print(f"📧 Pobieranie wiadomości Gmail dla {user_id}, query: '{query}'")
        
        # Pobierz listę wiadomości
        messages_result = tools.gmail_service.users().messages().list(
            userId=user_id,
            q=query,
            maxResults=max_results
        ).execute()
        
        messages = messages_result.get('messages', [])
        
        formatted_messages = []
        for msg in messages:
            # Pobierz szczegóły każdej wiadomości
            message = tools.gmail_service.users().messages().get(
                userId=user_id,
                id=msg['id']
            ).execute()
            
            # Wyciągnij nagłówki
            headers = message['payload'].get('headers', [])
            subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'Bez tematu')
            sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Nieznany nadawca')
            date = next((h['value'] for h in headers if h['name'] == 'Date'), '')
            
            formatted_messages.append({
                'id': message['id'],
                'subject': subject,
                'sender': sender,
                'date': date,
                'snippet': message.get('snippet', ''),
                'labels': message.get('labelIds', [])
            })
        
        return {
            'success': True,
            'messages_count': len(formatted_messages),
            'messages': formatted_messages,
            'user_id': user_id,
            'query': query
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'message': f"Błąd pobierania wiadomości Gmail: {e}"
        }

async def get_gmail_message_content(
    message_id: str,
    user_id: str = "me"
) -> Dict[str, Any]:
    """
    Pobiera pełną treść konkretnej wiadomości Gmail
    
    Args:
        message_id: ID konkretnej wiadomości Gmail
        user_id: ID użytkownika (domyślnie "me")
    """
    try:
        tools = CustomGoogleTools()
        
        print(f"📧 Pobieranie treści wiadomości {message_id} dla {user_id}")
        
        # Pobierz szczegóły wiadomości
        message = tools.gmail_service.users().messages().get(
            userId=user_id,
            id=message_id,
            format='full'
        ).execute()
        
        # Wyciągnij nagłówki
        headers = message['payload'].get('headers', [])
        subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'Bez tematu')
        sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Nieznany nadawca')
        date = next((h['value'] for h in headers if h['name'] == 'Date'), '')
        to = next((h['value'] for h in headers if h['name'] == 'To'), '')
        
        # Wyciągnij treść wiadomości
        body = ""
        if 'parts' in message['payload']:
            # Wiadomość ma części (załączniki, HTML, tekst)
            for part in message['payload']['parts']:
                if part['mimeType'] == 'text/plain':
                    if 'data' in part['body']:
                        body_data = part['body']['data']
                        body = base64.urlsafe_b64decode(body_data).decode('utf-8')
                        break
        else:
            # Prosta wiadomość tekstowa
            if message['payload']['body'].get('data'):
                body_data = message['payload']['body']['data']
                body = base64.urlsafe_b64decode(body_data).decode('utf-8')
        
        if not body:
            body = message.get('snippet', 'Nie można pobrać treści wiadomości')
        
        return {
            'success': True,
            'message_id': message_id,
            'subject': subject,
            'sender': sender,
            'to': to,
            'date': date,
            'body': body,
            'snippet': message.get('snippet', ''),
            'labels': message.get('labelIds', [])
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'message': f"Błąd pobierania treści wiadomości: {e}"
        }

async def create_calendar_event(
    title: str,
    start_time: str,
    end_time: str,
    description: str = "",
    location: str = "",
    attendees: Optional[List[str]] = None,
    calendar_id: str = "primary"
) -> Dict[str, Any]:
    """
    Tworzy nowe wydarzenie w Google Calendar
    
    Args:
        title: Tytuł wydarzenia
        start_time: Czas rozpoczęcia (ISO format)
        end_time: Czas zakończenia (ISO format) 
        description: Opis wydarzenia
        location: Lokalizacja
        attendees: Lista emaili uczestników
        calendar_id: ID kalendarza
    """
    try:
        tools = CustomGoogleTools()
        
        if attendees is None:
            attendees = []
        
        event = {
            'summary': title,
            'description': description,
            'location': location,
            'start': {
                'dateTime': start_time,
                'timeZone': 'Europe/Warsaw',
            },
            'end': {
                'dateTime': end_time,
                'timeZone': 'Europe/Warsaw',
            },
            'attendees': [{'email': email} for email in attendees],
            'reminders': {
                'useDefault': True,
            },
            # Automatyczne tworzenie Google Meet
            'conferenceData': {
                'createRequest': {
                    'requestId': f"meet-{title[:20]}-{start_time[:10]}",  # Unikalny ID
                    'conferenceSolutionKey': {
                        'type': 'hangoutsMeet'
                    }
                }
            },
        }
        
        print(f"📅 Tworzenie wydarzenia: {title} w kalendarzu {calendar_id}")
        
        # Dodaj timeout żeby uniknąć zawieszenia
        import socket
        socket.setdefaulttimeout(30)  # 30 sekund timeout
        
        created_event = tools.calendar_service.events().insert(
            calendarId=calendar_id,
            body=event,
            conferenceDataVersion=1  # Wymagane dla conferenceData
        ).execute()
        
        # Pobierz informacje o Google Meet
        conference_data = created_event.get('conferenceData', {})
        meet_link = None
        if 'entryPoints' in conference_data:
            for entry in conference_data['entryPoints']:
                if entry.get('entryPointType') == 'video':
                    meet_link = entry.get('uri')
                    break
        
        return {
            'success': True,
            'event_id': created_event.get('id'),
            'event_link': created_event.get('htmlLink'),
            'meet_link': meet_link,
            'title': title,
            'start_time': start_time,
            'end_time': end_time,
            'message': f'Wydarzenie "{title}" zostało utworzone z automatycznym linkiem Google Meet'
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'message': f"Błąd tworzenia wydarzenia: {e}"
        }

async def update_calendar_event(
    event_id: str,
    title: Optional[str] = None,
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
    description: Optional[str] = None,
    location: Optional[str] = None,
    attendees: Optional[List[str]] = None,
    calendar_id: str = "primary"
) -> Dict[str, Any]:
    """
    Aktualizuje istniejące wydarzenie w Google Calendar
    
    Args:
        event_id: ID wydarzenia do aktualizacji
        title: Nowy tytuł wydarzenia (opcjonalny)
        start_time: Nowy czas rozpoczęcia (opcjonalny)
        end_time: Nowy czas zakończenia (opcjonalny)
        description: Nowy opis (opcjonalny)
        location: Nowa lokalizacja (opcjonalna)
        attendees: Nowa lista uczestników (opcjonalna)
        calendar_id: ID kalendarza
    """
    try:
        tools = CustomGoogleTools()
        
        # Pobierz istniejące wydarzenie
        existing_event = tools.calendar_service.events().get(
            calendarId=calendar_id,
            eventId=event_id
        ).execute()
        
        print(f"📅 Aktualizowanie wydarzenia: {event_id}")
        
        # Aktualizuj tylko te pola które zostały podane
        if title is not None:
            existing_event['summary'] = title
        if description is not None:
            existing_event['description'] = description
        if location is not None:
            existing_event['location'] = location
        if start_time is not None:
            existing_event['start'] = {
                'dateTime': start_time,
                'timeZone': 'Europe/Warsaw',
            }
        if end_time is not None:
            existing_event['end'] = {
                'dateTime': end_time,
                'timeZone': 'Europe/Warsaw',
            }
        if attendees is not None:
            existing_event['attendees'] = [{'email': email} for email in attendees]
        
        # Dodaj timeout żeby uniknąć zawieszenia
        import socket
        socket.setdefaulttimeout(30)  # 30 sekund timeout
        
        updated_event = tools.calendar_service.events().update(
            calendarId=calendar_id,
            eventId=event_id,
            body=existing_event
        ).execute()
        
        return {
            'success': True,
            'event_id': updated_event.get('id'),
            'event_link': updated_event.get('htmlLink'),
            'title': updated_event.get('summary'),
            'updated': True
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'message': f"Błąd aktualizacji wydarzenia: {e}"
        }

async def delete_calendar_event(
    event_id: str,
    calendar_id: str = "primary"
) -> Dict[str, Any]:
    """
    Usuwa wydarzenie z Google Calendar
    
    Args:
        event_id: ID wydarzenia do usunięcia
        calendar_id: ID kalendarza
    """
    try:
        tools = CustomGoogleTools()
        
        print(f"🗑️ Usuwanie wydarzenia: {event_id}")
        
        # Dodaj timeout żeby uniknąć zawieszenia
        import socket
        socket.setdefaulttimeout(30)
        
        tools.calendar_service.events().delete(
            calendarId=calendar_id,
            eventId=event_id
        ).execute()
        
        return {
            'success': True,
            'event_id': event_id,
            'deleted': True,
            'message': f'Wydarzenie {event_id} zostało usunięte'
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'message': f"Błąd usuwania wydarzenia: {e}"
        }

# Google Docs API functions
async def create_google_doc(
    title: str,
    content: str = "",
    folder_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Tworzy nowy dokument Google Docs
    
    Args:
        title: Tytuł dokumentu
        content: Początkowa zawartość dokumentu (opcjonalna)
        folder_id: ID folderu gdzie utworzyć dokument (opcjonalne)
    """
    try:
        tools = CustomGoogleTools()
        
        print(f"📄 Tworzenie dokumentu Google Docs: {title}")
        
        # Dodaj timeout żeby uniknąć zawieszenia
        import socket
        socket.setdefaulttimeout(30)
        
        # Stwórz dokument
        doc_metadata = {
            'title': title
        }
        
        # Jeśli określono folder, ustaw go jako rodzica
        if folder_id:
            doc_metadata['parents'] = [folder_id]
        
        doc = tools.docs_service.documents().create(body={
            'title': title
        }).execute()
        
        doc_id = doc.get('documentId')
        
        # Jeśli podano content, dodaj go do dokumentu
        if content:
            requests = [
                {
                    'insertText': {
                        'location': {
                            'index': 1,
                        },
                        'text': content
                    }
                }
            ]
            
            tools.docs_service.documents().batchUpdate(
                documentId=doc_id,
                body={'requests': requests}
            ).execute()
        
        # Przenieś do odpowiedniego folderu w Drive jeśli podano
        if folder_id and hasattr(tools, 'drive_service'):
            try:
                tools.drive_service.files().update(
                    fileId=doc_id,
                    addParents=folder_id,
                    fields='id, parents'
                ).execute()
            except Exception as e:
                print(f"⚠️ Nie można przenieść do folderu: {e}")
        
        return {
            'success': True,
            'document_id': doc_id,
            'title': title,
            'url': f'https://docs.google.com/document/d/{doc_id}/edit',
            'content_added': bool(content),
            'message': f'Dokument "{title}" został utworzony pomyślnie'
        }
        
    except Exception as e:
        print(f"❌ Błąd tworzenia dokumentu: {e}")
        return {
            'success': False,
            'error': str(e),
            'message': f'Nie można utworzyć dokumentu: {e}'
        }

async def get_google_doc_content(
    document_id: str
) -> Dict[str, Any]:
    """
    Pobiera treść dokumentu Google Docs
    
    Args:
        document_id: ID dokumentu Google Docs
    """
    try:
        tools = CustomGoogleTools()
        
        print(f"📄 Pobieranie treści dokumentu: {document_id}")
        
        # Dodaj timeout żeby uniknąć zawieszenia
        import socket
        socket.setdefaulttimeout(30)
        
        # Pobierz dokument
        document = tools.docs_service.documents().get(documentId=document_id).execute()
        
        title = document.get('title', 'Bez tytułu')
        
        # Ekstraktuj tekst z dokumentu
        content = ''
        body = document.get('body', {})
        
        if 'content' in body:
            for element in body['content']:
                if 'paragraph' in element:
                    paragraph = element['paragraph']
                    if 'elements' in paragraph:
                        for elem in paragraph['elements']:
                            if 'textRun' in elem:
                                content += elem['textRun'].get('content', '')
        
        return {
            'success': True,
            'document_id': document_id,
            'title': title,
            'content': content,
            'url': f'https://docs.google.com/document/d/{document_id}/edit',
            'word_count': len(content.split()),
            'character_count': len(content),
            'message': f'Treść dokumentu "{title}" została pobrana pomyślnie'
        }
        
    except Exception as e:
        print(f"❌ Błąd pobierania dokumentu: {e}")
        return {
            'success': False,
            'error': str(e),
            'message': f'Nie można pobrać dokumentu: {e}'
        }

async def update_google_doc(
    document_id: str,
    new_content: str,
    append: bool = True
) -> Dict[str, Any]:
    """
    Aktualizuje treść dokumentu Google Docs
    
    Args:
        document_id: ID dokumentu Google Docs
        new_content: Nowa treść do dodania/zastąpienia
        append: Czy dodać treść na końcu (True) czy zastąpić całość (False)
    """
    try:
        tools = CustomGoogleTools()
        
        print(f"📄 Aktualizacja dokumentu: {document_id}")
        
        # Dodaj timeout żeby uniknąć zawieszenia
        import socket
        socket.setdefaulttimeout(30)
        
        requests = []
        
        if append:
            # Dodaj treść na końcu dokumentu
            requests.append({
                'insertText': {
                    'location': {
                        'index': 1,  # Na początku - Google Docs API dodaje na końcu automatycznie
                    },
                    'text': f'\n{new_content}'
                }
            })
        else:
            # Zastąp całą treść
            # Najpierw pobierz dokument żeby znać długość
            document = tools.docs_service.documents().get(documentId=document_id).execute()
            
            # Znajdź koniec dokumentu
            body = document.get('body', {})
            end_index = body.get('content', [{}])[-1].get('endIndex', 1)
            
            # Usuń starą treść
            requests.append({
                'deleteContentRange': {
                    'range': {
                        'startIndex': 1,
                        'endIndex': end_index - 1
                    }
                }
            })
            
            # Wstaw nową treść
            requests.append({
                'insertText': {
                    'location': {
                        'index': 1,
                    },
                    'text': new_content
                }
            })
        
        # Wykonaj aktualizację
        result = tools.docs_service.documents().batchUpdate(
            documentId=document_id,
            body={'requests': requests}
        ).execute()
        
        return {
            'success': True,
            'document_id': document_id,
            'url': f'https://docs.google.com/document/d/{document_id}/edit',
            'action': 'append' if append else 'replace',
            'content_length': len(new_content),
            'replies': result.get('replies', []),
            'message': f'Dokument został {"uzupełniony" if append else "zastąpiony"} pomyślnie'
        }
        
    except Exception as e:
        print(f"❌ Błąd aktualizacji dokumentu: {e}")
        return {
            'success': False,
            'error': str(e),
            'message': f'Nie można zaktualizować dokumentu: {e}'
        }

async def list_google_docs(
    max_results: int = 10,
    search_query: str = ""
) -> Dict[str, Any]:
    """
    Lista dokumentów Google Docs
    
    Args:
        max_results: Maksymalna liczba dokumentów do zwrócenia
        search_query: Zapytanie wyszukiwania (opcjonalne)
    """
    try:
        tools = CustomGoogleTools()
        
        print(f"📄 Pobieranie listy dokumentów Google Docs...")
        
        # Dodaj timeout żeby uniknąć zawieszenia
        import socket
        socket.setdefaulttimeout(30)
        
        # Konstruuj zapytanie
        query = "mimeType='application/vnd.google-apps.document'"
        if search_query:
            query += f" and name contains '{search_query}'"
        
        # Pobierz listę dokumentów przez Drive API v3
        results = tools.drive_service.files().list(
            q=query,
            pageSize=max_results,
            fields='files(id,name,modifiedTime,owners)',
            orderBy='modifiedTime desc'
        ).execute()
        
        documents = results.get('files', [])
        
        # Formatuj wyniki
        formatted_docs = []
        for doc in documents:
            doc_info = {
                'id': doc.get('id'),
                'title': doc.get('name', 'Bez tytułu'),  # API v3 używa 'name' zamiast 'title'
                'url': f"https://docs.google.com/document/d/{doc.get('id')}/edit",
                'modified_date': doc.get('modifiedTime'),  # API v3 używa 'modifiedTime' zamiast 'modifiedDate'
                'owners': [owner.get('displayName', 'Nieznany') for owner in doc.get('owners', [])]
            }
            formatted_docs.append(doc_info)
        
        return {
            'success': True,
            'documents': formatted_docs,
            'count': len(formatted_docs),
            'search_query': search_query or 'wszystkie dokumenty',
            'message': f'Znaleziono {len(formatted_docs)} dokumentów Google Docs'
        }
        
    except Exception as e:
        print(f"❌ Błąd pobierania listy dokumentów: {e}")
        return {
            'success': False,
            'error': str(e),
            'message': f'Nie można pobrać listy dokumentów: {e}'
        }

async def list_drawio_files(
    max_results: int = 10,
    search_query: str = ""
) -> Dict[str, Any]:
    """
    Lista plików draw.io z Google Drive
    
    Args:
        max_results: Maksymalna liczba plików do zwrócenia
        search_query: Zapytanie wyszukiwania w nazwie pliku (opcjonalne)
    """
    try:
        tools = CustomGoogleTools()
        
        print(f"🎨 Pobieranie listy plików draw.io z Google Drive...")
        
        # Dodaj timeout żeby uniknąć zawieszenia
        import socket
        socket.setdefaulttimeout(30)
        
        # Konstruuj zapytanie dla plików draw.io
        # Pliki draw.io mogą mieć różne MIME types
        drawio_queries = [
            "mimeType='application/vnd.jgraph.mxfile'",  # Standard draw.io files
            "name contains '.drawio'",  # Files with .drawio extension
            "name contains '.draw.io'",  # Alternative extension
            "mimeType='application/xml' and name contains 'drawio'",  # XML files from draw.io
        ]
        
        all_files = []
        
        for query in drawio_queries:
            if search_query:
                full_query = f"({query}) and name contains '{search_query}'"
            else:
                full_query = query
            
            try:
                results = tools.drive_service.files().list(
                    q=full_query,
                    pageSize=max_results,
                    fields='files(id,name,mimeType,modifiedTime,size,webViewLink,owners)',
                    orderBy='modifiedTime desc'
                ).execute()
                
                files = results.get('files', [])
                all_files.extend(files)
                
            except Exception as e:
                print(f"⚠️ Błąd dla zapytania '{query}': {e}")
                continue
        
        # Usuń duplikaty na podstawie ID
        unique_files = {}
        for file in all_files:
            file_id = file.get('id')
            if file_id not in unique_files:
                unique_files[file_id] = file
        
        # Formatuj wyniki
        formatted_files = []
        for file in list(unique_files.values())[:max_results]:
            file_info = {
                'id': file.get('id'),
                'name': file.get('name', 'Bez nazwy'),
                'mime_type': file.get('mimeType'),
                'size': file.get('size', 'Nieznany'),
                'modified_date': file.get('modifiedTime'),
                'web_view_link': file.get('webViewLink'),
                'owners': [owner.get('displayName', 'Nieznany') for owner in file.get('owners', [])],
                'is_drawio': True
            }
            formatted_files.append(file_info)
        
        return {
            'success': True,
            'files': formatted_files,
            'count': len(formatted_files),
            'search_query': search_query or 'wszystkie pliki draw.io',
            'message': f'Znaleziono {len(formatted_files)} plików draw.io'
        }
        
    except Exception as e:
        print(f"❌ Błąd pobierania plików draw.io: {e}")
        return {
            'success': False,
            'error': str(e),
            'message': f'Nie można pobrać plików draw.io: {e}'
        }

async def get_drawio_content(
    file_id: str
) -> Dict[str, Any]:
    """
    Pobiera treść pliku draw.io z Google Drive
    
    Args:
        file_id: ID pliku draw.io w Google Drive
    """
    try:
        tools = CustomGoogleTools()
        
        print(f"🎨 Pobieranie treści pliku draw.io: {file_id}")
        
        # Dodaj timeout żeby uniknąć zawieszenia
        import socket
        socket.setdefaulttimeout(30)
        
        # Pobierz metadane pliku
        file_metadata = tools.drive_service.files().get(
            fileId=file_id,
            fields='id,name,mimeType,size,modifiedTime,webViewLink,owners'
        ).execute()
        
        # Pobierz treść pliku
        content = tools.drive_service.files().get_media(fileId=file_id).execute()
        
        # Dekoduj treść
        if isinstance(content, bytes):
            content_text = content.decode('utf-8')
        else:
            content_text = str(content)
        
        # Sprawdź czy to XML (pliki draw.io są w formacie XML)
        import xml.etree.ElementTree as ET
        try:
            root = ET.fromstring(content_text)
            is_xml = True
            xml_root_tag = root.tag
        except ET.ParseError:
            is_xml = False
            xml_root_tag = None
        
        # Wyciągnij teksty z diagramu (jeśli to XML)
        diagram_texts = []
        if is_xml:
            try:
                # Szukaj wszystkich elementów tekstowych w XML
                for elem in root.iter():
                    if elem.text and elem.text.strip():
                        text = elem.text.strip()
                        if len(text) > 1 and not text.isdigit():  # Filtruj krótkie/numeryczne wartości
                            diagram_texts.append(text)
                    
                    # Sprawdź atrybuty - draw.io często przechowuje tekst w atrybutach
                    for attr_name, attr_value in elem.attrib.items():
                        if attr_name in ['value', 'label', 'text'] and attr_value.strip():
                            text = attr_value.strip()
                            if len(text) > 1:
                                diagram_texts.append(text)
                
                # Usuń duplikaty zachowując kolejność
                diagram_texts = list(dict.fromkeys(diagram_texts))
                
            except Exception as e:
                print(f"⚠️ Błąd parsowania XML: {e}")
        
        return {
            'success': True,
            'file_id': file_id,
            'name': file_metadata.get('name', 'Bez nazwy'),
            'mime_type': file_metadata.get('mimeType'),
            'size': file_metadata.get('size', 'Nieznany'),
            'modified_date': file_metadata.get('modifiedTime'),
            'web_view_link': file_metadata.get('webViewLink'),
            'owners': [owner.get('displayName', 'Nieznany') for owner in file_metadata.get('owners', [])],
            'raw_content': content_text[:1000] + '...' if len(content_text) > 1000 else content_text,  # Pierwsze 1000 znaków
            'is_xml': is_xml,
            'xml_root_tag': xml_root_tag,
            'diagram_texts': diagram_texts,
            'text_count': len(diagram_texts),
            'content_length': len(content_text),
            'message': f'Treść pliku draw.io "{file_metadata.get("name")}" została pobrana pomyślnie'
        }
        
    except Exception as e:
        print(f"❌ Błąd pobierania treści draw.io: {e}")
        return {
            'success': False,
            'error': str(e),
            'message': f'Nie można pobrać treści pliku draw.io: {e}'
        }

async def search_drawio_diagrams(
    search_text: str,
    max_results: int = 10
) -> Dict[str, Any]:
    """
    Wyszukuje diagramy draw.io które zawierają określony tekst
    
    Args:
        search_text: Tekst do wyszukania w diagramach
        max_results: Maksymalna liczba wyników
    """
    try:
        print(f"🔍 Wyszukiwanie '{search_text}' w diagramach draw.io...")
        
        # Najpierw pobierz wszystkie pliki draw.io
        all_files_result = await list_drawio_files(max_results=50)
        
        if not all_files_result['success']:
            return all_files_result
        
        matching_files = []
        
        # Przeszukaj każdy plik
        for file_info in all_files_result['files']:
            try:
                # Pobierz treść pliku
                content_result = await get_drawio_content(file_info['id'])
                
                if content_result['success']:
                    # Sprawdź czy wyszukiwany tekst występuje w treści
                    found_in_texts = False
                    found_in_content = False
                    
                    # Szukaj w wyciągniętych tekstach diagramu
                    if content_result['diagram_texts']:
                        for text in content_result['diagram_texts']:
                            if search_text.lower() in text.lower():
                                found_in_texts = True
                                break
                    
                    # Szukaj w surowej treści XML
                    if search_text.lower() in content_result['raw_content'].lower():
                        found_in_content = True
                    
                    # Jeśli znaleziono, dodaj do wyników
                    if found_in_texts or found_in_content:
                        match_info = {
                            **file_info,
                            'found_in_texts': found_in_texts,
                            'found_in_content': found_in_content,
                            'matching_texts': [
                                text for text in content_result['diagram_texts']
                                if search_text.lower() in text.lower()
                            ] if found_in_texts else [],
                            'diagram_texts': content_result['diagram_texts']
                        }
                        matching_files.append(match_info)
                
            except Exception as e:
                print(f"⚠️ Błąd przeszukiwania pliku {file_info['name']}: {e}")
                continue
        
        # Ogranicz wyniki
        matching_files = matching_files[:max_results]
        
        return {
            'success': True,
            'search_text': search_text,
            'files': matching_files,
            'count': len(matching_files),
            'total_searched': len(all_files_result['files']),
            'message': f'Znaleziono {len(matching_files)} diagramów draw.io zawierających "{search_text}"'
        }
        
    except Exception as e:
        print(f"❌ Błąd wyszukiwania w diagramach draw.io: {e}")
        return {
            'success': False,
            'error': str(e),
            'message': f'Nie można przeszukać diagramów draw.io: {e}'
        } 