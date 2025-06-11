# 🧠 Konfiguracja RAG dla Google ADK Business Agent

## 1. 📧 Dostęp do konta kdunowski@district.org

### A) Google Admin Console (district.org)
Jako super admin organizacji:

1. **Admin Console** → **Security** → **API Controls** → **Domain-wide delegation**
2. **Add new** i wpisz:
   - **Client ID**: (znajdź w google_cloud_credentials.json, pole "client_id")
   - **OAuth scopes**:
     ```
     https://www.googleapis.com/auth/gmail.readonly,
     https://www.googleapis.com/auth/gmail.send,
     https://www.googleapis.com/auth/gmail.modify,
     https://www.googleapis.com/auth/calendar,
     https://www.googleapis.com/auth/calendar.events
     ```

### B) W kodzie agenta
Agent automatycznie użyje impersonacji dla `kdunowski@district.org` przez Service Account.

---

## 2. 🧠 Vertex AI RAG Corpus

### A) Stwórz RAG Corpus
```bash
# 1. Zaloguj się do gcloud
gcloud auth login

# 2. Ustaw projekt
gcloud config set project districtagent

# 3. Stwórz RAG Corpus
gcloud ai rag-corpora create \
  --display-name="Business Emails Knowledge Base" \
  --description="Baza wiedzy z emaili biznesowych kdunowski@district.org" \
  --region=us-central1
```

### B) Zanotuj ID Corpus
Po utworzeniu otrzymasz ID w formacie:
```
projects/districtagent/locations/us-central1/ragCorpora/[CORPUS_ID]
```

### C) Zaktualizuj zmienną środowiskową
W `.env` dodaj:
```bash
GOOGLE_CLOUD_PROJECT=districtagent
RAG_CORPUS_ID=[CORPUS_ID]
```

---

## 3. 🔧 Instalacja zależności

```bash
# Doinstaluj Vertex AI
pip install google-cloud-aiplatform
pip install vertexai

# Zaktualizuj requirements
echo "google-cloud-aiplatform==1.45.0" >> requirements_google_adk.txt
echo "vertexai==1.45.0" >> requirements_google_adk.txt
```

---

## 4. 🚀 Jak działa RAG w agencie

### Automatyczna klasyfikacja emaili:
```python
# Agent automatycznie:
analyze_and_store_email(
    email_content="Treść emaila...",
    sender="klient@firma.com", 
    subject="Oferta na projekt XYZ"
)
```

### Kategorie biznesowe:
- `zarządzanie_projektami` - zadania, deadliny, projekty
- `sprzedaż` - klienci, oferty, zamówienia  
- `finanse` - budżety, płatności, faktury
- `spotkania` - meeting, konferencje
- `pilne` - urgent, asap, natychmiast

### Wyszukiwanie w bazie wiedzy:
```python
# Agent może wyszukiwać kontekst:
business_knowledge_search(
    query="podobne projekty z klientem ABC"
)
```

---

## 5. 📊 Memory Service

Agent automatycznie:
1. **Zapisuje każdą sesję** do Vertex AI RAG
2. **Buduje kontekst** z poprzednich rozmów
3. **Wyszukuje podobne przypadki** z przeszłości
4. **Sugeruje akcje** oparte na historii

---

## 6. 🎯 Przykładowe zastosowania

### Email Analysis + RAG:
```
User: "Sprawdź najnowsze emaile o projektach"
Agent: 
1. Pobiera emaile z Gmail
2. Klasyfikuje każdy email 
3. Zapisuje do RAG
4. Wyszukuje podobne projekty z przeszłości
5. Dostarcza insights: "Podobny projekt z Q3 2023 trwał 3 miesiące"
```

### Contextual Responses:
```
User: "Jak poszło spotkanie z klientem ABC?"
Agent:
1. Wyszukuje w RAG wszystkie wzmianki o kliencie ABC
2. Analizuje historię komunikacji
3. Dostarcza pełny kontekst biznesowy
```

---

## 7. 🔍 Testowanie RAG

Po uruchomieniu agenta przetestuj:

1. **"Przeanalizuj tego emaila: [wklej treść]"**
2. **"Wyszukaj informacje o projekcie XYZ"**  
3. **"Jakie podobne problemy już rozwiązywaliśmy?"**
4. **"Pokaż historię komunikacji z klientem ABC"**

Agent będzie automatycznie budował bazę wiedzy z każdej interakcji! 🚀 