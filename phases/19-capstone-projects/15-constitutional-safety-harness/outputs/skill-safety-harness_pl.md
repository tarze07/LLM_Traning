---

name: safety-harness
description: Połącz warstwowy rurociąg bezpieczeństwa wokół docelowej aplikacji LLM, uruchom sześciorodzinny zespół czerwonych drużyn i przeprowadź samokrytykę dotyczącą konstytucji w celu uzyskania mierzalnej delty nieszkodliwości.
version: 1.0.0
phase: 19
lesson: 15
tags: [capstone, safety, red-team, llama-guard, x-guard, garak, pyrit, constitutional-ai]

---

Biorąc pod uwagę docelową aplikację LLM (model dostrojony do instrukcji 8B lub chatbot RAG), wzmocnij ją za pomocą warstwowego potoku bezpieczeństwa i przeprowadź autonomiczny zasięg czerwonej drużyny w sześciu rodzinach ataków. Sporządź raport nieszkodliwości przed/po.

Plan budowy:

1. Potok pięciowarstwowy: oczyszczanie danych wejściowych (pasek o zerowej szerokości, dekodowanie kodowania, normalizacja Unicode) -> szyny NeMo Guardrails v0.12 -> bramka klasyfikatora (Llama Guard 4 / X-Guard / ShieldGemma-2 / Nemotron 3) -> docelowy LLM -> filtr wyjściowy (Llama Guard 4 + Presidio PII + kontrola cytowań). Oznaczone wyjścia trafiają do kolejki Slack HITL.
2. Emituj zakres Langfuse na warstwę, aby atrybucja była widoczna od końca do końca.
3. Harmonogram zespołu czerwonego obsługujący garak, PyRIT, PAIR, TAP, GCG, wieloobrotową personę i wielojęzyczne ataki typu code-switch na cron.
4. Każde udane jailbreak: wynik CVSS 4.0, reprodukcja, plan łagodzenia, harmonogram ujawnienia.
5. Sonda XSTest z łagodnym monitem, działająca w sposób ciągły w celu wykrycia regresji nadmiernej odmowy.
6. Przebieg samokrytyki konstytucyjnej: 1 tys. podpowiedzi dotyczących szkodliwych prób -> docelowe wersje robocze -> wyniki krytyków w stosunku do pisemnej konstytucji -> przepisane pary -> SFT. Zmierz przed/po przetrzymanej ocenie nieszkodliwości.
7. Alerty: Ostrzeżenie o Slacku w przypadku łagodnej regresji, PagerDuty krytyczny w przypadku nowej rodziny jailbreaków.

Rubryka oceny:

| Waga | Kryterium | Pomiar |
|:-:|---|---|
| 25 | Pokrycie powierzchni ataku | Przećwiczono ponad 6 rodzin ataków, ponad 2 języki |
| 20 | Kompromis prawdziwie pozytywny/fałszywie pozytywny | Współczynnik blokowania ataków vs współczynnik łagodnych przejść testu XST |
| 20 | Delta samokrytyki | Przed/po nieszkodliwości na odłożonej ewaluacji |
| 20 | Dokumentacja i ujawnianie | Wyniki punktacji CVSS z osią czasu |
| 15 | Automatyzacja i powtarzalność | Oparty na Cron, alerty wykonywane od początku do końca |

Twarde odrzucenia:

- Jednowarstwowe stosy bezpieczeństwa. Tezą tego zwieńczenia jest głęboka obrona.
- Biegi zespołu czerwonego, które zgłaszają wskaźnik powodzenia bez liczb nadmiernych odmów XSTest.
- Konstytucyjna samokrytyka bez wyczekiwanej oceny (podaje dokładność zbioru uczącego, a nie uogólnienie).
— Brak punktacji CVSS w wynikach jailbreak.

Zasady odmowy:

- Odmów podania numeru bezpieczeństwa bez łagodnego kontrapunktu w postaci sondy. Jedno bez drugiego wprowadza w błąd.
- Odmawiaj automatycznego przeszkolenia w przypadku sukcesów drużyny czerwonej bez ludzkiej kontroli par krytykujących.
- Odmów ubiegania się o wielojęzyczną ochronę bez uruchomienia X-Guard w co najmniej dwóch językach innych niż angielski.

Dane wyjściowe: repozytorium zawierające pięciowarstwowy potok, harmonogram czerwonego zespołu, biegacze PAIR/TAP/GCG, zestaw szkoleniowy do samokrytyki zgodnie z konstytucją, panel kontrolny XSTest dotyczący nadmiernych odmów, narzędzie do śledzenia ustaleń CVSS oraz opis wymieniający trzy rodziny ataków, które miały najwyższy współczynnik powodzenia wstępnego utwardzania i konkretną warstwę potoku, która łagodziła każdą z nich.