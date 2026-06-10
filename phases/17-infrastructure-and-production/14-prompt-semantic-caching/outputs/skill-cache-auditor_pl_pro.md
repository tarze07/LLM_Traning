---

name: cache-auditor
description: Przeprowadzenie audytu szablonu promptu LLM oraz charakterystyki ruchu pod kątem możliwości buforowania. Rekomendacje dotyczące restrukturyzacji promptu, wyboru czasu TTL, optymalizacji współbieżności i progu podobieństwa dla pamięci podręcznej semantycznej.
version: 1.0.0
phase: 17
lesson: 14
tags: [caching, prompt-cache, semantic-cache, anthropic, openai, parallelization, ttl]

---

Na podstawie podanego szablonu promptu, charakterystyki ruchu (częstotliwość zapytań, stopień współbieżności) oraz dostawcy API (Anthropic, OpenAI, Gemini, vLLM we własnej infrastrukturze), przeprowadź audyt efektywności buforowania.

Przygotuj:

1. Strukturę prefiksów: Podziel szablon promptu na sekcje statyczne (buforowane) i dynamiczne (niebuforowane). Wskaż wszelkie dynamiczne treści znajdujące się obecnie w prefiksie i zaproponuj ich przeniesienie/przepisanie.
2. Wybór TTL: Porównanie opcji Anthropic: TTL 5 minut (narzut zapisu 1.25x) vs 1 godzina (narzut zapisu 2x). Podejmij decyzję na podstawie częstotliwości zapytań – opcja 1-godzinna jest opłacalna, jeśli prefiks jest ponownie używany w ciągu godziny.
3. Audyt współbieżności: Zidentyfikuj zapytania równoległe współdzielące ten sam prefiks. Jeśli N > 2 i zapytania są wysyłane współbieżnie, wymagaj wdrożenia wzorca „najpierw sekwencyjnie, potem równolegle” (serialize-first-then-fanout). Oszacuj oczekiwaną redukcję kosztów.
4. Ocena buforowania semantycznego (L1): Zdecyduj, czy wdrożenie L1 ma uzasadnienie biznesowe. W przypadku otwartego czatu prawdopodobnie nie (niski hit rate). Dla ustrukturyzowanych FAQ/wsparcia – tak. Ustal próg podobieństwa cosinusowego (początkowo 0.95); obniżaj go wyłącznie na podstawie testów jakości odpowiedzi.
5. Prognozę oszczędności: Oblicz szacowaną miesięczną różnicę w kosztach (USD) w porównaniu do wariantu bazowego bez buforowania, uwzględniając obecny ruch i zakładane współczynniki trafień.
6. Metryki i monitorowanie (Observability): Zdefiniuj kluczowy wskaźnik na dashboardzie wykrywający regresje – współczynnik trafień cache L2 w ujęciu godzinowym. Skonfiguruj alert, gdy spadnie on o więcej niż 20%.

Kryteria odrzucenia audytu:
- Deklarowanie sztywnych „50% oszczędności” bez szczegółowego obliczenia oczekiwanego współczynnika trafień oraz narzutu za zapis. Odrzuć taki audyt – wymaga on kalkulacji dla każdej warstwy osobno.
- Pozostawienie dynamicznej treści w prefiksie w sytuacji, gdy proste przepisanie pozwoliłoby na jej przeniesienie na koniec. Odrzuć.
- Wysyłanie równoległych żądań ze współdzielonym prefiksem bez zastosowania wzorca „najpierw sekwencyjnie”. Odrzuć – wskaż ryzyko 5-10-krotnego wzrostu kosztów.

Zasady odmowy/zastrzeżenia:
- Jeśli prompt zawiera >80% zawartości dynamicznej, nie gwarantuj oszczędności z buforowania prefiksów. W takim przypadku zalecaj co najwyżej buforowanie semantyczne.
- Jeśli próg podobieństwa dla cache semantycznego zostanie ustawiony poniżej 0.85 bez przeprowadzenia oceny jakości odpowiedzi, odrzuć projekt ze względu na ryzyko halucynacji lub zwracania błędnych odpowiedzi.
- Jeśli dostawca API nie obsługuje jawnej kontroli cache (np. dostawca inny niż Anthropic, bądź wersje Gemini bez jawnego buforowania) i polega wyłącznie na automatycznym buforowaniu, zaznacz, że współczynnik trafień ma charakter oportunistyczny i nie jest gwarantowany.

Format końcowy: Jednostronicowy raport z audytu zawierający: schemat przepisanego prefiksu, rekomendację TTL, wzorzec współbieżności, próg L1, prognozowane oszczędności oraz zalecane metryki monitorowania. Raport należy zakończyć rekomendacją kwartalnego przeglądu – ponownego audytu promptów po każdej zmianie ich szablonów.
