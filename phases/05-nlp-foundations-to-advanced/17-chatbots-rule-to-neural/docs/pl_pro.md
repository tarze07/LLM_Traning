# Chatboty – od systemów regułowych i neuronowych do agentów LLM

> ELIZA odpowiadała na podstawie dopasowywania wzorców. Dialogflow mapował intencje użytkownika. GPT generował odpowiedzi w oparciu o wagi sieci. Claude uruchamia zewnętrzne narzędzia i weryfikuje ich wyniki. Każda kolejna era rozwiązywała kluczowe wady poprzedniej.

**Typ:** Teoria
**Języki:** Python
**Wymagania wstępne:** Faza 5 · 13 (Odpowiadanie na pytania), Faza 5 · 14 (Wyszukiwanie informacji)
**Czas:** ~75 minut

## Problem

Użytkownik pisze: „Chcę zmienić swój lot”. System musi zidentyfikować jego intencję, ustalić, jakich informacji brakuje, jak je pozyskać i jak sfinalizować operację. Następnie użytkownik dodaje: „Czekaj, a co jeśli zamiast tego anuluję rezerwację?”. W tym momencie system musi poprawnie obsłużyć kontekst, płynnie przełączyć się między zadaniami i utrzymać stan konwersacji.

Projektowanie systemów konwersacyjnych to jedno z najtrudniejszych zadań w uczeniu maszynowym. Dane wejściowe mają charakter otwarty, a odpowiedzi muszą zachować spójność na przestrzeni wielu tur konwersacji (turns). Co więcej, system często musi wchodzić w interakcję ze światem zewnętrznym (np. zmieniać rezerwacje lotów czy obciążać karty płatnicze), a każde potknięcie jest natychmiast widoczne dla użytkownika.

Architektury chatbotów ewoluowały przez cztery główne paradygmaty – każdy z nich powstawał jako odpowiedź na ograniczenia poprzednika. W tej lekcji przeanalizujemy ich rozwój. Współczesne systemy produkcyjne w 2026 roku są zazwyczaj hybrydą dwóch ostatnich podejść.

## Koncepcja

![Ewolucja chatbotów: systemy regułowe → wyszukiwanie → modele neuronowe → agenci](../assets/chatbot.svg)

**Systemy regułowe (ELIZA, AIML, Dialogflow).** Ręcznie zdefiniowane reguły i szablony dopasowują wypowiedzi użytkownika i generują odpowiedzi. Klasyfikatory intencji (intents) kierują rozmowę do predefiniowanych ścieżek, a maszyny stanów realizujące tzw. wypełnianie szczelin (slot-filling) zbierają brakujące dane. Rozwiązanie to działa bezbłędnie w wąskim zakresie, do którego zostało zaprojektowane, lecz natychmiast zawodzi przy jakiejkolwiek odchyłce. Wciąż jest jednak stosowane w krytycznych obszarach (np. autoryzacja bankowa, systemy rezerwacyjne linii lotniczych), gdzie nie można pozwolić na halucynacje modeli.

**Systemy oparte na wyszukiwaniu (Retrieval-based).** Działają na zasadzie inteligentnego FAQ. Baza zawiera pary (pytanie, odpowiedź). W czasie rzeczywistym system koduje zapytanie użytkownika do postaci wektora i wyszukuje najbardziej podobne pytanie w bazie, zwracając przypisaną do niego odpowiedź (podobnie jak moduł sugerowania artykułów w Zendesk). Rozwiązanie to lepiej radzi sobie z parafrazami niż sztywne reguły i – ponieważ nie generuje tekstu od zera – całkowicie eliminuje ryzyko halucynacji.

**Modele neuronowe (seq2seq).** Architektury koder-dekoder trenowane bezpośrednio na logach konwersacji. Generują odpowiedzi od zera. Wypowiedzi są płynne językowo, ale modele te mają skłonność do dawania ogólnikowych odpowiedzi (np. „Nie wiem”, „Super”) oraz dryfu tematycznego i halucynacji. Trudno utrzymać je w ryzach konkretnego tematu. To właśnie te ograniczenia leżały u podstaw niepowodzeń pierwszych chatbotów od Google, Facebooka i Microsoftu w latach 2016–2019.

**Agenci LLM.** Duży model językowy zintegrowany w pętli wykonawczej, która planuje działania, wywołuje zewnętrzne narzędzia i weryfikuje ich wyniki. Nie jest to po prostu chatbot z rozbudowanym promptem. Pętla agenta wygląda następująco: planowanie → wywołanie narzędzia (tool call) → obserwacja wyniku → decyzja o kolejnym kroku. Zastosowanie mechanizmu RAG (Retrieval-Augmented Generation) chroni model przed halucynacjami, a interfejsy API (wywołania funkcji/narzędzi) pozwalają mu na realne wykonywanie akcji. To dominująca architektura w 2026 roku.

Te cztery podejścia nie wykluczają się wzajemnie. Nowoczesny chatbot produkcyjny w 2026 roku łączy je w jedną całość: reguły obsługują uwierzytelnianie i kluczowe operacje, baza FAQ odpowiada na standardowe pytania, generowanie neuronowe dba o naturalne brzmienie wypowiedzi, a agent LLM obsługuje złożone, otwarte zapytania.

## Zbuduj to

### Krok 1: Dopasowywanie wzorców w systemach regułowych

```python
import re

class RulePattern:
    def __init__(self, pattern, response_template):
        self.regex = re.compile(pattern, re.IGNORECASE)
        self.template = response_template

PATTERNS = [
    RulePattern(r"my name is (\w+)", "Nice to meet you, {0}."),
    RulePattern(r"i (need|want) (.+)", "Why do you {0} {1}?"),
    RulePattern(r"i feel (.+)", "Why do you feel {0}?"),
    RulePattern(r"(.*)", "Tell me more about that."),
]

def rule_based_respond(user_input):
    for pattern in PATTERNS:
        m = pattern.regex.match(user_input.strip())
        if m:
            return pattern.template.format(*m.groups())
    return "I don't understand."
```

Oto ELIZA w 20 linijkach kodu. Zastosowany tu zabieg zwierciadlany (np. „Czuję się smutny” → „Dlaczego czujesz się smutny?”) to klasyczna demonstracja wirtualnego psychoterapeuty Weizenbauma z 1966 roku. Mimo upływu lat, wciąż pozostaje to świetnym przykładem dydaktycznym.

### Krok 2: System oparty na wyszukiwaniu (FAQ)

Ten przykładowy fragment kodu wymaga zainstalowania biblioteki `sentence-transformers` (która instaluje również PyTorcha). W pliku wykonywalnym `code/main.py` w celach demonstracyjnych wykorzystano współczynnik Jaccarda z biblioteki standardowej, co pozwala na uruchomienie kodu bez zewnętrznych zależności.

```python
from sentence_transformers import SentenceTransformer
import numpy as np

FAQ = [
    ("how do i reset my password", "Go to Settings > Security > Reset Password."),
    ("how do i cancel my order", "Go to Orders, find the order, click Cancel."),
    ("what is your return policy", "30-day returns on unused items, original packaging."),
]

encoder = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
faq_questions = [q for q, _ in FAQ]
faq_embeddings = encoder.encode(faq_questions, normalize_embeddings=True)

def faq_respond(user_input, threshold=0.5):
    q_emb = encoder.encode([user_input], normalize_embeddings=True)[0]
    sims = faq_embeddings @ q_emb
    best = int(np.argmax(sims))
    if sims[best] < threshold:
        return None
    return FAQ[best][1]
```

Zastosowanie progu odcięcia (threshold) to kluczowa decyzja projektowa. Jeśli stopień dopasowania najlepszej odpowiedzi jest poniżej progu, zwracamy `None` i pozwalamy systemowi przekazać zapytanie dalej (np. do konsultanta lub agenta LLM).

### Krok 3: Generowanie neuronowe (baseline)

Użycie małego, dostrojonego pod kątem instrukcji modelu koder-dekoder (np. FLAN-T5) lub innego modelu konwersacyjnego. W 2026 roku takie modele jako samodzielne rozwiązania produkcyjne są niewystarczające (ze względu na sprzeczności, dryfowanie i halucynacje), ale świetnie sprawdzają się w architekturach hybrydowych do nadawania wypowiedziom naturalnego brzmienia. Modele oparte wyłącznie na dekoderze (np. DialoGPT) wymagają dokładnego definiowania separatorów tur konwersacji i obsługi tokenów końca sekwencji (EOS); z kolei potok text-to-text modelu FLAN-T5 działa w celach dydaktycznych od razu po zainicjowaniu.

```python
from transformers import pipeline

chatbot = pipeline("text2text-generation", model="google/flan-t5-small")

response = chatbot("Respond politely to: Hi there!", max_new_tokens=40)
print(response[0]["generated_text"])
```

### Krok 4: Pętla agenta LLM

Wzorzec architektury produkcyjnej w 2026 roku:

```python
def agent_loop(user_message, tools, llm, max_steps=5):
    history = [{"role": "user", "content": user_message}]
    for _ in range(max_steps):
        response = llm(history, tools=tools)
        tool_call = response.get("tool_call")
        if tool_call:
            tool_name = tool_call.get("name")
            args = tool_call.get("arguments")
            if not isinstance(tool_name, str) or tool_name not in tools:
                history.append({"role": "assistant", "tool_call": tool_call})
                history.append({"role": "tool", "name": str(tool_name), "content": f"error: unknown tool {tool_name!r}"})
                continue
            if not isinstance(args, dict):
                history.append({"role": "assistant", "tool_call": tool_call})
                history.append({"role": "tool", "name": tool_name, "content": f"error: arguments must be a dict, got {type(args).__name__}"})
                continue
            fn = tools[tool_name]
            result = fn(**args)
            history.append({"role": "assistant", "tool_call": tool_call})
            history.append({"role": "tool", "name": tool_name, "content": result})
        else:
            return response["content"]
    return "I could not complete the task in the step budget."
```

Warto zwrócić uwagę na trzy kwestie: Narzędzia (tools) to funkcje wykonywalne, które model LLM może zdecydować się wywołać. Pętla kończy się, gdy model zamiast wywołania narzędzia zwraca ostateczną odpowiedź dla użytkownika. Budżet kroków (max_steps) zapobiega wpadnięciu agenta w nieskończoną pętlę przy niejednoznacznych poleceniach.

Systemy produkcyjne dodatkowo wdrażają: weryfikację kontekstową RAG (wstrzykiwanie odpowiednich dokumentów do promptu), barierki ochronne (guardrails – np. blokowanie krytycznych akcji bez autoryzacji), obserwowalność (logowanie każdego kroku działania agenta) oraz automatyczną ewaluację (ciągła weryfikacja, czy agent działa zgodnie z założeniami).

### Krok 5: Routing hybrydowy

```python
def hybrid_chat(user_input):
    if is_destructive_action(user_input):
        return structured_flow(user_input)

    faq_answer = faq_respond(user_input, threshold=0.6)
    if faq_answer:
        return faq_answer

    return agent_loop(user_input, tools, llm)

def is_destructive_action(text):
    danger_words = ["delete", "cancel", "charge", "refund", "transfer"]
    return any(w in text.lower() for w in danger_words)
```

Złota reguła: deterministyczne przepływy regułowe dla operacji krytycznych/anulowania subskrypcji, wyszukiwanie FAQ dla powtarzalnych pytań oraz agenci LLM do obsługi nietypowych, otwartych problemów. To standard wdrażany w systemach obsługi klienta w 2026 roku.

## Zastosowanie

Zalecane architektury na rok 2026:

| Przypadek użycia | Architektura |
|--------|--------------|
| Rezerwacja, płatność, uwierzytelnienie | Maszyny stanowe oparte na regułach + wypełnianie szczelin (slot-filling) |
| Często zadawane pytania dotyczące obsługi klienta | Pobieranie predefiniowanych odpowiedzi (FAQ Retrieval) |
| Otwarty czat pomocy technicznej | Agent LLM z RAG + wywołaniami narzędzi |
| Narzędzia wewnętrzne / Asystenci IDE | Agent LLM z wywołaniami narzędzi (wyszukiwanie, odczyt, zapis) |
| Chatboty towarzyszące / odgrywające role | Dostrojony LLM z systemowym promptem definiującym personę + RAG do zarządzania pamięcią |

W systemach produkcyjnych zawsze warto stosować routing hybrydowy. Żadna pojedyncza architektura nie poradzi sobie optymalnie ze wszystkimi zapytaniami. Warstwa routingu jest zazwyczaj szybkim klasyfikatorem intencji (intent classifier) o niskim koszcie obliczeniowym.

## Typowe problemy i luki bezpieczeństwa (Failure Modes)

- **Pozorna realizacja (Pewna fabrykacja):** Agent LLM z pełnym przekonaniem twierdzi, że wykonał zadaną czynność (np. przelał środki), choć w rzeczywistości tego nie zrobił. Środki zaradcze: bezwzględnie weryfikuj wyniki wywołań narzędzi, loguj ich wykonanie i nigdy nie pozwalaj modelowi na informowanie o sukcesie operacji bez potwierdzenia z zewnętrznego API.
- **Prompt Injection (Wstrzykiwanie instrukcji):** Użytkownik przesyła złośliwy tekst, który nadpisuje pierwotne instrukcje systemowe. Jest to podatność sklasyfikowana jako LLM01 na liście OWASP Top 10 for LLM Applications. Występuje w dwóch odmianach: wstrzykiwanie bezpośrednie (direct injection – poprzez okno czatu) oraz pośrednie (indirect injection – poprzez złośliwą zawartość w dokumentach, wiadomościach e-mail lub wynikach działania narzędzi, które agent analizuje).

  Skuteczność tych ataków zależy od scenariusza. Wskaźniki powodzenia dla wiodących modeli w ogólnych testach użycia narzędzi i pisania kodu wahają się od ~0,5% do 8,5%. Jednak w środowiskach wysokiego ryzyka (ataki adaptacyjne na agentów kodujących AI, podatna na ataki orkiestracja) skuteczność ataków sięga nawet ~84%. Przykładem podatności wykrytej w systemach produkcyjnych jest EchoLeak (CVE-2025-32711, CVSS 9.3) – luka w zabezpieczeniach Microsoft 365 Copilot umożliwiająca bezklikową eksfiltrację danych, wywoływaną przez spreparowaną wiadomość e-mail.

  Środki zaradcze: traktuj wszystkie dane wejściowe jako potencjalnie niebezpieczne na każdym etapie pętli agenta; waliduj i oczyszczaj parametry przekazywane do narzędzi; izoluj dane zwracane przez narzędzia od systemowego promptu; stosuj wzorzec Plan-Verify-Execute (PVE), w którym agent najpierw generuje plan działania, a przed wykonaniem każdej operacji weryfikuje ją pod kątem zgodności z pierwotnym planem (co uniemożliwia wstrzyknięcie nowych, nieautoryzowanych akcji za pośrednictwem wyników z narzędzi); wymagaj potwierdzenia użytkownika (human-in-the-loop) dla akcji krytycznych; nadaj narzędziom minimalne niezbędne uprawnienia.

  Należy pamiętać, że sam prompt engineering nie gwarantuje pełnego bezpieczeństwa. Konieczne jest wdrożenie zewnętrznych warstw ochronnych (guardrails w środowisku wykonawczym, walidacja parametrów z użyciem list dozwolonych wpisów, detekcja anomalii semantycznych).
- **Dryfowanie agenta (Context/Scope drift):** Agent zbacza z głównego celu, ponieważ wywołane narzędzie zwróciło nadmiarowe lub niezwiązane bezpośrednio informacje. Środki zaradcze: precyzyjne i wąskie definicje interfejsów narzędzi; dbanie o to, by prompt systemowy jasno precyzował cel; wdrożenie automatycznych testów wykrywających gubienie wątku przez agenta.
- **Nieskończone pętle (Infinite loops):** Agent w kółko wywołuje to samo narzędzie z tymi samymi parametrami. Środki zaradcze: sztywny limit kroków (max_steps), deduplikacja wywołań oraz okresowe weryfikowanie przez model, czy wykonywane akcje rzeczywiście przybliżają go do celu.
- **Przepełnienie okna kontekstowego:** Długa konwersacja powoduje utratę najwcześniejszych wypowiedzi. Środki zaradcze: automatyczne podsumowywanie historii konwersacji, wyszukiwanie semantyczne w historii (archived turns) lub stosowanie modeli o bardzo długim oknie kontekstowym.

## Zapisywanie szablonu

Zapisz jako `outputs/skill-chatbot-architect.md`:

```markdown
---
name: chatbot-architect
description: Zaprojektuj architekturę chatbota dla wybranego scenariusza użycia.
version: 1.0.0
phase: 5
lesson: 17
tags: [nlp, agents, chatbot]
---

Na podstawie kontekstu produktowego (potrzeby użytkownika, ograniczenia prawne/zgodności, dostępne narzędzia, wolumen danych) wygeneruj:

1. Architektura: Regułowa, oparta na wyszukiwaniu, neuronowa, agent LLM lub hybrydowa (ze wskazaniem ścieżek obsługi).
2. Wybór LLM (jeśli dotyczy): Wskaż rodzinę modeli (Claude, GPT, Llama, Mixtral) dopasowaną do wymagań jakościowych (tool-use) oraz budżetu.
3. Strategia osadzania kontekstowego (Grounding): Źródła danych dla RAG, metoda wyszukiwania oraz interfejsy narzędzi.
4. Plan ewaluacji: Wskaźnik sukcesu zadań (task success rate), poprawność wywołań narzędzi, odsetek zboczenia z tematu, poziom halucynacji na wydzielonym zbiorze dialogów testowych.

Nigdy nie rekomenduj agenta opartego wyłącznie na modelu LLM do wykonywania operacji krytycznych (płatności, usuwanie konta, modyfikacja danych) bez wdrożenia ustrukturyzowanego procesu potwierdzeń. Bezwzględnie wymagaj audytu bezpieczeństwa pod kątem podatności na Prompt Injection, jeśli agent posiada uprawnienia do zapisu.
```

## Ćwiczenia praktyczne

1. **Poziom łatwy:** Zaimplementuj opisany powyżej system regułowy z 10 wzorcami (regex) dla chatbota obsługującego zamówienia w kawiarni. Uwzględnij przypadki brzegowe: modyfikacje zamówień, anulowanie oraz niejednoznaczne intencje użytkownika.
2. **Poziom średni:** Stwórz hybrydowy system FAQ + wsparcie LLM. Przygotuj bazę 50 pytań i odpowiedzi (FAQ) dla produktu SaaS, a w przypadku braku dopasowania przekieruj zapytanie do modelu LLM korzystającego z RAG opartego na dokumentacji. Przetestuj system na 100 rzeczywistych zapytaniach i zmierz odsetek odmów (rejection rate) oraz poprawność odpowiedzi.
3. **Poziom trudny:** Zaimplementuj opisaną wyżej pętlę agenta wyposażonego w trzy narzędzia (wyszukiwanie informacji, odczyt profilu użytkownika, wysyłanie e-maili). Przeprowadź ewaluację na 50 scenariuszach testowych, w tym próbach ataków Prompt Injection. Zgłoś odsetek zadań niedokończonych, popełnionych błędów oraz udanych ataków wstrzyknięcia instrukcji.

## Kluczowe pojęcia

| Termin | Potoczne określenie | Znaczenie precyzyjne |
|------|-----------------|----------------------|
| Intencja (Intent) | Czego chce użytkownik | Etykieta kategoryzująca intencję użytkownika (np. book_flight, reset_password). Służy do kierowania rozmowy do odpowiedniego modułu. |
| Szczelina (Slot) | Brakująca informacja | Konkretny parametr wymagany do wykonania akcji (np. data, cel podróży). Proces zbierania tych danych to slot-filling (wypełnianie szczelin). |
| RAG | Retrieval-Augmented Generation | Pobranie powiązanych dokumentów z bazy wiedzy w celu ugruntowania odpowiedzi generowanej przez model LLM. |
| Wywołanie narzędzia | Wywołanie funkcji (Tool/Function call) | Model generuje ustrukturyzowany obiekt (np. JSON) zawierający nazwę funkcji oraz jej parametry. Środowisko uruchomieniowe wykonuje kod i zwraca wynik z powrotem do modelu. |
| Pętla agenta | Pętla agenta (Agent loop) | Pętla sterująca pracą LLM, która naprzemiennie wywołuje model i zewnętrzne narzędzia, aż do momentu realizacji zadania. |
| Prompt Injection | Wstrzykiwanie instrukcji | Złośliwe dane wejściowe mające na celu nadpisanie lub obejście systemowych instrukcji modelu. |

## Literatura uzupełniająca

- [Weizenbaum (1966). ELIZA – a computer program for the study of natural language communication between man and machine](https://web.stanford.edu/class/cs124/p36-weizenabaum.pdf) — oryginalna publikacja dotycząca chatbota opartego na regułach.
- [Thoppilan i in. (2022). LaMDA: Language Models for Dialog Applications](https://arxiv.org/abs/2201.08239) — publikacja Google prezentująca możliwości neuronowych chatbotów tuż przed upowszechnieniem podejścia agentowego.
- [Yao i in. (2022). ReAct: Synergizing Reasoning and Acting in Language Models](https://arxiv.org/abs/2210.03629) — kluczowa praca naukowa wprowadzająca wzorzec pętli agentowej ReAct.
- [Przewodnik firmy Anthropic: Building effective agents](https://www.anthropic.com/research/building-effective-agents) — wytyczne i najlepsze praktyki budowy systemów agentowych.
- [Greshake i in. (2023). Not what you've signed up for: Compromising Real-World LLM-Integrated Applications with Indirect Prompt Injection](https://arxiv.org/abs/2302.12173) — pionierska publikacja dotycząca podatności na pośrednie wstrzykiwanie instrukcji (indirect prompt injection).
- [OWASP Top 10 for LLM Applications 2025 – LLM01: Prompt Injection](https://genai.owasp.org/llmrisk/llm01-prompt-injection/) — oficjalna dokumentacja najpopularniejszych zagrożeń bezpieczeństwa dla aplikacji LLM.
- [AWS Guide: Securing Amazon Bedrock agents against indirect prompt injections](https://aws.amazon.com/blogs/machine-learning/securing-amazon-bedrock-agents-a-guide-to-safeguarding-against-indirect-prompt-injections/) — praktyczne metody zabezpieczania agentów w chmurze, w tym architektura Plan-Verify-Execute.
- [EchoLeak (CVE-2025-32711) – analiza luki bezpieczeństwa](https://www.vectra.ai/topics/prompt-injection) — studium przypadku ukazujące ryzyko bezklikowej eksfiltracji danych z asystentów AI i pokazujące konieczność stosowania barier w środowisku wykonawczym.
