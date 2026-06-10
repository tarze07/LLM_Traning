# Ramy gotowości OpenAI i Ramy bezpieczeństwa DeepMind Frontier

> Ramy gotowości OpenAI v2 (kwiecień 2025 r.) wprowadzają kategorie badawcze — autonomia dalekiego zasięgu, worki z piaskiem, autonomiczna replikacja i adaptacja, podważanie zabezpieczeń — odrębne od kategorii śledzonych. Śledzone kategorie uruchamiają raporty dotyczące możliwości i raporty zabezpieczeń sprawdzane przez Grupę Doradczą ds. Bezpieczeństwa. Rozwiązanie FSF v3 firmy DeepMind (wrzesień 2025 r., z dodanymi poziomami możliwości śledzenia 17 kwietnia 2026 r.) łączy autonomię w obszary badań i rozwoju ML oraz domeny cybernetyczne (poziom autonomii ML R&D 1 = pełna automatyzacja rurociągu badań i rozwoju w zakresie sztucznej inteligencji po konkurencyjnych kosztach w porównaniu z narzędziami ludzkimi i sztuczną inteligencją). FSF v3 wyraźnie rozwiązuje problem zwodniczego dostosowania poprzez automatyczne monitorowanie niewłaściwego użycia rozumowania instrumentalnego. Szczera uwaga: Kategorie badawcze w PF v2 (w tym Autonomia dalekiego zasięgu) nie powodują automatycznie środków łagodzących; językiem polityki jest „potencjalny”. Samo DeepMind twierdzi, że zautomatyzowane monitorowanie „nie będzie wystarczające w dłuższej perspektywie”, jeśli wzmocni się rozumowanie instrumentalne.

**Typ:** Ucz się
**Języki:** Python (stdlib, narzędzie do porównywania oparte na trzech platformach)
**Wymagania wstępne:** Faza 15 · 19 (Antropiczne RSP)
**Czas:** ~45 minut

## Problem

Lekcja 19. Przeczytaj uważnie politykę skalowania firmy Anthropic. Ta lekcja uzupełnia obraz, czytając OpenAI i DeepMind. Te trzy dokumenty to artefakty kuzynów, które odpowiadają na to samo pytanie – kiedy laboratorium graniczne powinno wstrzymać lub zamknąć model – i zbiegają się w niewielkim zestawie kategorii i różnią się w konkretnych, istotnych miejscach.

Zbieżność: wszystkie trzy określają autonomię dalekiego zasięgu jako klasę zdolności wartą śledzenia. Wszystkie trzy uznają oszukańcze zachowanie (fałszowanie ustawienia, worki z piaskiem) jako specyficzną klasę ryzyka. Wszystkie trzy posiadają wewnętrzny organ odwoławczy. Rozbieżność: OpenAI dzieli kategorie na „Śledzone” (obowiązkowe łagodzenie) i „Badania” (bez automatycznego wyzwalania). DeepMind dzieli autonomię na dwie domeny, zamiast nazywać ją osobno. Laboratorium nazywa monitorowane vs badawcze, krytyczne vs umiarkowane lub poziom 1 vs poziom 2; Konsekwencje operacyjne tego, w jakim przedziale znajduje się dana funkcja, są różne w zależności od laboratorium.

Wspólne czytanie jest pożytecznym ćwiczeniem. Ta sama funkcja może obejmować „obowiązkowe łagodzenie” w Anthropic, „monitorowanie, ale nie wyzwalanie” w OpenAI i „śledzenie w określonej domenie” w DeepMind. Nastawienie polityczne ma znaczenie.

## Koncepcja

### Ramy gotowości OpenAI, wersja 2 (kwiecień 2025 r.)

Struktura:

- **Śledzone kategorie**: uruchamiaj raporty możliwości (co potrafi model) oraz raporty zabezpieczeń (jakie środki łagodzące są stosowane). Sprawdzone przez Grupę Doradczą ds. Bezpieczeństwa przed wdrożeniem.
- **Kategorie badawcze**: możliwości modelu, które laboratorium śledzi, ale nie zobowiązuje się jeszcze do wprowadzenia konkretnych środków zaradczych. Obejmuje autonomię dalekiego zasięgu, worki z piaskiem, autonomiczną replikację i adaptację, podważanie zabezpieczeń.

Klatki kluczowe w wersji 2: Kategorie badawcze nie uruchamiają automatycznie środków zaradczych. Językiem polityki są „potencjalne” środki zaradcze. To jest specyficzna różnica, na którą warto zwrócić uwagę: lokalizacja kategorii w zestawie Śledzone vs. Badania stanowi zawias między „zamkniętymi” a „obserwowanymi”.

### DeepMind Frontier Safety Framework v3 (wrzesień 2025 r.; śledzenie poziomów możliwości dodano 17 kwietnia 2026 r.)

Struktura:

- **Poziomy zdolności krytycznych (CCL)**: progi zdolności w pięciu obszarach: cybernetyka, bio, badania i rozwój w zakresie uczenia maszynowego, CBRN, autonomia (łącznie z badaniami i rozwojem w zakresie uczenia maszynowego oraz cybernetyką).
- **Śledzone poziomy możliwości**: dodatkowa szczegółowość dodana w kwietniu 2026 r. Konkretny przykład: poziom autonomii ML w zakresie badań i rozwoju 1 = pełna automatyzacja procesu badawczo-rozwojowego w zakresie sztucznej inteligencji po konkurencyjnych kosztach w porównaniu z narzędziami ludzkimi i sztuczną inteligencją.
- **Zwodnicze monitorowanie dopasowania**: wyraźne zobowiązanie do automatycznego monitorowania niewłaściwego użycia rozumowania instrumentalnego.

Ramy autonomii różnią się od ram OpenAI. DeepMind nie utrzymuje „Autonomii” jako domeny najwyższego poziomu; obejmuje dziedziny, w których autonomia wyrządziłaby szkody (ML R&D i Cyber). Argument jest taki, że autonomia bez domeny to zdolność bez ryzyka; kontrargumentem jest to, że autonomia między domenami jest meta-ryzykiem, które framework powinien nazwać.

### Na czym zbiegają się wszystkie trzy

- Wewnętrzna Grupa Doradcza ds. Bezpieczeństwa (o nazwach Anthropic SAG, OpenAI SAG, wewnętrzny komitet DeepMind). Przed wdrożeniem przejrzyj modele o dużej wydajności.
- Wyraźna wzmianka o zwodniczym dostosowaniu / fałszowaniu ustawienia jako klasie ryzyka.
- Stałe artefakty w zadeklarowanej kadencji (Anthropic: plan działania dotyczący bezpieczeństwa na granicy, raport ryzyka; OpenAI: raporty dotyczące możliwości i zabezpieczeń; DeepMind: cykl aktualizacji FSF).
- Potwierdzenie, że zabezpieczenia służące wyłącznie do monitorowania mają pułap. DeepMind jasno stwierdza: „automatyczne monitorowanie nie będzie wystarczające w dłuższej perspektywie”.

### Gdzie się rozchodzą

- **Anthropic**: usunięto zobowiązanie do pauzy w wersji 3.0; Próg AI R&D-4 to nazwana następna brama.
- **OpenAI**: Podział śledzenia i badań; Kategorie badań (w tym Autonomia dalekiego zasięgu) nie są automatycznie bramowane.
- **DeepMind**: autonomia połączona z innymi domenami; Śledzone poziomy możliwości zwiększają szczegółowość w kwietniu 2026 r.

### Worki z piaskiem: specyficzna umiejętność, która komplikuje wszystkie trzy

Worki z piaskiem (model strategicznie wypadający słabo w ocenach) znajdują się w kategoriach badawczych OpenAI. RSP firmy Anthropic, wersja 3.0, rozwiązuje ten problem poprzez lukę w kontekście oceny (lekcja 1). DeepMind rozwiązuje ten problem poprzez zwodnicze monitorowanie dopasowania w FSF v3.

Jeśli model opiera się na ocenach, progi możliwości każdego frameworka są niedoszacowane. Struktura działa tylko wtedy, gdy pomiar działa. Dlatego też oprócz samooceny laboratorium konieczne są pomiary zewnętrzne (Lekcja 21, METR) i ocena kontradyktoryjna.

### Umiejętność czytania zasad

- Zlokalizuj: każda funkcja, na której Ci zależy, powinna być możliwa do znalezienia w polityce. Jeśli nie można go znaleźć, polisa go nie obejmuje.
- Klasyfikuj: czy jest śledzony (łagodzenie wyzwalaczy) czy badawczy (śledzony, ale nie wyzwalający)? OpenAI nazywa to; Anthropic i DeepMind mają swoje własne odpowiedniki.
- Kadencja: czy polityka jest aktualizowana według zadeklarowanego harmonogramu, czy dopiero po określonych zdarzeniach? Deklarowana kadencja jest mocniejsza.
- Niezależność: czy ocena zewnętrzna jest obowiązkowa czy opcjonalna? Partnerzy antropiczni z Apollo i amerykańskim Instytutem Bezpieczeństwa AI; OpenAI z METR; DeepMind głównie z wewnętrznym SAG.

## Użyj tego

`code/main.py` implementuje małe narzędzie do porównywania w formie tabeli decyzyjnej. Biorąc pod uwagę możliwość (autonomię, zwodnicze dostosowanie, automatyzację badań i rozwoju, poprawę cyberbezpieczeństwa itp.), pokazuje, w jaki sposób każda z trzech polityk klasyfikuje tę zdolność i jakie uruchamia środki łagodzące. To pomoc w czytaniu, a nie narzędzie polityczne.

## Wyślij to

`outputs/skill-cross-policy-diff.md` tworzy porównanie między zasadami dla określonej możliwości, używając trzech struktur jako odniesienia.

## Ćwiczenia

1. Uruchom `code/main.py`. Upewnij się, że dane wyjściowe narzędzia porównywania odpowiadają zasadom co najmniej dwóch funkcji, które możesz zweryfikować w dokumentach źródłowych.

2. Przeczytaj w całości Ramy gotowości OpenAI v2. Zidentyfikuj każdą kategorię badań. Dla każdego napisz jedno zdanie wyjaśniające, dlaczego znajduje się ono w obszarze Badania, a nie Śledzenie.

3. Przeczytaj w całości DeepMind FSF v3 oraz aktualizację śledzenia poziomów możliwości z kwietnia 2026 r. Zidentyfikuj szczegółowe kryteria oceny poziomu 1 autonomii ML w zakresie badań i rozwoju. Jak byś to zmierzył zewnętrznie?

4. Worki z piaskiem znajdują się w kategoriach badawczych OpenAI. Zaprojektuj ocenę, która zmusiłaby model worków z piaskiem do ujawnienia jego rzeczywistych możliwości. Odwołaj się do dyskusji na temat gier z lekcji 1.

5. Porównaj trzy zasady dotyczące konkretnej zdolności (twój wybór). Podaj, która klasyfikacja polis jest dla Ciebie najbardziej rygorystyczna, a która najmniej. Uzasadnij tekstem źródłowym.

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|---|---|---|
| Ramy gotowości | „Polityka skalowania OpenAI” | PF v2 (kwiecień 2025 r.); Śledzone a kategorie badawcze |
| Śledzona kategoria | „Obowiązkowe łagodzenie” | Możliwości wyzwalaczy + raporty zabezpieczeń; recenzja SAG |
| Kategoria badań | „Tylko monitorowane” | Śledzone, ale bez automatycznego łagodzenia skutków; obejmuje autonomię dalekiego zasięgu |
| Ramy bezpieczeństwa granicznego | „Polityka skalowania DeepMind” | FSF v3 (wrzesień 2025 r.) + śledzone poziomy możliwości (kwiecień 2026 r.) |
| CCL | „Krytyczny poziom zdolności” | Próg DeepMind na domenę (Cyber, Bio, ML R&D, CBRN) |
| Poziom autonomii ML w zakresie badań i rozwoju 1 | „Automatyzacja badań i rozwoju” | W pełni zautomatyzuj proces badań i rozwoju sztucznej inteligencji po konkurencyjnych kosztach |
| Worki z piaskiem | „Strategiczne słabe wyniki” | Model osiąga gorsze wyniki w ewaluacjach; w kategoriach badań OpenAI |
| Rozumowanie instrumentalne | „Rozumowanie o środkach i celach” | Rozumowanie o tym, jak osiągnąć cele; cel monitorowania DeepMind |

## Dalsze czytanie

— [OpenAI — aktualizacja naszych ram gotowości](https://openai.com/index/updating-our-preparedness-framework/) — ogłoszenie w wersji 2.
- [OpenAI — Gotowość Framework v2 PDF](https://cdn.openai.com/pdf/18a02b5d-6b67-4cec-ab64-68cdfbddebcd/preparedness-framework-v2.pdf) — pełny dokument.
– [DeepMind — Wzmocnienie naszych ram bezpieczeństwa na granicach](https://deepmind.google/blog/strengthening-our-frontier-safety-framework/) — Ogłoszenie FSF v3.
– [DeepMind — Aktualizacja ram bezpieczeństwa na granicy (kwiecień 2026 r.)](https://deepmind.google/blog/updating-the-frontier-safety-framework/) — Dodanie śledzonych poziomów możliwości.
– [Raport FSF Gemini 3 Pro](https://storage.googleapis.com/deepmind-media/gemini/gemini_3_pro_fsf_report.pdf) — przykład raportu ryzyka w formacie FSF.