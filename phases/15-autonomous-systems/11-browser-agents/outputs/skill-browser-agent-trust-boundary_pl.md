---

name: browser-agent-trust-boundary
description: Określ zakres proponowanego wdrożenia agenta przeglądarki — strefy zaufania, autoryzowane zapisy, wymagane zabezpieczenia — zanim agent dotknie prawdziwej witryny.
version: 1.0.0
phase: 15
lesson: 11
tags: [browser-agents, prompt-injection, trust-boundary, osworld, webarena]

---

Biorąc pod uwagę proponowany przepływ pracy agenta przeglądarki, utwórz dokument określający zakres granic zaufania, który wylicza każdy odczyt, każdy zapis i minimalny stos obrony wymagany do pierwszego uruchomienia.

Wyprodukuj:

1. **Przeczytaj powierzchnię.** Wymień wszystkie źródła, które agent pobierze. Sklasyfikuj każdą z nich jako zaufaną (strony własne obsługiwane przez organizację użytkownika) lub niezaufaną (dowolna strona trzecia, dowolna treść wygenerowana przez użytkownika, dowolny wynik wyszukiwania). Wszystkie odczyty spoza zaufania należy traktować jako potencjalne kanały szybkiego wstrzykiwania.
2. **Zapisz powierzchnię.** Wypisz wszystkie następujące działania, do których agent jest upoważniony (przesłanie formularza, opublikowanie treści, wywołanie narzędzia zaplecza, zapis do pamięci). Dla każdego z nich określ promień wybuchu i czy działanie jest odwracalne.
3. **Wymagane zabezpieczenia.** Minimalny stos: czyszczenie zawartości, granica odczytu/zapisu (zapisy wymagają świeżego zatwierdzenia, gdy content_origin jest poza zaufaniem), lista dozwolonych narzędzi na zadanie, izolacja sesji z poświadczeniami o określonym zakresie, tokeny kanaryjskie w pamięci trwałej, HITL dla nieodwracalnych działań.
4. **Dopasowanie testu porównawczego do dystrybucji.** Jeśli agent zgłosi wynik zweryfikowany przez przeglądarkę BrowseComp, OSWorld lub WebArena, podaj nazwę nakładania się dystrybucji między testem porównawczym a rzeczywistym zadaniem. Wysoki wynik BrowseComp nie pozwala przewidzieć niezawodności przepływu rezerwacji.
5. **Lista kontrolna znanych ataków.** Potwierdź, że wdrożenie jest odporne na (a) wstrzykiwanie widocznego tekstu, (b) wstrzykiwanie fragmentów adresu URL/zapytań, (c) ataki polegające na wiązaniu pamięci (klasa Tainted Memories), (d) ataki w kształcie CSRF na uwierzytelnione sesje, (e) przechwytywania jednym kliknięciem. Dla każdego z nich nazwij konkretną obronę i miejsce, w którym strzela.

Twarde odrzucenia:
- Agenci przeglądarki z dostępem do poświadczeń produkcyjnych i bez izolacji sesji.
- Każde wdrożenie, w którym zapis inicjowany jest z zawartości niezaufanej, nie wymaga świeżej zgody HITL.
- Każde wdrożenie polegające wyłącznie na odkażaniu zawartości (środki odkażające wyłapują łatwe ataki; wyrafinowane ładunki przechodzą).
- Trwała pamięć bez wpisów dotyczących kanarków.
- Przepływy pracy dotyczące transakcji finansowych lub danych klientów bez HITL przy zapisach.

Zasady odmowy:
- Jeśli użytkownik nie może podać promienia wybuchu wtrysku, napisz błędnie, odmów i zażądaj wyraźnego zdania.
- Jeśli użytkownik zaproponuje agenta przeglądarki na stosie, na którym nie są dostępne poświadczenia o określonym zakresie, odmów i zażądaj najpierw osobnej tożsamości.
- Jeśli użytkownik przytacza wynik testu porównawczego (BrowseComp, OSWorld, WebArena) jako dowód, że agent „może” wykonać zadanie produkcyjne, odmówić i zażądać wewnętrznej oceny rzeczywistej dystrybucji.

Format wyjściowy:

Zwróć notatkę dotyczącą granicy zaufania zawierającą:
- **Odczyt tabeli powierzchni** (pochodzenie, zaufanie / brak zaufania)
- **Zapisz tabelę powierzchni** (działanie, promień wybuchu, odwracalne tak/nie)
- **Stos obronny** (wypunktowana lista skonfigurowanych warstw)
- **Nota dotycząca dopasowania do wzorca** (jeśli dotyczy)
- **Lista kontrolna znanych ataków** (pięć rzędów, obrona nazwana w każdym rzędzie)
- **Ocena wdrożenia** (wyłącznie produkcja / testowanie / badania)