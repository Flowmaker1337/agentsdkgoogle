# 🚀 Google ADK Business Agent - Launcher

## Szybkie uruchomienie

### Opcja 1: Pełny Launcher (Zalecane)
```bash
python AgentLauncher.py
```

**Funkcje:**
- ✅ Uruchamia oba serwisy jednocześnie
- ✅ Monitoruje procesy w czasie rzeczywistym
- ✅ Automatyczne zatrzymywanie przy Ctrl+C
- ✅ Kolorowe logi z timestampami
- ✅ Sprawdzanie zależności
- ✅ Automatyczne otwieranie przeglądarki

### Opcja 2: Prosty Starter
```bash
python start.py
```

**Funkcje:**
- ✅ Szybkie uruchomienie
- ✅ Automatyczne otwieranie przeglądarki
- ⚠️ Wymaga ręcznego zatrzymania procesów

### Opcja 3: Ręczne uruchomienie (jak wcześniej)
```bash
# Terminal 1
python session_api.py

# Terminal 2  
python google_adk_business_agent.py
```

## Co zostaje uruchomione?

### 1. Session API (Port 8000)
- **Glass UI**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/api/health
- **Zarządzanie sesjami**: SQLite database

### 2. Business Agent (Port 8765)
- **WebSocket**: ws://localhost:8765
- **Google API Integration**: Gmail, Calendar, Docs, Drive
- **Draw.io Support**: Odczyt diagramów
- **OAuth2 Authentication**: Automatyczne tokeny

## Zatrzymywanie

### AgentLauncher.py
```bash
Ctrl+C  # Zatrzyma wszystkie procesy automatycznie
```

### start.py lub ręczne uruchomienie
```bash
# Znajdź procesy
ps aux | grep python

# Zatrzymaj procesy
kill <PID_session_api>
kill <PID_business_agent>

# Lub użyj pkill
pkill -f session_api.py
pkill -f google_adk_business_agent.py
```

## Rozwiązywanie problemów

### Port już zajęty
```bash
# Sprawdź co używa portów
lsof -i :8000
lsof -i :8765

# Zatrzymaj procesy
kill -9 <PID>
```

### Brakujące zależności
```bash
pip install -r requirements.txt
```

### Problemy z OAuth2
1. Sprawdź `google_cloud_credentials.json`
2. Sprawdź `oauth2_tokens.json`
3. Uruchom ponownie autoryzację

## Logi i debugowanie

### AgentLauncher.py
- Kolorowe logi w czasie rzeczywistym
- Automatyczne monitorowanie procesów
- Informacje o statusie serwisów

### Ręczne sprawdzenie
```bash
# Session API
curl http://localhost:8000/api/health

# Lista sesji
curl http://localhost:8000/api/sessions

# Business Agent (sprawdź logi w terminalu)
```

## Struktura plików

```
agentsdkgoogle/
├── AgentLauncher.py          # 🚀 Główny launcher
├── start.py                  # 🚀 Prosty starter
├── session_api.py            # 📡 Session API
├── google_adk_business_agent.py  # 🤖 Business Agent
├── modern_glass_agent_ui.html    # 🎨 Glass UI
├── session_database.py       # 💾 Database layer
├── custom_google_tools.py    # 🛠️ Google tools
└── README_LAUNCHER.md        # 📖 Ta dokumentacja
```

## Porady

1. **Używaj AgentLauncher.py** - najwygodniejsze rozwiązanie
2. **Sprawdź porty** - upewnij się że 8000 i 8765 są wolne
3. **Otwórz http://localhost:8000** - główny interfejs
4. **Ctrl+C zatrzymuje wszystko** - w AgentLauncher.py
5. **Sprawdź logi** - jeśli coś nie działa 