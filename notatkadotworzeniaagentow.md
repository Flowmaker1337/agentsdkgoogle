# Notatka do tworzenia agentów Google ADK

## Analiza kodu źródłowego Google ADK

### 1. Typy agentów w Google ADK

#### A) **LlmAgent** (podstawowy agent LLM)
- **Cel**: Pojedynczy agent z modelem LLM, narzędziami, instrukcjami
- **Konfiguracja**: `model`, `instruction`, `tools`, `generate_content_config`
- **Użycie**: Do prostych zadań, które nie wymagają koordynacji wielu agentów

#### B) **SequentialAgent** 
- **Cel**: Uruchamia sub-agentów po kolei (sekwencyjnie)
- **Użycie**: Gdy zadanie ma jasne etapy, które muszą być wykonane po kolei
- **Przykład**: 1) Przeczytaj email → 2) Przeanalizuj → 3) Odpowiedz

#### C) **ParallelAgent**
- **Cel**: Uruchamia sub-agentów równolegle w izolowanych branch-ach
- **Użycie**: Gdy potrzebujesz wielu perspektyw/podejść równocześnie
- **Przykład**: Generowanie wielu odpowiedzi do porównania

#### D) **LoopAgent**
- **Cel**: Uruchamia sub-agentów w pętli z `max_iterations`
- **Użycie**: Dla zadań iteracyjnych (refinement, retry logic)

### 2. **RunConfig** - kluczowe ustawienia

```python
RunConfig(
    max_llm_calls=500,  # DOMYŚLNIE 500, nie 20!
    response_modalities=["TEXT"],
    streaming_mode=StreamingMode.NONE,
    save_input_blobs_as_artifacts=False
)
```

**WAŻNE ODKRYCIE**: 
- Domyślny limit to **500 wywołań LLM**, nie 5 czy 20!
- Dla prostego pytania o datę powinno wystarczyć **1-2 wywołania max**

### 3. Problem z moim kodem

#### Co robiłem źle:
1. **Zbyt niski limit LLM calls**: Ustawiłem 5, potem 20 - to za mało dla złożonych zadań
2. **Niepotrzebne fallback-i**: Tworzę 3 warstwy fallback-ów zamiast naprawić jeden główny problem
3. **Błędna konfiguracja agenta**: Prawdopodobnie agent przechodzi w nieskończoną pętlę

#### Prawdziwy problem:
- Agent ma zbyt skomplikowaną strukturę 
- Może ma sub-agentów albo transfer logic która powoduje pętle
- Możliwe że `disallow_transfer_to_parent=False` powoduje ping-pong między agentami

### 4. Optymalna konfiguracja prostego LlmAgent

```python
# PROSTY AGENT - dla podstawowych zadań
agent = LlmAgent(
    name="business_assistant",
    model="gemini-2.0-flash-001",
    instruction="Jesteś asystentem biznesowym. Odpowiadaj krótko i na temat.",
    tools=[get_current_datetime, gmail_tools, calendar_tools],
    disallow_transfer_to_parent=True,  # WAŻNE!
    disallow_transfer_to_peers=True,   # WAŻNE!
    generate_content_config=types.GenerateContentConfig(
        temperature=0.1,  # Niższa temperatura dla precyzji
        max_output_tokens=500  # Ograniczenie długości odpowiedzi
    )
)
```

#### Kluczowe ustawienia:
- `disallow_transfer_to_parent=True` - **zapobiega ping-pong między agentami**
- `disallow_transfer_to_peers=True` - **zapobiega transferom do innych agentów**  
- `temperature=0.1` - mniej kreatywności, więcej precyzji
- `max_output_tokens=500` - krótsze odpowiedzi

### 5. RunConfig dla prostych zadań

```python
run_config = RunConfig(
    response_modalities=["TEXT"],
    max_llm_calls=10,  # Wystarczy dla prostych pytań
    streaming_mode=StreamingMode.NONE
)
```

### 6. Wnioski

**Problem z moim kodem**:
1. Agent prawdopodobnie ma włączone transfery między agentami → pętla
2. Za dużo fallback-ów zamiast naprawienia głównego problemu
3. Niepotrzebna komplikacja dla prostych zadań

**Rozwiązanie**:
1. Stwórz prosty LlmAgent z wyłączonymi transferami
2. Usuń wszystkie fallback-i  
3. Użyj domyślnego RunConfig (500 calls limit)
4. Testuj na prostym pytaniu o datę

**Cel**: 
- Pytanie o datę = **1 wywołanie LLM**
- Proste zadania biznesowe = **1-3 wywołania LLM max**
- Złożone zadania = **10-50 wywołań LLM max** 