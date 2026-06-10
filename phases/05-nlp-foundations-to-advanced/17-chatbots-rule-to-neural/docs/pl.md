# Chatboty — oparte na regułach, od neuronowych do agentów LLM

> ELIZA odpowiedziała, podając pasujące wzorce. Intencje zmapowane w DialogFlow. GPT odpowiedział na podstawie wag. Claude uruchamia narzędzia i weryfikuje. Każda era rozwiązała najgorszą porażkę poprzedniej.

**Typ:** Ucz się
**Języki:** Python
**Wymagania wstępne:** Faza 5 · 13 (odpowiadanie na pytania), faza 5 · 14 (wyszukiwanie informacji)
**Czas:** ~75 minut

## Problem

Użytkownik mówi: „Chcę zmienić swój lot”. System musi dowiedzieć się, czego chcą, jakich informacji brakuje, jak je zdobyć i jak zakończyć akcję. Następnie użytkownik mówi: „czekaj, a co jeśli zamiast tego anuluję?” a system musi zapamiętać kontekst, przełączać zadania i zachować stan.

Rozmowa jest trudna dla systemu ML. Dane wejściowe są otwarte. Sygnał wyjściowy musi być spójny na wielu zwojach. System może wymagać działania na świecie (zmiana lotu, obciążenie karty). Każdy zły krok jest widoczny dla użytkownika.

Architektury chatbotów przeszły przez cztery paradygmaty, każdy wprowadzony, ponieważ poprzedni zawiódł zbyt wyraźnie. Ta lekcja porządkuje je. Krajobraz produkcyjny na rok 2026 jest hybrydą dwóch ostatnich.

## Koncepcja

![Ewolucja Chatbota: oparta na regułach → pobieranie → neuronowa → agent](../assets/chatbot.svg)

**Oparte na regułach (ELIZA, AIML, DialogFlow).** Ręcznie opracowane wzorce dopasowują się do danych wejściowych użytkownika i generują odpowiedzi. Klasyfikatory intencji kierują do predefiniowanych przepływów. Maszyny stanu wypełniające szczeliny zbierają wymagane informacje. Działa znakomicie w wąskim zakresie, dla którego został zaprojektowany. Zawodzi natychmiast poza nim. Nadal wysyłamy w obszarach o krytycznym znaczeniu dla bezpieczeństwa (uwierzytelnianie bankowe, rezerwacje linii lotniczych), gdzie halucynacje nie są tolerowane.

**Oparty na wyszukiwaniu.** System przypominający często zadawane pytania. Zakoduj każdą parę (wypowiedź, odpowiedź). W czasie wykonywania zakoduj wiadomość użytkownika i pobierz najbliższą zapisaną odpowiedź. Pomyśl o klasycznej funkcji „podobnych artykułów” Zendeska. Lepiej radzi sobie z parafrazami niż z regułami. Żadnego pokolenia, więc nie ma halucynacji.

**Neural (seq2seq).** Koder-dekoder przeszkolony na podstawie dzienników rozmów. Generuje odpowiedzi od zera. Płynny, ale podatny na ogólnikowe wnioski („nie wiem”) i dryfowanie rzeczowe. Nigdy rzetelnie na temat. Powód, dla którego Google, Facebook i Microsoft miały rozczarowujące chatboty w latach 2016–2019.

**Agenci LLM.** Model językowy zamknięty w pętli, która planuje, wywołuje narzędzia i weryfikuje wyniki. To nie jest chatbot z długim monitem. Pętla agenta: planuj → narzędzie wywołujące → obserwuj wynik → zdecyduj o kolejnym kroku. Uziemienie w pierwszej kolejności odzyskanie (RAG) chroni go przed halucynacjami. Wywołania narzędzi pozwalają mu faktycznie robić różne rzeczy. To jest architektura 2026.

Cztery paradygmaty nie są zamiennikami sekwencyjnymi. Produkcyjny chatbot na rok 2026 obsługuje wszystkie cztery opcje: oparty na regułach do uwierzytelniania i destrukcyjnych działań, wyszukiwanie często zadawanych pytań, generowanie neuronów do naturalnego frazowania, agent LLM do niejednoznacznych zapytań otwartych.

## Zbuduj to

### Krok 1: dopasowywanie wzorców w oparciu o reguły

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

ELIZA w 20 linijkach. Sztuczka z refleksją („Czuję się smutny” → „Dlaczego czujesz się smutny”) to kanoniczne demo psychoterapeuty z Weizenbauma z 1966 r. Wciąż pouczające.

### Krok 2: w oparciu o wyszukiwanie (FAQ)

Ten ilustracyjny fragment wymaga `pip install sentence-transformers` (który wciąga latarkę). Uruchamialny `code/main.py` w tej lekcji wykorzystuje zamiast tego podobieństwo Jaccarda stdlib, więc lekcja przebiega bez zewnętrznych zależności.

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

Odmowa oparta na progach jest kluczowym wyborem projektowym. Jeśli najlepsze dopasowanie nie jest wystarczająco bliskie, zwróć `None` i pozwól systemowi eskalować.

### Krok 3: generowanie neuronów (wartość bazowa)

Użyj małego, dostrojonego do instrukcji kodera-dekodera (FLAN-T5) lub precyzyjnie dostrojonego modelu konwersacyjnego. Produkcja sama w sobie nie nadaje się do użytku w 2026 r. (sprzeczność, odejście od tematu, bzdury oparte na faktach), ale jest dostarczana w systemach hybrydowych w celu zapewnienia naturalnego frazowania. Modele wyposażone wyłącznie w dekoder w stylu DialoGPT wymagają wyraźnych separatorów skrętów i obsługi EOS, aby uzyskać spójne odpowiedzi; potok tekst2tekstowy FLAN-T5 działa od razu w celach dydaktycznych.

```python
from transformers import pipeline

chatbot = pipeline("text2text-generation", model="google/flan-t5-small")

response = chatbot("Respond politely to: Hi there!", max_new_tokens=40)
print(response[0]["generated_text"])
```

### Krok 4: Pętla agenta LLM

Kształt produkcji na rok 2026:

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

Trzy rzeczy do nazwania. Narzędzia to wywoływalne funkcje, które LLM może wywołać. Pętla kończy się, gdy LLM zwróci ostateczną odpowiedź zamiast wywołania narzędzia. Budżet kroków zapobiega nieskończonym pętlom w przypadku niejednoznacznych zadań.

Prawdziwa produkcja dodaje: uziemienie oparte na pobieraniu (wstrzyknięcie odpowiednich dokumentów przed każdym wywołaniem LLM), poręcze (odmawianie destrukcyjnych działań bez potwierdzenia), obserwowalność (rejestrowanie każdego kroku) i oceny (automatyczne sprawdzanie, czy zachowanie agenta pozostaje zgodne ze specyfikacją).

### Krok 5: routing hybrydowy

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

Wzór: deterministyczne reguły dla wszystkiego, co destrukcyjne, wyszukiwanie gotowych często zadawanych pytań, agenci LLM dla wszystkiego innego. To właśnie będzie dostarczane w systemach obsługi klienta w 2026 roku.

## Użyj tego

Stos na rok 2026:

| Przypadek użycia | Architektura |
|--------|--------------|
| Rezerwacja, płatność, uwierzytelnienie | Maszyny stanowe oparte na regułach + wypełnianie slotów |
| Często zadawane pytania dotyczące obsługi klienta | Pobieranie wybranych odpowiedzi |
| Otwarty czat pomocy | Agent LLM z RAG + wywołaniami narzędzi |
| Narzędzia wewnętrzne / Asystenci IDE | Agent LLM z wywołaniami narzędzi (wyszukiwanie, odczyt, zapis) |
| Chatboty towarzyszące/postaciowe | Dostrojony LLM z monitem systemu persona, odzyskiwanie wiedzy |

Zawsze używaj routingu hybrydowego w środowisku produkcyjnym. Żadna pojedyncza architektura nie obsługuje dobrze każdego żądania. Sama warstwa routingu jest zazwyczaj klasyfikatorem o małej intencji.

## Tryby awarii, które nadal są dostarczane

- **Pewna fabrykacja.** Agent LLM twierdzi, że wykonał czynność, której nie wykonał. Łagodzenie: weryfikuj wyniki, rejestruj wywołania narzędzi, nigdy nie pozwól, aby LLM twierdził, że coś zrobił bez pomyślnego zwrotu narzędzia.
- **Wstrzyknięcie podpowiedzi.** Użytkownik wstawia tekst, który zastępuje zachętę systemową. Miejsce LLM01 na liście 10 najlepszych aplikacji OWASP dla aplikacji LLM 2025. Dwie wersje: wtrysk bezpośredni (wklejony do czatu) i wtrysk pośredni (ukryty w dokumentach, e-mailach lub wynikach narzędzi czytanych przez agenta).

  Wskaźniki ataków różnią się w zależności od scenariusza. Zmierzone wskaźniki powodzenia wahają się od ~0,5 do 8,5% w przypadku modeli pionierskich w ogólnych testach porównawczych użycia narzędzi i kodowania. Konkretne konfiguracje wysokiego ryzyka (ataki adaptacyjne na agentów kodujących AI, podatna na ataki orkiestracja) osiągnęły ~84%. Produkcyjne CVE obejmują EchoLeak (CVE-2025-32711, CVSS 9.3) — lukę polegającą na wydobywaniu danych bez kliknięcia w Microsoft 365 Copilot wywoływaną przez wiadomość e-mail kontrolowaną przez osobę atakującą.

  Środki zaradcze: traktuj dane wejściowe użytkownika jako niezaufane w całej pętli; odkażać przed wywołaniem narzędzia; izolować wyniki narzędzia od głównego monitu; użyj wzorca Plan-Verify-Execute (PVE), w którym agent najpierw planuje, a następnie weryfikuje każdą akcję względem planu przed wykonaniem (powstrzymuje to wstrzykiwanie przez narzędzie nowych, nieplanowanych akcji); wymagać potwierdzenia użytkownika w przypadku destrukcyjnych działań; zastosuj najniższe uprawnienia do zakresów narzędzi.

  Żadna ilość szybkich prac inżynieryjnych nie eliminuje w pełni tego ryzyka. Wymagane są zewnętrzne warstwy ochrony środowiska wykonawczego (ochrona LLM, weryfikacja listy dozwolonych, wykrywanie anomalii semantycznych).
- **Przesunięcie zakresu.** Agent wypada z zadania, ponieważ wywołanie narzędzia zwróciło powiązane informacje. Łagodzenie: wąskie kontrakty na narzędzia; utrzymuj skupienie monitu systemowego; dodaj oceny dla stawki poza zadaniem.
- **Nieskończone pętle.** Agent ciągle wywołuje to samo narzędzie. Łagodzenie: budżet krokowy, deduplikacja wywołań narzędzi, ocena LLM na temat „czy robimy postęp”.
- **Wyczerpanie okna kontekstowego.** Długie rozmowy wytrącają najwcześniejsze momenty z kontekstu. Łagodzenie: podsumuj starsze zwroty, wyszukaj odpowiednie przeszłe zwroty według podobieństwa lub użyj modelu o długim kontekście.

## Wyślij to

Zapisz jako `outputs/skill-chatbot-architect.md`:

```markdown
---
name: chatbot-architect
description: Design a chatbot stack for a given use case.
version: 1.0.0
phase: 5
lesson: 17
tags: [nlp, agents, chatbot]
---

Given a product context (user need, compliance constraints, available tools, data volume), output:

1. Architecture. Rule-based, retrieval, neural, LLM agent, or hybrid (specify which paths go where).
2. LLM choice if applicable. Name the model family (Claude, GPT-4, Llama-3.1, Mixtral). Match to tool-use quality and cost.
3. Grounding strategy. RAG sources, retrieval method (see lesson 14), tool contracts.
4. Evaluation plan. Task success rate, tool-call correctness, off-task rate, hallucination rate on held-out dialogs.

Refuse to recommend a pure-LLM agent for any destructive action (payments, account deletion, data modification) without a structured confirmation flow. Refuse to skip the prompt-injection audit if the agent has write access to anything.
```

## Ćwiczenia

1. **Łatwe.** Zaimplementuj powyższą odpowiedź opartą na regułach z 10 wzorami dla bota zamawiającego w kawiarni. Przypadki testowe Edge: podwójne zamówienia, modyfikacje, anulowanie, niejasne intencje.
2. **Średni.** Stwórz hybrydowy FAQ + pomoc LLM. 50 wpisów w często zadawanych pytaniach dotyczących produktu SaaS, rezerwa LLM z możliwością pobierania za pośrednictwem witryny dokumentacji. Zmierz współczynnik odmów i dokładność na 100 prawdziwych pytaniach wsparcia.
3. **Trudne.** Zaimplementuj powyższą pętlę agenta za pomocą trzech narzędzi (wyszukiwanie, odczytywanie danych użytkownika, wysyłanie wiadomości e-mail). Przeprowadź ocenę z 50 scenariuszami testowymi, w tym szybkimi próbami wstrzyknięcia. Zgłaszaj odsetek niewykonanych zadań, odsetek nieudanych zadań i wszelkie sukcesy wstrzyknięć.

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|-----------------|----------------------|
| Zamiar | Czego chce użytkownik | Etykieta kategoryczna (book_flight, reset_password). Skierowany do opiekuna. |
| Gniazdo | Informacja | Parametr, którego potrzebuje bot (data, miejsce docelowe). Wypełnianie slotów to sekwencja zapytań. |
| SZARA | Odzyskiwanie plus generowanie | Uzyskaj odpowiednie dokumenty, a następnie ugruntuj odpowiedź LLM. |
| Wywołanie narzędzia | Wywołanie funkcji | LLM emituje wywołanie strukturalne z nazwą + argumentami. Środowisko wykonawcze wykonuje się, zwraca wynik. |
| Pętla agenta | Planuj, działaj, sprawdzaj | Kontroler uruchamiający wywołania LLM przeplatane wywołaniami narzędzi do momentu zakończenia zadania. |
| Szybki zastrzyk | Komunikat o atakach użytkowników | Złośliwe dane wejściowe próbujące zastąpić monit systemowy. |

## Dalsze czytanie

- [Weizenbauma (1966). ELIZA — program komputerowy do badania komunikacji w języku naturalnym] (https://web.stanford.edu/class/cs124/p36-weizenabaum.pdf) — oryginalny dokument dotyczący chatbota opartego na regułach.
- [Thoppilan i in. (2022). LaMDA: Modele językowe dla aplikacji dialogowych](https://arxiv.org/abs/2201.08239) — publikacja Google z późnego okresu przed przejęciem pracy przez agentów LLM na temat neuronowych chatbotów.
- [Yao i in. (2022). ReAct: Synergizing Reasoning and Acting in Language Models](https://arxiv.org/abs/2210.03629) — artykuł, w którym nazwano wzorzec pętli agenta.
– [Przewodnik firmy Anthropic na temat budowania skutecznych agentów](https://www.anthropic.com/research/building-efektyw-agents) – wytyczne dotyczące produkcji na 2024 r., które nadal obowiązują w 2026 r.
- [Greshake i in. (2023). Nie to, na co się zapisałeś: naruszanie rzeczywistych aplikacji zintegrowanych z LLM za pomocą pośredniego wstrzykiwania podpowiedzi](https://arxiv.org/abs/2302.12173) — dokument dotyczący szybkiego wstrzykiwania.
- [10 najlepszych aplikacji OWASP dla aplikacji LLM 2025 — LLM01 Prompt Injection](https://genai.owasp.org/llmrisk/llm01-prompt-injection/) — ranking, w którym szybkie wstrzyknięcie stało się najważniejszym problemem związanym z bezpieczeństwem.
- [AWS — Zabezpieczanie agentów Amazon Bedrock przed pośrednimi zastrzykami monitującymi] (https://aws.amazon.com/blogs/machine-learning/securing-amazon-bedrock-agents-a-guide-to-safeguarding-against-indirect-prompt-injections/) — praktyczne zabezpieczenia warstwy orkiestracji, w tym przepływy Plan-Verify-Execute i potwierdzenia użytkownika.
– [EchoLeak (CVE-2025-32711)](https://www.vectra.ai/topics/prompt-injection) — kanoniczny CVE do ekstrakcji danych bez kliknięcia z pośredniego natychmiastowego wstrzyknięcia. Przypadek referencyjny pokazujący, dlaczego agenci dostępu do zapisu potrzebują zabezpieczeń w czasie wykonywania.