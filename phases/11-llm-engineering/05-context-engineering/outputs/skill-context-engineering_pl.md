---

name: skill-context-engineering
description: Ramy decyzyjne dotyczące projektowania potoków montażu kontekstu w oparciu o typ zadania, rozmiar okna i budżet opóźnień
version: 1.0.0
phase: 11
lesson: 05
tags: [context-engineering, context-window, rag, memory, tool-selection, lost-in-the-middle]

---

# Inżynieria kontekstowa

Podczas tworzenia aplikacji LLM zastosuj tę strukturę do zaprojektowania potoku montażu kontekstu.

## Podstawowe zasady

1. **Kontekst jest rzadki.** Okno 128 tys. wydaje się duże, ale szybko się zapełnia. Budżetuj każdy komponent jawnie.
2. **Uwaga jest nierówna.** Modelki skupiają się bardziej na początku i na końcu. Umieść tam najważniejsze informacje. Środek to martwa strefa.
3. **Dynamiczne uderzenia są statyczne.** Różne zapytania wymagają innego kontekstu. Składaj na zapytanie, a nie raz przy uruchomieniu.
4. **Mniej znaczy więcej.** Wyselekcjonowany kontekst 10 tys. jest lepszy od porzuconego kontekstu 100 tys. Stosunek sygnału do szumu ma większe znaczenie niż całkowita informacja.
5. **Mierz wszystko.** Nie możesz optymalizować tego, czego nie mierzysz. Zliczaj tokeny na komponent przy każdym żądaniu.

## Kontekstowe wytyczne budżetowe

| Składnik | Typowy zakres | Priorytet | Strategia kompresji |
|----------|-------------|----------|-----------------------------------|
| Podpowiedź systemowa | 200-1000 tokenów | Naprawiono, wysoki | Napisz ciasno, usuń nadmiarowość |
| Definicje narzędzi | 500-3000 tokenów | Dynamiczny, średni | Przytnij według celu zapytania |
| Pobrany kontekst | 1 000-5 000 tokenów | Dynamiczny, wysoki | Zmiana rankingu + próg + deduplikacja |
| Historia rozmów | 500-5000 tokenów | Dynamiczny, średni | Podsumuj stare zwroty |
| Kilka przykładów | 500-2000 tokenów | Dynamiczny, wysoki | Wybierz według podobieństwa zadań |
| Zapytanie użytkownika | 50-500 tokenów | Naprawiono, najwyższy | Nie dotyczy |
| Rezerwa wytwórcza | 2 000-8 000 tokenów | Naprawiono | Dostosuj według oczekiwanej długości wyjściowej |

## Kiedy używać każdego typu pamięci

**Krótkoterminowe (historia rozmów):** Bieżąca sesja. Zarządzane poprzez podsumowanie. Kompresy są starsze niż 5-10 wymian. Zachowaj dosłownie ostatnie 3-4 tury.

**Długoterminowe (baza danych faktów):** Preferencje i fakty dotyczące projektu, które utrzymują się podczas sesji. Pobierz na początku sesji. Przykłady: „użytkownik woli Pythona”, „projekt korzysta z PostgreSQL”, „zespół podąża za rozwojem opartym na trunkingu”. Przechowuj w CLAUDE.md, bazie danych lub systemie pamięci strukturalnej.

**Epizodyczne (przeszłe interakcje):** Konkretne rozmowy z przeszłości, istotne dla bieżącego zadania. Przechowuj jako elementy osadzone, pobieraj na podstawie podobieństwa. „W zeszłym tygodniu debugowaliśmy podobny problem z uwierzytelnianiem” to pamięć epizodyczna.

## Strategia wyboru narzędzia

Nie dołączaj wszystkich narzędzi do każdego żądania. To marnuje żetony i dezorientuje model.

1. Klasyfikuj intencję zapytania (kod, e-mail, kalendarz, badania, dane)
2. Przypisz intencje do kategorii narzędzi
3. Dołącz tylko pasujące narzędzia
4. Jeśli intencja jest niejednoznaczna, uwzględnij narzędzia z 2 najlepszych kategorii
5. Zawsze dołączaj narzędzie „ogólne” (np. wyszukiwarkę internetową) jako narzędzie zastępcze

Oczekiwane oszczędności: 60–80% tokenów definicji narzędzi w przypadku zapytań z jasną intencją.

## Najlepsze praktyki w zakresie pobierania

- **Ponowna ocena po pobraniu.** Podobieństwo wektorów to filtr przybliżony. Narzędzie do zmiany rankingu (koder krzyżowy lub oparty na LLM) znacznie poprawia precyzję.
- **Ustaw próg trafności.** Nie uwzględniaj fragmentów o podobieństwie poniżej 0,3 cosinusa. Dodają hałasu.
- **Dedduplikacja.** Jeśli dwie części mają łącznie ponad 80% zawartości, zachowaj tylko tę z wyższą oceną.
- **Zastosuj kolejność gubiąc się w środku.** Umieść najbardziej odpowiednie fragmenty jako pierwsze i ostatnie.
- **Ogranicz całkowitą liczbę tokenów pobierania.** 3-5 bardzo istotnych fragmentów zamiast 15 przeciętnych.

## Zarządzanie historią

- Zachowaj dosłownie ostatnie 3-4 tury (model wymaga najnowszego kontekstu)
- Podsumuj starsze zmiany w skrócie („Omówiliśmy X, zdecydowaliśmy o Y i zablokowaliśmy Z”)
- Upuść zakręty generowane przez system, które nie dodają żadnych informacji (wywołania narzędzi bez treści skierowanych do użytkownika)
- Uruchom kompresję, gdy historia przekroczy 30% dostępnego budżetu

## Czerwone flagi

- Monit systemowy przekracza 2000 tokenów: prawdopodobnie zawiera informacje, które powinny być dynamiczne
- Wszystkie narzędzia zawarte w każdym żądaniu: wdrożenie selekcji opartej na intencjach
- Brak filtrowania trafności przy wyszukiwaniu: wyrzucasz hałas do okna
- Historia rośnie nieograniczona: podsumowanie nie jest realizowane
- Brak rezerwy wytwórczej: model obcina swoje odpowiedzi
- Te same informacje w 3 miejscach (podpowiedź systemowa, pobrany dokument, historia): deduplikacja
- Wykorzystanie kontekstu powyżej 60%: zostawiasz zbyt mało miejsca, aby model mógł „myśleć”