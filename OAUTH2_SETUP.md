# 🔐 Konfiguracja OAuth2 dla Google ADK Business Agent

## 1. 🏗️ Utwórz OAuth2 Credentials w Google Cloud Console

### Krok 1: Otwórz Google Cloud Console
```
https://console.cloud.google.com/apis/credentials?project=districtagent
```

### Krok 2: Utwórz OAuth2 Client ID
1. Kliknij **+ CREATE CREDENTIALS**
2. Wybierz **OAuth 2.0 Client IDs**
3. **Application type**: **Desktop application**
4. **Name**: `Google ADK Business Agent`
5. Kliknij **CREATE**

### Krok 3: Pobierz credentials
6. Kliknij **⬇️ Download JSON**
7. Zapisz jako `oauth2_credentials.json` w głównym folderze projektu

---

## 2. 🔧 Aktywuj wymagane APIs

W Google Cloud Console → **APIs & Services** → **Library**, aktywuj:

- ✅ **Gmail API**
- ✅ **Google Calendar API**
- ✅ **Google Drive API** (opcjonalnie)

---

## 3. 🚀 Pierwsza autoryzacja

### Uruchom agenta:
```bash
python start_google_adk_agent.py
```

### W przeglądarce:
1. Agent automatycznie otworzy przeglądarkę
2. Zaloguj się na konto **kdunowski@district.org**
3. Zatwierdź uprawnienia:
   - ✅ Odczyt Gmail
   - ✅ Wysyłanie emaili
   - ✅ Zarządzanie Calendar
4. Agent zapisze token autoryzacji

---

## 4. 🧪 Test funkcjonalności

W WebSocket interfejsie napisz:
```
Test wiadomość
```

Agent powinien automatycznie:
- ✅ Sprawdzić aktualną datę
- ✅ Sprawdzić najnowsze emaile Gmail
- ✅ Sprawdzić kalendarz na dziś

---

## 5. 🔧 Troubleshooting

### ❌ "OAuth2 credentials client_id is missing"
- Sprawdź czy istnieje plik `oauth2_credentials.json`
- Sprawdź format pliku (powinien zawierać `client_id` i `client_secret`)

### ❌ "access_denied" podczas autoryzacji
- Sprawdź czy APIs są aktywowane w Google Cloud Console
- Upewnij się że logujesz się na właściwe konto

### ❌ "invalid_client" 
- Sprawdź czy `redirect_uri` to `http://localhost:8080/callback`
- Sprawdź czy `client_id` i `client_secret` są poprawne

---

## 6. 📁 Struktura plików

```
agentsdkgoogle/
├── oauth2_credentials.json          # OAuth2 config (WYMAGANE)
├── google_cloud_credentials.json    # Service Account (dla Vertex AI)
├── google_adk_business_agent.py     # Główny agent
└── start_google_adk_agent.py        # Launcher
```

## ✅ Sukces!

Po poprawnej konfiguracji agent będzie miał dostęp do:
- 📧 **67 funkcji Gmail** - czytanie, wysyłanie, organizacja
- 📅 **35 funkcji Calendar** - zarządzanie spotkaniami
- 🧠 **Inteligentne analizy** przez Gemini 2.0 Flash 