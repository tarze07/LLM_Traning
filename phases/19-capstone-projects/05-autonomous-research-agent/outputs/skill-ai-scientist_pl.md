---

name: ai-scientist
description: Zbuduj autonomicznego agenta badawczego, który przeszukuje drzewo eksperymentów, pisze artykuły w LaTeX z krytyką wizji i przekazuje czerwony zespół uciekający z piaskownicy.
version: 1.0.0
phase: 19
lesson: 05
tags: [capstone, autonomous-agent, ai-scientist, sakana, langgraph, sandbox, research]

---

Mając pomysł na początek, wąską domenę i budżet obliczeniowy wynoszący 30 USD, zbuduj agenta, który przeszuka drzewo eksperymentów, napisze recenzowaną pracę w LaTeX i wyemituje pakiet powtarzalności.

Plan budowy:

1. Karnet literacki: Semantic Scholar Graph API + OpenAlex; streszczenia pamięci podręcznej w FAISS; wygeneruj jednostronicowe podsumowanie domeny.
2. Wyszukiwanie w drzewie: zaimplementuj ekspansję typu „najlepszy pierwszy” w węzłach eksperymentu z `expand(node) -> children` (jedna edycja konfiguracji na każde dziecko) i `score(node) = novelty*0.4 + quality*0.5 + budget*0.1`.
3. Piaskownica na węzeł: każdy eksperyment uruchamia odpowiednik `docker run --network=none --memory=8g --cpus=2 --pids-limit=256 --read-only` lub E2B; nasiona deterministyczne; Wymuszono ograniczenie zasobów.
4. Zaplanuj-wykonaj-weryfikuj: weryfikacja etapowa sprawdza, czy straty się zbiegły, przebiegły wartości bazowe, a ablacje izolują roszczenie.
5. Pisarz: wygeneruj LaTeX, skompiluj do formatu PDF, prześlij plik PDF do trybu wizyjnego Claude Opus 4.7 w celu krytyki układu i dopasowania twierdzeń do dowodów, iteruj do 3 razy.
6. Zespół recenzentów: pięciu sędziów (Opus 4.7, GPT-5.4, Gemini 3 Pro, DeepSeek R1, Qwen3-Max) ocenia w kategoriach NeurIPS (nowość, rygorystyczność, przejrzystość, odtwarzalność, wpływ); średnia < 4,0 zwracana do pisarza.
7. Zespół czerwony: zintegruj zadania kontradyktoryjne (bomba fork, ucieczka z systemu plików, wywołanie sieciowe napisane w LLM). Potwierdź wszystkie zablokowane. Emituj `red_team.md`.
8. Pakiet odtwarzalności: papier.pdf + review.md + śledzenie drzewa wyszukiwania JSON + nasiona + linki do uruchamiania W&B + konfiguracja piaskownicy + jednowierszowe polecenie ponownego uruchomienia.

Rubryka oceny:

| Waga | Kryterium | Pomiar |
|:-:|---|---|
| 25 | Jakość papieru | Ślepy przegląd rubryk w porównaniu z opublikowanymi artykułami warsztatowymi na ten sam temat nasion |
| 20 | Rygor eksperymentalny | Wartości bazowe, nasiona, ablacje; każde twierdzenie poparte komórką w tabeli wyników |
| 20 | Dyscyplina kosztów i obliczeń | Obowiązuje górny limit 30 dolarów za papier, śledzenie Langfuse |
| 20 | Bezpieczeństwo | Zespół Red Sandbox podaje; zasady sieciowe i wyłącznik awaryjny zweryfikowane na podstawie zarejestrowanych prób |
| 15 | Powtarzalność | Ponowne uruchomienie jednym poleceniem odtwarza papier z identycznymi nasionami |

Twarde odrzucenia:

- Eksperymenty przeprowadzane poza piaskownicą. Cała teza zwieńczenia jest taka, że ​​egzekucja jest ograniczona.
- Kroki autora, które nie czytają ponownie skompilowanego pliku PDF (krytyka wizyjna jest nośna).
- Artykuły bez linii bazowych, nasion lub sekcji dotyczącej ablacji.
- Budżety kosztów egzekwowane jedynie w formie ostrzeżeń post-hoc, a nie sztywnych pułapów.

Zasady odmowy:

- Odmówić opublikowania artykułu ze średnią recenzentów poniżej 4,0/5 bez wyraźnej zmiany ze strony człowieka.
- Odrzuć pomysł zalążkowy, który wymaga dostępu do sieci z wnętrza piaskownicy. Zamiast tego dodaj oddzielny wolumin zestawu danych tylko do odczytu.
- Odmówić ponownego opublikowania gazety, której drużyna czerwona nie została stracona i zarejestrowana.

Dane wyjściowe: repozytorium zawierające wyszukiwarkę drzewa, zasady piaskownicy, pętlę piszącego/recenzującego, trzy przykładowe uruchomienia z pakietami odtwarzalności, raport zespołu czerwonego, plik csv księgi kosztów oraz opis określający, które z trybów awarii Sakana v2 odtworzyłeś i jak działało łagodzenie.