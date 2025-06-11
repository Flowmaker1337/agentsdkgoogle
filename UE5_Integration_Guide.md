# 🎭 MetaHuman Business Assistant - Przewodnik Integracji UE5

## 🎯 Przegląd Systemu

```
👤 Użytkownik (Ty)
    ↕️ Voice/Text Input
🎭 MetaHuman Avatar (UE5)
    ↕️ WebViewEnhanced/WebSocket
🤖 Business Agent (Python)
    ↕️ MCP Protocol
📊 Business Tools (APIs)
```

## 🚀 Krok 1: Przygotowanie Agenta Python

### Instalacja zależności:

```bash
# Instalacja Google ADK
pip install -r requirements.txt

# Instalacja MCP servers
npm install -g google-calendar-mcp-server
npm install -g gmail-mcp-server  
npm install -g @notionhq/notion-mcp-server
```

### Konfiguracja środowiska:
```bash
# Skopiuj i uzupełnij plik konfiguracyjny
cp env_example.txt .env
# Edytuj .env z Twoimi API keys
```

## 🎮 Krok 2: Konfiguracja UE5

### A) Instalacja WebViewEnhanced Plugin

1. **Pobierz WebViewEnhanced** z Marketplace lub GitHub
2. **Umieść w folderze Plugins** Twojego projektu UE5
3. **Rebuild projekt** - ważne dla macOS!
4. **Włącz plugin** w Editor → Plugins

### B) Tworzenie MetaHuman Avatar

1. **MetaHuman Creator**:
   - Stwórz swojego biznes avatara
   - Pobierz do UE5
   - Ustawienie animacji (Idle, Talking, Listening)

2. **Setup Animation Blueprint**:
   ```cpp
   // Stany animacji
   - Idle (spokojny)
   - Talking (animacja mowy)
   - Listening (skupiony)
   - Thinking (zamyślony)
   ```

### C) WebSocket Communication Setup

**Utwórz Blueprint Communication Manager:**

```cpp
// Variables
FString WebSocketURL = "ws://localhost:8765"
bool bIsConnected = false
FString CurrentUserInput = ""
FString AgentResponse = ""

// Events  
UFUNCTION(BlueprintCallable)
void ConnectToAgent();

UFUNCTION(BlueprintCallable) 
void SendMessageToAgent(FString Message);

UFUNCTION(BlueprintImplementableEvent)
void OnAgentResponse(const FString& Response);
```

## 🎤 Krok 3: Voice Integration

### Speech-to-Text Setup (macOS):
```cpp
// W Blueprint lub C++
#include "Components/SpeechRecognitionComponent.h"

UCLASS()
class METAHUMANBUSINESS_API AVoiceManager : public AActor
{
    GENERATED_BODY()

public:
    UFUNCTION(BlueprintCallable)
    void StartListening();
    
    UFUNCTION(BlueprintCallable)
    void StopListening();
    
    UFUNCTION(BlueprintImplementableEvent)
    void OnSpeechRecognized(const FString& RecognizedText);
};
```

### Text-to-Speech Setup:
```cpp
// Użyj platformowego TTS
UFUNCTION(BlueprintCallable)
void SpeakText(FString TextToSpeak)
{
    // macOS: NSString* command = [NSString stringWithFormat:@"say '%@'", text];
    // Windows: SAPI
    // Linux: espeak
}
```

## 🔌 Krok 4: WebViewEnhanced Integration

### Setup HTML Interface:
```html
<!DOCTYPE html>
<html>
<head>
    <title>MetaHuman Business Interface</title>
    <style>
        body { 
            background: transparent; 
            font-family: 'Segoe UI', Arial; 
            color: white;
        }
        .chat-container { 
            padding: 20px; 
            max-width: 800px; 
        }
        .message { 
            margin: 10px 0; 
            padding: 15px; 
            border-radius: 10px; 
        }
        .user { background: #0078d4; }
        .assistant { background: #2d3748; }
    </style>
</head>
<body>
    <div class="chat-container">
        <div id="messages"></div>
        <input type="text" id="userInput" placeholder="Napisz wiadomość...">
    </div>
    
    <script>
        // WebSocket connection to Python agent
        const ws = new WebSocket('ws://localhost:8765');
        
        ws.onmessage = function(event) {
            addMessage('assistant', event.data);
            // Send to UE5 via UE5 interface
            if (window.ue) {
                window.ue.interface.broadcast('AgentResponse', event.data);
            }
        };
        
        function sendMessage(text) {
            addMessage('user', text);
            ws.send(text);
        }
        
        function addMessage(sender, text) {
            const messages = document.getElementById('messages');
            const div = document.createElement('div');
            div.className = `message ${sender}`;
            div.textContent = text;
            messages.appendChild(div);
            messages.scrollTop = messages.scrollHeight;
        }
        
        // UE5 Interface binding
        if (window.ue && window.ue.interface) {
            window.ue.interface.bind('SendToAgent', sendMessage);
        }
    </script>
</body>
</html>
```

## 🎯 Krok 5: UE5 Blueprint Logic

### Main GameMode Blueprint:

```cpp
// Event BeginPlay
void AMetaHumanBusinessGameMode::BeginPlay()
{
    Super::BeginPlay();
    
    // Initialize WebView
    InitializeWebView();
    
    // Start listening for voice
    StartVoiceRecognition();
    
    // Connect to Python agent
    ConnectToBusinessAgent();
}

// Custom Events
UFUNCTION(BlueprintImplementableEvent)
void OnUserSpoke(const FString& UserText);

UFUNCTION(BlueprintImplementableEvent)  
void OnAgentResponded(const FString& AgentText);

UFUNCTION(BlueprintCallable)
void SendToAgent(const FString& Message)
{
    // Send via WebSocket to Python
    WebSocketComponent->SendMessage(Message);
    
    // Update MetaHuman state to "Thinking"
    MetaHumanRef->SetAnimationState(EMetaHumanState::Thinking);
}
```

### MetaHuman Animation Controller:

```cpp
UENUM(BlueprintType)
enum class EMetaHumanState : uint8
{
    Idle        UMETA(DisplayName = "Idle"),
    Listening   UMETA(DisplayName = "Listening"), 
    Thinking    UMETA(DisplayName = "Thinking"),
    Speaking    UMETA(DisplayName = "Speaking")
};

UFUNCTION(BlueprintCallable)
void SetAnimationState(EMetaHumanState NewState)
{
    CurrentState = NewState;
    
    switch(NewState)
    {
    case EMetaHumanState::Idle:
        PlayIdleAnimation();
        break;
    case EMetaHumanState::Listening:
        PlayListeningAnimation();
        break;
    case EMetaHumanState::Thinking:
        PlayThinkingAnimation();
        break;
    case EMetaHumanState::Speaking:
        PlaySpeakingAnimation();
        break;
    }
}
```

## 🔊 Krok 6: Audio System

### Lip Sync Integration:
```cpp
// Użyj Audio2Face lub OVR Lip Sync
UCLASS()
class METAHUMANBUSINESS_API ULipSyncComponent : public UActorComponent
{
    GENERATED_BODY()

public:
    UFUNCTION(BlueprintCallable)
    void StartLipSync(USoundWave* AudioToPlay);
    
    UFUNCTION(BlueprintCallable)
    void StopLipSync();
    
private:
    UPROPERTY()
    class UOVRLipSyncContextWrapper* LipSyncContext;
};
```

## 📱 Krok 7: UI/UX Design

### Modern Business Interface:
- **Floating UI panels** z informacjami biznesowymi
- **Voice visualization** (spektrogram podczas mówienia)
- **Status indicators** (połączenie z APIs)
- **Quick actions** (kalendarz, zadania, raporty)

## 🛡️ Krok 8: Security & Performance

### Security Considerations:
```cpp
// Weryfikacja połączeń WebSocket
bool ValidateWebSocketConnection(FString ClientIP)
{
    // Tylko lokalne połączenia
    return ClientIP.StartsWith("127.0.0.1") || ClientIP.StartsWith("localhost");
}

// Rate limiting
UPROPERTY()
int32 RequestsPerMinute = 60;
```

### Performance Optimization:
- **Async WebSocket communication**
- **Cached responses** dla częstych zapytań
- **Efficient MetaHuman LOD** system
- **Audio streaming** zamiast pełnego ładowania

## 🚀 Krok 9: Uruchomienie Systemu

### Sekwencja startowa:

1. **Uruchom Python Agent**:
   ```bash
   python business_avatar_agent.py
   ```

2. **Uruchom UE5 projekt**:
   - Compile w trybie Editor
   - Uruchom z flagą -log dla debugowania

3. **Test połączenia**:
   - Sprawdź WebSocket connection
   - Test voice input/output
   - Weryfikuj MCP tools

### Przykładowe komendy testowe:
- *"Sprawdź mój kalendarz na dziś"*
- *"Napisz email do zespołu o spotkaniu"*
- *"Przygotuj raport sprzedaży z tego tygodnia"*
- *"Zaplanuj spotkanie z klientem na jutro"*

## 🔧 Troubleshooting

### Częste problemy:

1. **WebSocket nie łączy**:
   - Sprawdź firewall
   - Weryfikuj port 8765
   - Check Python agent logs

2. **MetaHuman nie animuje**:
   - Rebuild Animation Blueprint
   - Check Animation State Machine
   - Verify Skeletal Mesh

3. **Voice nie działa**:
   - Uprawnienia mikrofonu (macOS)
   - Audio device configuration
   - Check Speech Recognition component

4. **MCP tools fail**:
   - Verify API keys w .env
   - Check npm packages installation
   - Test individual MCP servers

## 🎯 Następne kroki rozbudowy:

1. **AI Vision** - analiza dokumentów przez kamerkę
2. **Multi-language support** - obsługa wielu języków  
3. **Custom business integrations** - integracja z CRM/ERP
4. **Mobile companion app** - kontrola przez telefon
5. **VR/AR support** - rozszerzona rzeczywistość

---

**🎉 Gratulacje! Masz teraz kompletnego MetaHuman Business Assistant!**

Twój avatar będzie mógł:
- ✅ Zarządzać kalendarzem i spotkaniami
- ✅ Analizować i wysyłać emaile  
- ✅ Tworzyć raporty biznesowe
- ✅ Komunikować się naturalnie (głos + tekst)
- ✅ Wyglądać profesjonalnie w 3D
- ✅ Integrować się z Twoimi systemami biznesowymi 