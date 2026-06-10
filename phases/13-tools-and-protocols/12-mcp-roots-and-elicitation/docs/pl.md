# Korzenie i pozyskiwanie — określanie zakresu i wkład użytkownika w trakcie lotu

> Zakodowane na stałe ścieżki przerywają moment otwarcia przez użytkownika innego projektu. Wstępnie wypełnione argumenty narzędzia psują się, gdy użytkownik nie określi ich wartości. Roots ogranicza serwer do kontrolowanego przez użytkownika zestawu identyfikatorów URI; wywoływanie wstrzymuje się w połowie wywołania narzędzia, aby poprosić użytkownika o ustrukturyzowane wprowadzenie danych za pośrednictwem formularza lub adresu URL. Dwa elementy podstawowe klienta, dwie poprawki typowych trybów awarii MCP. SEP-1036 (wywoływanie trybu URL, 25.11.2025 r.) ma charakter eksperymentalny do pierwszej połowy 2026 r. — sprawdź wersje pakietu SDK, zanim zaczniesz na nim polegać.

**Typ:** Kompilacja
**Języki:** Python (stdlib, roots + demonstracja wywoływania)
**Wymagania wstępne:** Faza 13 · 07 (serwer MCP)
**Czas:** ~45 minut

## Cele nauczania

- Zadeklaruj `roots` i odpowiedz na `notifications/roots/list_changed`.
- Ogranicz operacje na plikach serwera do identyfikatorów URI znajdujących się w zadeklarowanym zestawie głównym.
- Użyj `elicitation/create`, aby poprosić użytkownika o potwierdzenie lub ustrukturyzowane wprowadzenie danych w trakcie wywołania narzędzia.
- Wybierz pomiędzy wywoływaniem w trybie formularza i w trybie adresu URL (ten drugi jest eksperymentalny; odnotowano ryzyko dryfu).

## Problem

Dwie konkretne awarie, na które natrafia serwer MCP podczas produkcji.

**Założenie o nieprawidłowej ścieżce.** Serwer jest zapisany zgodnie z `~/notes`. Użytkownik na innej maszynie z notatkami w `~/Documents/Notes` otrzymuje wywołanie narzędzia, które kończy się cichym niepowodzeniem (nie znaleziono pliku) lub, co gorsza, zapisaniem w niewłaściwym miejscu.

**Brakujący argument, który użytkownik mógłby znać.** Użytkownik pyta „usuń starą notatkę z raportu TPS”. Model wywołuje `notes_delete(title: "TPS report")`, ale istnieją trzy pasujące notatki z lat 2023, 2024 i 2025. Narzędzie nie może zgadywać. Niepowodzenie w przypadku „niejednoznaczności” jest denerwujące; bieganie na wszystkich trzech jest katastrofalne.

Roots naprawiają pierwszy: klient deklaruje w `initialize` zestaw identyfikatorów URI, z którymi może się stykać serwer. Funkcja elicitation naprawia drugą opcję: serwer wstrzymuje wywołanie narzędzia i wysyła `elicitation/create` z prośbą do użytkownika o wybranie, które z nich.

## Koncepcja

### Korzenie

Klient deklaruje listę główną pod adresem `initialize`:

```json
{
  "capabilities": {"roots": {"listChanged": true}}
}
```

Serwer może następnie wywołać `roots/list`:

```json
{"roots": [{"uri": "file:///Users/alice/Documents/Notes", "name": "Notes"}]}
```

Serwery MUSZĄ traktować korzenie jako granicę: każdy plik odczytywany lub zapisywany poza zestawem głównym jest odrzucany. Nie jest to wymuszane przez klienta (serwer nadal ma kod, któremu użytkownik ufa), ale serwery zgodne ze specyfikacją to honorują.

Kiedy użytkownik dodaje lub usuwa katalog główny, klient wysyła `notifications/roots/list_changed`. Serwer ponownie wywołuje `roots/list` i aktualizuje swoją granicę.

### Dlaczego korzenie są prymitywnym klientem

Korzenie są deklarowane przez klienta, ponieważ reprezentują model zgody użytkownika. Użytkownik powiedział Claude Desktop „daj temu serwerowi notatek dostęp do tych dwóch katalogów”. Serwer nie może rozszerzyć tego zakresu.

### Wywoływanie: domyślny tryb formularza

`elicitation/create` przyjmuje schemat formularza i zachętę w języku naturalnym:

```json
{
  "method": "elicitation/create",
  "params": {
    "message": "Delete 'TPS report'? Multiple notes match; pick one.",
    "requestedSchema": {
      "type": "object",
      "properties": {
        "note_id": {
          "type": "string",
          "enum": ["note-3", "note-7", "note-14"]
        },
        "confirm": {"type": "boolean"}
      },
      "required": ["note_id", "confirm"]
    }
  }
}
```

Klient renderuje formularz, zbiera odpowiedź użytkownika, zwraca:

```json
{
  "action": "accept",
  "content": {"note_id": "note-14", "confirm": true}
}
```

Trzy możliwe akcje: `accept` (użytkownik wypełnił), `decline` (użytkownik zamknął), `cancel` (użytkownik przerwał całe wywołanie narzędzia).

Schematy formularzy są płaskie — obiekty zagnieżdżone nie są obsługiwane w wersji 1. Zestawy SDK zazwyczaj odrzucają wszystko, co jest bardziej złożone niż pojedyncza warstwa.

### Wywoływanie: tryb URL (SEP-1036, eksperymentalny)

Nowość w 2025-11-25. Zamiast schematu serwer wysyła adres URL:

```json
{
  "method": "elicitation/create",
  "params": {
    "message": "Sign in to GitHub",
    "url": "https://github.com/login/oauth/authorize?client_id=..."
  }
}
```

Klient otwiera adres URL w przeglądarce, czeka na zakończenie, wraca, gdy użytkownik wróci. Przydatne w przypadku przepływów OAuth, autoryzacji płatności i podpisywania dokumentów, gdy formularz jest niewystarczający.

Uwaga dotycząca ryzyka dryfu: kształt odpowiedzi SEP-1036 wciąż się ustala; niektóre zestawy SDK zwracają adres URL wywołania zwrotnego, inne zwracają token zakończenia. Przeczytaj informacje o wersji pakietu SDK przed użyciem trybu URL w środowisku produkcyjnym.

### Kiedy pozyskiwanie informacji jest właściwym narzędziem

- Potwierdzenie użytkownika przed destrukcyjnymi działaniami (niszcząca wskazówka + wywołanie).
- Ujednoznacznienie (wybierz jedno z N dopasowań).
- Konfiguracja pierwszego uruchomienia (klucze API, katalogi, preferencje).
- Przepływy w stylu OAuth (tryb URL).

### Gdy wywoływanie jest nieprawidłowe

- Uzupełnienie wymaganych przez narzędzie argumentów, o które model mógłby poprosić w prozie. Użyj normalnego monitu, a nie okna dialogowego z zachętą.
- Połączenia o wysokiej częstotliwości. Wywołanie przerywa rozmowę; nie uruchamiaj go w pętli.
- Wszystko, co serwer może sprawdzić po fakcie. Sprawdź, zwróć błąd, pozwól modelowi zapytać użytkownika tekstem.

### Most człowieka w pętli

Wywoływanie i próbkowanie razem umożliwiają model „człowieka w pętli” MCP. Pętla agenta serwera może zostać wstrzymana w celu wprowadzenia danych przez użytkownika (wywoływanie) lub rozumowania modelowego (próbkowanie). Faza 13 · 11 obejmowała pobieranie próbek; ta lekcja dotyczy wywoływania. Połącz je razem, aby uzyskać pełną kontrolę w środkowej pętli.

## Użyj tego

`code/main.py` rozszerza serwer notatek o:

- `roots/list` odpowiedź, którą serwer wysyła ponownie po powiadomieniu o zmianie listy głównej.
- Narzędzie `notes_delete`, które wykorzystuje `elicitation/create` do ujednoznacznienia dopasowania wielu notatek.
- Narzędzie `notes_setup`, które wykorzystuje wywoływanie w trybie adresu URL w celu otwarcia pierwszej strony konfiguracyjnej (symulowanej).
- Kontrola granic, która odmawia operacji na identyfikatorach URI poza zadeklarowanymi korzeniami.

Demo obejmuje trzy scenariusze: szczęśliwa ścieżka (jeden mecz), ujednoznacznienie (trzy dopasowania, wywołanie wywołania), zapis poza rootem (odrzucony).

## Wyślij to

Ta lekcja przedstawia `outputs/skill-elicitation-form-designer.md`. Mając narzędzie, które może wymagać potwierdzenia lub ujednoznacznienia użytkownika, umiejętność projektuje schemat formularza pozyskiwania i szablon wiadomości.

## Ćwiczenia

1. Uruchom `code/main.py`. Uruchom ścieżkę ujednoznaczniającą; potwierdź, że symulowana odpowiedź użytkownika zostanie przekierowana z powrotem do narzędzia.

2. Dodaj nowe narzędzie `notes_archive`, które za każdym razem wymaga potwierdzenia wywołania (niszcząca wskazówka). Sprawdź UX: jak to się ma do ponownego zapytania modelu w tekście?

3. Zaimplementuj wywoływanie w trybie adresu URL dla pierwszego uruchomienia przepływu OAuth. Zwróć uwagę na ryzyko dryfu i dodaj zabezpieczenie w wersji SDK.

4. Rozszerz obsługę `roots/list`: gdy nadejdzie powiadomienie, serwer powinien atomowo ponownie odczytać i ponownie przeskanować uchwyty otwartych plików, które mogą być teraz poza zakresem.

5. Przeczytaj wątek dyskusji na temat problemu SEP-1036 w serwisie GitHub. Zidentyfikuj jedno otwarte pytanie, które wpływa na sposób, w jaki serwery powinny obsługiwać wywołania zwrotne w trybie URL.

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|----------------|--------------------------------------|
| Korzeń | „Granica zgody” | URI, z którego klient zezwolił serwerowi na kontakt |
| `roots/list` | „Serwer pyta o zakres” | Klient zwraca bieżący zestaw główny |
| `notifications/roots/list_changed` | „Użytkownik zmienił zakres” | Klient sygnalizuje, że zestaw główny uległ mutacji |
| Wywoływanie | „Zapytaj użytkownika w trakcie rozmowy” | Inicjowane przez serwer żądanie ustrukturyzowanego wprowadzania danych przez użytkownika |
| `elicitation/create` | „Metoda” | Metoda JSON-RPC dla żądań wywołania |
| Tryb formularza | „Formularz oparty na schemacie” | Płaski schemat JSON renderowany jako formularz w interfejsie klienta |
| Tryb URL | „Przekierowanie przeglądarki” | eksperymentalny SEP-1036; otwiera adres URL i czeka |
| `accept` / `decline` / `cancel` | „Wyniki reakcji użytkowników” | Trzy gałęzie obsługiwane przez serwer |
| Ujednoznacznienie | „Wybierz jeden” | Typowy przypadek użycia pozyskiwania, gdy narzędzie ma N kandydatów |
| Płaska forma | „Tylko nieruchomości najwyższego poziomu” | Schematy pozyskiwania nie mogą być zagnieżdżane |

## Dalsze czytanie

- [MCP — specyfikacja korzeni klienta](https://modelcontextprotocol.io/specification/draft/client/roots) — odniesienie do korzeni kanonicznych
- [MCP — specyfikacja pozyskiwania klientów](https://modelcontextprotocol.io/specification/draft/client/elicitation) — kanoniczne odniesienie do pozyskiwania
- [Cisco — Co nowego w pozyskiwaniu MCP, treści strukturalnej, udoskonaleniach OAuth](https://blogs.cisco.com/developer/whats-new-in-mcp-elicitation-structured-content-and-oauth-enhancements) — przegląd dodatków 2025-11-25
- [MCP — GitHub SEP-1036](https://github.com/modelcontextprotocol/modelcontextprotocol) — propozycja wywoływania w trybie URL (eksperymentalna, ryzyko dryfu)
– [The New Stack — Jak pozyskiwanie wprowadza technologię human-in-the-loop do narzędzi AI](https://thenewstack.io/how-elicitation-in-mcp-brings-human-in-the-loop-to-ai-tools/) — Przewodnik po UX