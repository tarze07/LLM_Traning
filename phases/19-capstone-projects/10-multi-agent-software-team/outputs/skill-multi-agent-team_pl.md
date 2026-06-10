---

name: multi-agent-team
description: Zbuduj wieloagentowy zespół programistów składający się z architekta, programistów równoległych, recenzenta i testera; zmierzyć się z SWE-bench Pro i sporządzić sekcję zwłok.
version: 1.0.0
phase: 19
lesson: 10
tags: [capstone, multi-agent, swe-bench, langgraph, a2a, worktree, roles]

---

Biorąc pod uwagę adres URL problemu w GitHub i poziom równoległości, wdróż wieloagentowy zespół programistów, który stworzy PR gotowy do scalania. Oceń 50 problemów w SWE-bench Pro i opublikuj histogram niepowodzeń przekazania.

Plan budowy:

1. Tablica zadań: magazyn wpisanych wiadomości w formacie JSONL oparty na plikach (lub Redis). Rodzaje wiadomości: żądanie planu, podzadanie, diff_ready, recenzja_potrzebna, opinia_zwrotna, zatwierdzona, test_needed, test_passed, test_nieudany, replan_needed.
2. Architekt (Opus 4.7): czyta problem, pisze plan, emituje DAG podzadań z jawnymi interfejsami (dotknięte pliki, funkcje publiczne, wpływ testu).
3. Kodery N (Sonnet 4.7): każdy przejmuje podzadanie, tworzy nową piaskownicę `git worktree add` + Daytona, implementuje niezależnie.
4. Koordynator ds. łączenia: połączenie trójstronne; Rozwiązywanie konfliktów za pośrednictwem LLM tylko w przypadku nakładania się na poziomie plików.
5. Recenzent (GPT-5.4): odczytuje scalone różnice; nie może zatwierdzić różnic, których jest autorem; wysyła zatwierdzoną informację zwrotną lub opinię_recenzyjną kierowaną do odpowiedniego programisty.
6. Tester (Gemini 2.5 Pro): uruchamia zestaw testów w czystej piaskownicy; emituje test_passed lub test_failed z artefaktami.
7. Rozliczenie przekazania: każdy komunikat między rolami staje się zakresem Langfuse'a z rozmiarem i modelem ładunku. Oblicz wzmocnienie tokena = total_tokens / single_agent_baseline_tokens.
8. Wprowadź sondę oczywistego błędu (10% uruchomień), aby zmierzyć odsetek błędnych zatwierdzeń recenzentów.
9. Uruchom na 50 wydaniach SWE-bench Pro; opublikuj pass@1, zegar ścienny a punkt odniesienia dla jednego agenta, podział tokenów na role, histogram niepowodzeń przekazania.

Rubryka oceny:

| Waga | Kryterium | Pomiar |
|:-:|---|---|
| 25 | SWE-bench Pro pass@1 | Karnet podzbioru 50 numerów @ 1 |
| 20 | Równoległe przyspieszenie | Zegar ścienny a punkt odniesienia dla jednego agenta |
| 20 | Jakość recenzji | Wskaźnik fałszywych zatwierdzeń w przypadku sondy zawierającej wstrzyknięty błąd |
| 20 | Wydajność tokena | Całkowita liczba tokenów na rozwiązany problem w porównaniu z pojedynczym agentem |
| 15 | Inżynieria koordynacji | Rozwiązywanie konfliktów scalania, histogram niepowodzenia przekazania |

Twarde odrzucenia:

- Recenzent, który może zatwierdzać różnice, których jest autorem lub który zaproponował. Twarde ograniczenie.
- Raporty bez dopasowanego przebiegu bazowego dla jednego agenta. Multiagent musi wygrywać *za dolara*, a nie tylko pass@1.
- Tablice zadań, na których wiadomości mają postać dowolnych ciągów znaków, a nie wpisanych wiadomości A2A.
- Łącz koordynatorów, którzy po cichu porzucają sprzeczne różnice, zamiast odsyłać do ponownego planu.

Zasady odmowy:

- Odmów uruchomienia bez pułapów budżetowych na rolę (token + dolar).
- Odmów otwarcia PR, którego tester nie zweryfikował w czystej piaskownicy.
- Odmawiaj skalowania koderów powyżej 8 w jednym przebiegu. Nad tym dominuje narzut koordynacyjny.

Dane wyjściowe: repozytorium zawierające tablicę zadań + pracowników ról, dziennik uruchomień SWE-bench Pro zawierający 50 problemów, dopasowany przebieg bazowy dla jednego agenta, pulpit nawigacyjny Langfuse z zakresami z tagami ról i podziałami tokenów na role, raport z sondy wstrzykniętych błędów oraz sekcja zwłok wymieniająca trzy przekazania, które najczęściej się psuły, oraz schemat komunikatu lub monitującą zmianę, która spowodowała zmniejszenie każdego z nich.