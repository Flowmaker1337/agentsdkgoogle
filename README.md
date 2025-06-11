# 🎭 MetaHuman Business Assistant

**Inteligentny asystent biznesowy z avatarem MetaHuman w Unreal Engine 5**

Połączenie zaawansowanej sztucznej inteligencji Google ADK z 3D avatarem MetaHuman, stwarzające nową generację osobistych asystentów biznesowych.

![MetaHuman Business Assistant](https://via.placeholder.com/800x400/0078d4/ffffff?text=MetaHuman+Business+Assistant)

## 🌟 Funkcje

### 🤖 AI Assistant (Backend)
- **Google ADK + Gemini 2.0 Flash** - najnowsza technologia AI
- **MCP Protocol** - integracja z dziesiątkami systemów biznesowych
- **Async WebSocket** - komunikacja w czasie rzeczywistym z UE5
- **Business Intelligence** - analityka, raporty, automatyzacja

### 🎭 MetaHuman Avatar (UE5 Frontend)  
- **Photorealistic MetaHuman** - profesjonalny wygląd biznesowy
- **Voice Recognition** - rozpoznawanie mowy (macOS/Windows/Linux)
- **Text-to-Speech** - naturalna synteza mowy
- **Lip Sync** - synchronizacja ruchu ust z mową
- **Animation States** - reaktywne animacje (słuchanie, myślenie, mówienie)

### 💼 Business Integration
- **📅 Google Calendar** - zarządzanie kalendarzem i spotkaniami
- **📧 Gmail** - analiza i wysyłanie emaili
- **📝 Notion** - zarządzanie projektami i dokumentacją  
- **🔍 Google Search** - wyszukiwanie informacji biznesowych
- **📊 Analytics** - raporty i analizy biznesowe

## 🚀 Szybki Start

### Krok 1: Instalacja
```bash
# Sklonuj lub pobierz projekt
cd metahuman-business-assistant

# Instalacja zależności Python
pip install -r requirements.txt

# Instalacja MCP serwerów
npm install -g @notionhq/notion-mcp-server
npm install -g google-calendar-mcp-server
npm install -g gmail-mcp-server
```

### Krok 2: Konfiguracja
```bash
# Skopiuj i edytuj plik konfiguracyjny
cp env_example.txt .env

# Edytuj .env i dodaj swoje API keys:
# GOOGLE_API_KEY=twój_klucz_google_ai_studio
# NOTION_API_KEY=twój_klucz_notion
```

### Krok 3: Test (bez UE5)
```bash
# Uruchom w trybie testowym
python start_business_assistant.py --test
```

### Krok 4: Integracja z UE5
```bash
# Uruchom serwer WebSocket dla UE5
python start_business_assistant.py

# W UE5: Połącz się z ws://localhost:8765
```

## 📖 Szczegółowa Dokumentacja

### 🎮 Integracja z UE5
Kompletny przewodnik integracji z Unreal Engine 5 znajdziesz w:
**[UE5_Integration_Guide.md](UE5_Integration_Guide.md)**

Zawiera szczegółowe instrukcje:
- Konfiguracja WebViewEnhanced Plugin
- Tworzenie MetaHuman Avatar
- WebSocket Communication Setup
- Voice Recognition i Text-to-Speech
- Animation System
- UI/UX Design

### 🔧 Konfiguracja MCP
Asystent wykorzystuje **Model Context Protocol** do integracji z systemami biznesowymi:

```python
# Przykład konfiguracji Google Calendar
MCPToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            command="npx",
            args=["-y", "google-calendar-mcp-server"]
        )
    ),
    tool_filter=['list_events', 'create_event', 'find_free_time']
)
```

## 💼 Przykłady Użycia

### Zarządzanie Kalendarzem
```
👤 "Sprawdź mój kalendarz na dziś"
🎭 "Masz 3 spotkania: 9:00 standup, 14:00 prezentacja, 16:30 1:1 z Anną"

👤 "Zaplanuj spotkanie z zespołem na jutro"  
🎭 "Sprawdzam dostępność... Mogę zarezerwować jutro 10:00-11:00. Wysłać zaproszenia?"
```

### Analiza Biznesowa
```
👤 "Przygotuj raport sprzedaży z tego tygodnia"
🎭 "📊 RAPORT SPRZEDAŻY: Wzrost o 15%, 89 nowych leadów, top produkt: WebApp Pro"

👤 "Pokaż produktywność zespołu"
🎭 "📈 Zespół ma 87% efektywności, najlepsze godziny: 9-11, optymalne dni: Wt/Śr"
```

### Komunikacja
```
👤 "Napisz email do klienta o opóźnieniu projektu"
🎭 "Przygotowałem profesjonalny email z przeprosinami i nowym timeline. Wysłać?"

👤 "Sprawdź czy mam ważne wiadomości"
🎭 "3 pilne emaile: oferta od BigCorp, pytanie o cennik, zaproszenie na konferencję"
```

## 🛠 Architektura Systemu

```
🎭 MetaHuman Avatar (UE5)
    ↕️ WebSocket (ws://localhost:8765)
🤖 Business Agent (Python + Google ADK)
    ↕️ MCP Protocol
📊 Business Tools:
    ├── 📅 Google Calendar API
    ├── 📧 Gmail API  
    ├── 📝 Notion API
    ├── 🔍 Google Search API
    └── 📊 Custom Analytics
```

## 🔐 Bezpieczeństwo

### Zabezpieczenia
- **Lokalne połączenia** - tylko localhost WebSocket
- **Rate Limiting** - ograniczenie liczby zapytań
- **Tool Filtering** - ograniczenie dostępnych funkcji
- **API Key Management** - bezpieczne przechowywanie kluczy
- **Input Validation** - walidacja wszystkich danych wejściowych

### Best Practices
```python
# Ograniczenie narzędzi do bezpiecznych operacji
tool_filter=['read_file', 'list_directory']  # ✅ Bezpieczne
# tool_filter=['delete_file', 'format_disk']  # ❌ Niebezpieczne
```

## 🎯 Rozbudowa

### Gotowe rozszerzenia:
- **CRM Integration** (Salesforce, HubSpot)
- **Finance APIs** (QuickBooks, Stripe)
- **Project Management** (Jira, Monday.com)
- **Cloud Services** (AWS, Azure, GCP)
- **Social Media** (LinkedIn, Twitter)

### Planowane funkcje:
- **AI Vision** - analiza dokumentów przez kamerę
- **Multi-language** - obsługa wielu języków
- **Mobile App** - kompaktowa aplikacja mobilna
- **VR/AR Support** - rozszerzona rzeczywistość
- **Team Collaboration** - współpraca zespołowa

## 📋 Wymagania Systemowe

### Python (Backend)
- **Python 3.9+**
- **Google ADK 1.2.1+**
- **4GB RAM** (minimum)
- **Dostęp do internetu** (dla APIs)

### UE5 (Frontend)
- **Unreal Engine 5.3+**
- **WebViewEnhanced Plugin**
- **MetaHuman Creator** assets
- **8GB RAM** (minimum)
- **Dedykowana karta graficzna** (zalecane)

### Platformy
- ✅ **macOS** (pełne wsparcie + WebViewEnhanced)
- ✅ **Windows** (pełne wsparcie)
- ✅ **Linux** (ograniczone wsparcie voice)

## 🆘 Pomoc i Support

### Częste Problemy

**Problem**: *Agent nie odpowiada*
```bash
# Sprawdź logi
python start_business_assistant.py --test
# Verify API keys w .env
```

**Problem**: *UE5 nie łączy się*
```bash
# Sprawdź czy serwer działa
netstat -an | grep 8765
# Sprawdź firewall
```

**Problem**: *MCP tools nie działają*
```bash
# Sprawdź instalację MCP serwerów
npm list -g @notionhq/notion-mcp-server
# Reinstall w razie potrzeby
npm install -g @notionhq/notion-mcp-server
```

### Wsparcie Techniczne
- 📧 **Email**: [support@your-domain.com]
- 💬 **Discord**: [Link do serwera]
- 📖 **Wiki**: [Link do dokumentacji]
- 🐛 **Issues**: [GitHub Issues]

## 📜 Licencja

MIT License - patrz [LICENSE](LICENSE) dla szczegółów.

## 🙏 Podziękowania

- **Anthropic** - za Model Context Protocol
- **Google** - za ADK i Gemini AI
- **Epic Games** - za MetaHuman Creator
- **Społeczność MCP** - za niesamowite serwery

---

**🎉 Zbuduj przyszłość osobistych asystentów biznesowych już dziś!**

*MetaHuman Business Assistant - gdzie AI spotyka się z rzeczywistością.* 