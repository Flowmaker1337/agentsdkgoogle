#!/usr/bin/env python3
"""
Ręczny proces autoryzacji OAuth2 dla Google ADK Business Agent
Ten skrypt uruchomi przeglądarkę i przeprowadzi autoryzację OAuth2
"""

import os
import json
import webbrowser
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

# Scopes potrzebne dla Gmail, Calendar, Google Docs i Drive
SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.send', 
    'https://www.googleapis.com/auth/gmail.modify',
    'https://www.googleapis.com/auth/calendar',
    'https://www.googleapis.com/auth/calendar.events',
    'https://www.googleapis.com/auth/documents',
    'https://www.googleapis.com/auth/drive'
]

def main():
    """Uruchom proces autoryzacji OAuth2"""
    creds = None
    token_file = 'token.json'
    credentials_file = 'oauth2_credentials.json'
    
    print("🔐 Google ADK Business Agent - Autoryzacja OAuth2")
    print("=" * 50)
    
    # Sprawdź czy istnieje już token
    if os.path.exists(token_file):
        print("📂 Znaleziono istniejący token...")
        creds = Credentials.from_authorized_user_file(token_file, SCOPES)
    
    # Jeśli nie ma ważnych credentials, przeprowadź autoryzację
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("🔄 Odświeżanie tokenu...")
            try:
                creds.refresh(Request())
                print("✅ Token odświeżony pomyślnie!")
            except Exception as e:
                print(f"❌ Błąd odświeżania tokenu: {e}")
                creds = None
        
        if not creds:
            print("🚀 Rozpoczynam nową autoryzację...")
            
            if not os.path.exists(credentials_file):
                print(f"❌ Brak pliku {credentials_file}")
                return
            
            try:
                # Uruchom flow autoryzacji
                flow = InstalledAppFlow.from_client_secrets_file(
                    credentials_file, SCOPES)
                
                print("🌐 Otwieram przeglądarkę dla autoryzacji...")
                print("📋 Scopes do autoryzacji:")
                for scope in SCOPES:
                    print(f"   • {scope}")
                print()
                print("👤 Zaloguj się na konto: kdunowski@district.org")
                print("✅ Zaakceptuj wszystkie uprawnienia")
                print()
                
                # Uruchom serwer lokalny i otwórz przeglądarkę
                # Ustawienia manualne żeby było dokładnie jak w Google Cloud Console
                import urllib.parse
                flow.redirect_uri = 'http://localhost:8080'  # BEZ ukośnika na końcu
                creds = flow.run_local_server(
                    port=8080, 
                    open_browser=True,
                    bind_addr='localhost',
                    timeout_seconds=300
                )
                print("✅ Autoryzacja zakończona pomyślnie!")
                
            except Exception as e:
                print(f"❌ Błąd autoryzacji: {e}")
                return
    
    # Zapisz token
    if creds:
        with open(token_file, 'w') as token:
            token.write(creds.to_json())
        print(f"💾 Token zapisany w {token_file}")
        
        print("\n🎉 Autoryzacja OAuth2 zakończona!")
        print("📧 Agent ma teraz dostęp do:")
        print("   • Gmail (czytanie, wysyłanie, modyfikacja)")
        print("   • Calendar (wydarzenia, zarządzanie)")
        print("   • Google Docs (tworzenie, czytanie, edycja)")
        print("   • Google Drive (zarządzanie plikami)")
        print("\n🚀 Możesz teraz uruchomić Google ADK Business Agent")
        print("   python google_adk_business_agent.py")
    else:
        print("❌ Nie udało się uzyskać tokenu autoryzacji")

if __name__ == '__main__':
    main() 