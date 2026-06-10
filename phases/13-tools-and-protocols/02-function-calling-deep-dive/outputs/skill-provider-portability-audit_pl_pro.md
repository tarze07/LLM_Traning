---

name: provider-portability-audit
description: Przeprowadź audyt integracji wywołań funkcji u jednego dostawcy pod kątem problemów z kompatybilnością po przeniesieniu jej do pozostałych dwóch.
version: 1.0.0
phase: 13
lesson: 02
tags: [function-calling, openai, anthropic, gemini, portability]

---

Mając do dyspozycji integrację wywołań funkcji u jednego z dostawców (OpenAI, Anthropic lub Gemini), przeprowadź audyt przenośności. Wskaż wszelkie zmiany nazw pól, różnice w zachowaniu oraz konflikty z twardymi limitami, które pojawiają się przy wdrażaniu tej samej logiki u pozostałych dwóch dostawców.

Przygotuj:

1. Różnice w deklaracjach: Dla każdego narzędzia objętego integracją przedstaw mapowanie (translację) otoczki (envelope), pól i schematu wymagane przez pozostałych dwóch dostawców. Wskaż wszelkie konstrukcje schematu JSON, które nie są obsługiwane przez dostawcę docelowego (np. Gemini obsługuje jedynie podzbiór OpenAPI 3.0; OpenAI w trybie Strict nie pozwala na używanie `$ref` ani niejednoznacznego `oneOf`).
2. Różnice w odpowiedziach: Opisz, w którym miejscu struktury odpowiedzi danego dostawcy znajduje się wywołanie narzędzia (blok `tool_calls[]` vs `content[]` vs wpis `parts[]`) oraz który komponent odpowiada za parsowanie argumentów (`arguments` to ciąg znaków w OpenAI, a obiekt w Anthropic i Gemini).
3. Różnice w `tool_choice`: Przemapuj bieżące ustawienia wyboru narzędzi (auto / disabled / forced / required) na strukturę docelowego dostawcy. Wskaż ewentualne brakujące tryby.
4. Konflikty limitów: Zestaw limity dotyczące liczby narzędzi (128/64/64), głębokości schematu (5/10/brak limitu w praktyce) oraz ograniczenia długości argumentów. Podnieś poziom krytyczności dla każdej integracji, która przekracza limity dostawcy docelowego.
5. Mapowanie trybu ścisłego (Strict Mode): Określ, czy u docelowego dostawcy możliwe jest zachowanie semantyki trybu ścisłego. Funkcja `strict: true` z OpenAI nie ma bezpośredniego odpowiednika w Anthropic, natomiast w Gemini parametr `responseSchema` działa podobnie, lecz jest ustawiany na poziomie żądania.

Kryteria odrzucenia:
- Każda integracja, która zakłada, że `arguments` jest ciągiem znaków u dostawców innych niż OpenAI (może to prowadzić do niezgłaszanych błędów wykonania).
- Każda integracja, w której liczba narzędzi przekracza 64 podczas migracji do Anthropic lub Gemini bez użycia routera.
- Każda integracja wykorzystująca `$ref` w schemacie, gdy systemem docelowym jest OpenAI w trybie Strict.

Zasady odmowy wykonania zadania:
- Jeśli otrzymasz polecenie przeniesienia integracji zależnej od specyficznych funkcji dostawcy, które nie mają swoich odpowiedników (np. stanowe odpowiedzi w asystentach OpenAI, funkcja Computer Use w Anthropic), odmów wykonania zadania i wskaż brakującą funkcjonalność.
- W przypadku prośby o wskazanie „najlepszego” dostawcy, odmów wyboru. Ostateczna decyzja zależy od wymagań systemu dotyczących trybu ścisłego, budżetu oraz zapotrzebowania na równoległe wywoływanie funkcji.

Oczekiwany rezultat: Jednostronicowy raport z audytu zawierający tabelę różnic dla poszczególnych narzędzi, tabelę limitów oraz ostateczną ocenę wykonalności migracji („werdykt portu”) dla każdego docelowego dostawcy (wdrożenie bezpośrednie / wymagany router / zablokowane przez brak funkcji). Podsumuj całość jednym zdaniem, wskazując zmianę migracyjną o największym znaczeniu.
