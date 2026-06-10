---

name: codebase-rag
description: Zbuduj system wyszukiwania semantycznego obejmujący wiele repozytoriów z fragmentacją uwzględniającą AST, wyszukiwaniem hybrydowym, przyrostowym ponownym indeksowaniem i cytowanymi odpowiedziami.
version: 1.0.0
phase: 19
lesson: 02
tags: [capstone, rag, code-search, tree-sitter, qdrant, bm25, hybrid-retrieval]

---

Biorąc pod uwagę ponad 10 repozytoriów zawierających w sumie co najmniej 2 miliony linii kodu, zbuduj potok pozyskiwania, indeks hybrydowy i agent zapytań wymuszanych cytowaniami, który odpowiada na pytania dotyczące wielu repozytoriów za pomocą weryfikowalnych kotwic plik:linia.

Plan budowy:

1. Przeanalizuj każdy plik za pomocą narzędzia Tree-Sitter. Fragment na granicach węzłów funkcji i klas. Przechowuj `{repo, path, start_line, end_line, symbol, body}`.
2. Podsumuj każdy fragment za pomocą Claude Haiku 4.5 lub Gemini 2.5 Flash, korzystając z podpowiedzi systemowych buforowanych w pamięci podręcznej. Zapisz jednozdaniowe podsumowanie obok fragmentu.
3. Indeksuj trzy struktury: Qdrant (gęsty, Voyage-code-3 lub nomic-embed-code), Tantivy (BM25 z wagami pól) i kuzu (krawędzie wykresu symboli dla importu, wywołań, dziedziczenia).
4. Zbuduj agenta zapytań LangGraph z trzema węzłami: pobieranie (gęsty równoległy BM25), rerank (Cohere rerank-3 lub bge-reranker-v2-gemma-2b), syntezator (Claude Sonnet 4.7 z szybkim buforowaniem i wymogiem cytowania pliku:linii).
5. Filtr końcowy: odrzuć wszelkie roszczenia bez weryfikowalnej kotwicy `(repo/path:start-end)`; zapytaj ponownie lub odpuść.
6. Podłącz webhook git push, który oblicza różnicę na poziomie symboli i ponownie osadza tylko zmienione fragmenty. Cel: zatwierdzenie 50 plików z możliwością przeszukiwania w wieku poniżej 60 lat we flocie 2M-LOC.
7. Oceń za pomocą zestawu 100 pytań. Zgłoś MRR@10, nDCG@10, wierność cytowań i percentyle opóźnień.
8. Uruchom cotygodniowe zadanie dryfu, które ponownie wykona ocenę i alerty w przypadku spadku MRR@10 > 5%.

Rubryka oceny:

| Waga | Kryterium | Pomiar |
|:-:|---|---|
| 25 | Jakość wyszukiwania | MRR@10 i nDCG@10 w zestawie 100 pytań wstrzymanych |
| 20 | Wierność cytatów | Część żądań odpowiedzi z weryfikowalnymi plikami:kotwice linii |
| 20 | Opóźnienie i skala | opóźnienie zapytania p95 przy 10 tys. QPS w indeksowanym rozmiarze korpusu |
| 20 | Poprawność indeksowania przyrostowego | Czas od git push do możliwości przeszukiwania w przypadku zatwierdzenia 50 plików |
| 15 | UX i formatowanie odpowiedzi | Klikalność cytatów, podgląd fragmentów, afordancja kontynuacji |

Twarde odrzucenia:

— Porcjowanie tokenów o stałym rozmiarze zamiast fragmentowania uwzględniającego AST. Zatruwa korpusy zawierające duży kod.
- Pobieranie tylko cosinusów bez BM25 lub zmiany rankingu. Znane jest niepowodzenie w przypadku zapytań o dokładną nazwę symbolu.
- Odpowiedzi bez obowiązkowych cytatów w pliku:linia.
- Ponowne osadzanie całego korpusu przy każdym wypchnięciu git; musi być przyrostowe.

Zasady odmowy:

- Odmawiaj indeksowania repozytoriów bez przeczytania licencji. Niektóre zabraniają osadzania w zewnętrznych sklepach wektorowych.
- Odmawiaj odpowiadania na zapytania, które rzekomo cytują pliki, których indeks nigdy nie widział; zawsze sprawdzaj kotwicę przed powrotem.
- Odmówić udzielenia odpowiedzi na p95 powyżej 4s; zamiast tego zwróć częściowy wynik z uchwytem uzupełniającym.

Dane wyjściowe: repozytorium zawierające potok pozyskiwania, agent zapytań LangGraph, zestaw eval zawierający 100 pytań, link do pulpitu nawigacyjnego Langfuse oraz opis trzech naprawionych trybów niepowodzeń pobierania (zatruwanie wygenerowanego kodu, przywoływanie symboli z długim ogonem, rozpoznawanie symboli między repo) i dokładną zmianę, która naprawiła każdy z nich.