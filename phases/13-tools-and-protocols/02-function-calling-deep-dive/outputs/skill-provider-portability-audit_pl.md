---

name: provider-portability-audit
description: Przeprowadź inspekcję integracji wywołań funkcji z jednym dostawcą pod kątem uszkodzeń po przeniesieniu do pozostałych dwóch.
version: 1.0.0
phase: 13
lesson: 02
tags: [function-calling, openai, anthropic, gemini, portability]

---

Biorąc pod uwagę integrację wywołań funkcji u jednego dostawcy (OpenAI, Anthropic lub Gemini), przeprowadź audyt przenośności zawierający listę każdej zmiany nazwy pola, różnicy w zachowaniu i kolizji twardych limitów, która pojawia się, gdy ta sama logika jest dostarczana u pozostałych dwóch dostawców.

Wyprodukuj:

1. Różnica deklaracji Dla każdego narzędzia objętego integracją pokaż translację koperty/pola/schematu wymaganą dla każdego z dwóch pozostałych dostawców. Oznacz dowolną konstrukcję schematu JSON, której dostawca docelowy nie obsługuje (Gemini: podzbiór OpenAPI 3.0; ścisłe OpenAI: brak `$ref`, brak niejednoznacznego `oneOf`).
2. Różnica odpowiedzi Dokumentuj, gdzie znajduje się wywołanie narzędzia w kształcie odpowiedzi każdego dostawcy (blok `tool_calls[]` vs `content[]` vs wpis `parts[]`) i kto jest odpowiedzialny za analizowanie `arguments` (ciąg w OpenAI, obiekt w Anthropic i Gemini).
3. Różnica `tool_choice` Zamapuj bieżące ustawienie wyboru integracji (auto / zabroń / wymuś / wymagane) na kształt docelowego dostawcy; Oznacz brakujące tryby.
4. Ogranicz kolizje. Raportuj liczbę narzędzi (128/64/64), głębokość schematu (5/10/efektywnie nieograniczoną) i ograniczenia długości argumentów. Zwiększ poziom ważności bloków w przypadku każdej integracji, która przekracza limity docelowego dostawcy.
5. Mapowanie w trybie ścisłym. Określ, czy w obiekcie docelowym zachowana jest semantyka trybu ścisłego. OpenAI `strict: true` nie ma dokładnego odpowiednika w Anthropic; Gemini `responseSchema` jest przybliżony, ale jest na poziomie żądania.

Twarde odrzucenia:
- Dowolna integracja, która zakłada, że `arguments` jest ciągiem znaków w obiektach docelowych innych niż OpenAI. Po cichu przyniesie błędne wyniki.
- Dowolna integracja, której liczba narzędzi przekracza 64 podczas przenoszenia do Anthropic lub Gemini bez routera.
- Dowolna integracja wykorzystująca `$ref` w schemacie, gdy celem jest tryb ścisły OpenAI.

Zasady odmowy:
- Jeśli zostaniesz poproszony o przeniesienie integracji zależnej od funkcji specyficznej dla dostawcy, która nie ma analogii (np. zwroty stanowe API OpenAI Responses, blokady użytkowania komputera Anthropic), odmów i wyjaśnij, która funkcja nie ma docelowego odpowiednika.
- Jeśli zostaniesz poproszony o wybranie zwycięzcy, odmów. Wybór zależy od potrzeb hosta w zakresie trybu ścisłego, profilu kosztów i wymagań dotyczących połączeń równoległych.

Wynik: jednostronicowy audyt z tabelą różnic dla poszczególnych narzędzi, tabelą limitów i ostateczną „werdyktem portu” dla każdego dostawcy docelowego (statek / router potrzeb / funkcja zablokowana). Zakończ jednym zdaniem, wymieniając zmianę migracyjną o największym wpływie.