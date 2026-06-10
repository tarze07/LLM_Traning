---

name: consensus-designer
description: Zaprojektuj protokół konsensusu uwzględniający bizantyjską tolerancję błędów (BFT) dla systemów wieloagentowych. Określ zasady grupowania, ważenia głosów, progu akceptacji oraz eskalacji; przetestuj odporność projektu na ataki bizantyjskie, potakiwanie i monokulturę błędów.
version: 1.0.0
phase: 16
lesson: 14
tags: [multi-agent, consensus, BFT, voting, confidence]

---

Dla zespołu N agentów realizujących zadania wnioskowania, zaprojektuj protokół konsensusu odporny na trzy kluczowe typy zagrożeń specyficzne dla LLM: kłamstwo bizantyjskie, potakiwanie (sycophancy) oraz monokulturę skorelowanych błędów.

Opracuj:

1. **Strategia grupowania.** W jaki sposób grupowane są odpowiedzi? Do wyboru: kanonizacja tekstu (oczyszczanie ze znaków interpunkcyjnych, małe litery), analiza wektorowa (embeddings similarity) z określonym progiem odległości lub sztywna strukturyzacja danych (schemat JSON). Określ oczekiwaną dokładność klastrowania i dopuszczalne rozbieżności.
2. **Strategia wyznaczania wag.** Głosowanie większościowe (Majority Vote), ważone zaufaniem agentów (CP-WBFT), zależne od zaufania i jakości historycznej (WBFT) lub oparte na mediane geometrycznej ocen (DecentLLM). Uzasadnij wybór w kontekście profilu zagrożeń.
3. **Próg konsensusu.** Jaki ułamek łącznej wagi głosów jest wymagany do zaakceptowania wyniku? Określ procedurę na wypadek nieosiągnięcia progu: ponowna próba (retry), eskalacja (escalate) czy wstrzymanie się od decyzji.
4. **Zapewnienie różnorodności.** Jakie modele bazowe, warianty promptów oraz parametry temperatury zostaną zastosowane w zespole? Monokultura to zagrożenie, z którym klasyczne głosowanie większościowe sobie nie radzi — różnorodność modeli stanowi kluczowe zabezpieczenie systemowe.
5. **Niezależny weryfikator (Verifier).** Czy wdrożono agenta z dostępem wyłącznie do odczytu, który pobiera obiektywne dane (ground truth) lub stosuje sztywne reguły walidacji? Gdzie trafiają jego raporty? Weryfikator musi mieć zablokowaną możliwość wpływania na pulę głosów.
6. **Limit rund.** Maksymalna liczba rund przed podjęciem procedury eskalacji. Rekomenduje się limit 2-3 rund dla większości zadań; dłuższe dyskusje sprzyjają zachowaniom potakującym (konformizmowi).
7. **Macierz testów odporności.** Dla każdego scenariusza (bizantyjski, potakiwanie, monokultura) przedstaw oczekiwane zachowanie systemu oraz ryzyko szczątkowe. Jeśli protokół dopuszcza znany tryb awaryjny (fail-safe), opisz go krótko.

Kryteria wykluczające:

- Projekty, które opierają zespół agentów wyłącznie na jednym modelu bazowym (zagrożenie monokulturą).
- Dowolny projekt dopuszczający nieograniczoną liczbę rund dyskusji („dyskutujcie aż do porozumienia”), co promuje zachowania konformistyczne.
- Projekty, w których raporty weryfikatora są zapisywane z powrotem we wspólnej puli (ryzyko zatrucia weryfikatora).
- Twierdzenie, że mechanizm BFT rozwiązuje problem poprawności merytorycznej. BFT służy do uzgadniania wyników, a poprawność to osobna kwestia.

Zasady odmowy (Rejection rules):

- Jeśli zadanie nie posiada obiektywnej prawdy (pytania o opinie, synteza kreatywna), odrzuć klasyczny konsensus i zaleć model „agenty jako doradcy, decyzja po stronie człowieka”.
- Jeśli zespół składa się z mniej niż 3 agentów, odrzuć metodę konsensusu i zaleć architekturę z jednym agentem i niezależnym weryfikatorem.
- Jeśli wszystkie agenty korzystają z tego samego modelu bazowego i użytkownik nie może tego zmienić, wyraźnie oznacz maksymalny poziom dokładności (sufit) wynikający z ograniczeń monokultury.

Format wyjściowy: jednostronicowy opis projektu architektury. Rozpocznij od jednozdaniowego streszczenia (np. „Głosowanie ważone zaufaniem w zespole 5 agentów (3 modele bazowe), próg konsensusu semantycznego 0,55, niezależny weryfikator weryfikujący oryginalne źródła, maksymalnie 2 rundy”), a następnie przedstaw siedem opisanych wyżej sekcji. Zakończ macierzą testów odporności.
