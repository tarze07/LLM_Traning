---

name: moderation-stack
description: Zalecenia konfiguracji stosu moderacji dla wdrożenia produkcyjnego.
version: 1.0.0
phase: 18
lesson: 29
tags: [openai-moderation, perspective, llama-guard, layered-moderation, azure-content-safety]

---

Biorąc pod uwagę wdrożenie produkcyjne, zaleć konfigurację stosu moderacji w trzech warstwach.

Wyprodukuj:

1. Klasyfikator wejściowy. Wybierz Moderacja OpenAI, Llama Guard 3/4 lub Perspective API. Dopasuj do taksonomii zasad. W przypadku wdrożeń multimodalnych należy zastosować moderację Llama Guard 4 lub OpenAI.
2. Klasyfikator wyników. Taki sam lub inny niż klasyfikator wejściowy. Dopasuj progi do modelu ryzyka na niższym szczeblu łańcucha dostaw.
3. Niestandardowe reguły domeny. Wymień reguły specyficzne dla danej dziedziny, których nie wyłapią klasyfikatory ogólne: zastrzeżenia dotyczące porad finansowych, odmowy udzielenia porad medycznych, wzorce wyłączeń odpowiedzialności prawnej.
4. Sędzia w sprawach Edge. Określ ścieżkę eskalacji personelu. Twarde odmowy są ostateczne; niejednoznaczne przypadki kierowane są do przeglądu przez człowieka w ramach SLA.
5. Plan migracji. Jeśli na stosie znajduje się usługa Azure Content Moderator, zaplanuj migrację do usługi Azure AI Content Safety przed wycofaniem w lutym 2027 r.

Twarde odrzucenia:
- Każde wdrożenie bez moderacji wyników (samo wejście nie wystarczy).
- Każde wdrożenie bez niestandardowych reguł domeny na regulowanych powierzchniach (finanse, zdrowie, prawo).
- Każde wdrożenie opierające się wyłącznie na klasyfikatorach sprzed ery LLM (Perspective) dla nowoczesnych aplikacji do czatowania.

Zasady odmowy:
- Jeśli użytkownik poprosi o najlepszy pojedynczy klasyfikator, odmów — wybór klasyfikatora zależy od taksonomii polityki.
- Jeśli użytkownik prosi o progi, odrzuć pojedyncze liczby — progi zależą od tolerancji ryzyka i dalszych skutków.

Wynik: jednostronicowe zalecenie dotyczące wypełnienia pięciu sekcji, nadania nazwy klasyfikatorowi w każdej warstwie i oznaczenia obowiązków związanych z migracją. Cytuj raz każdą dokumentację OpenAI Moderation i odniesienia do Llama Guard 3/4.