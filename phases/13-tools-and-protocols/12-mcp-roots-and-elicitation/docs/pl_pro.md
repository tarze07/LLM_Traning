# Korzenie i pozyskiwanie — określanie zakresu i wkład użytkownika w trakcie lotu

> Kodowanie ścieżek dostępu na stałe (hardcoding) zawodzi, gdy użytkownik otwiera inny projekt. Automatyczne uzupełnianie argumentów narzędzi zawodzi, gdy zapytanie użytkownika jest niejednoznaczne. Katalogi główne (Roots) ograniczają uprawnienia serwera do zdefiniowanego przez użytkownika zestawu ścieżek URI. Z kolei formularze wywoływania (Elicitation) pozwalają serwerowi na wstrzymanie wykonania narzędzia i poproszenie użytkownika o podanie ustrukturyzowanych danych wejściowych za pomocą formularza lub adresu URL. To dwa kluczowe komponenty klienckie rozwiązujące najczęstsze błędy w integracjach MCP. Standard SEP-1036 (obsługujący wywoływanie w trybie URL z dnia 25.11.2025 r.) ma status eksperymentalny do pierwszej połowy 2026 roku – przed wdrożeniem należy upewnić się, że wersja używanego SDK go wspiera.

**Typ:** Kompilacja
**Języki:** Python (biblioteka standardowa, integracja roots + elicitation)
**Wymagania wstępne:** Faza 13 · 07 (Budowa serwera MCP)
**Czas:** ~45 minut

## Cele nauczania

- Zadeklaruj katalogi główne (`roots`) po stronie klienta i obsłuż powiadomienie `notifications/roots/list_changed` po stronie serwera.
- Ogranicz zakres operacji na plikach serwera wyłącznie do ścieżek URI zadeklarowanych w katalogach głównych.
- Wykorzystaj żądanie `elicitation/create`, aby poprosić użytkownika o zatwierdzenie akcji lub podanie dodatkowych danych w trakcie wykonywania narzędzia.
- Dokonaj wyboru między wywoływaniem w trybie formularza a trybem adresu URL (uwzględniając eksperymentalny charakter tego drugiego).

## Problem

Przeanalizujmy dwa typowe problemy, na które napotykają serwery MCP w środowiskach produkcyjnych:

**Błędne założenie dotyczące ścieżek dostępu.** Kod serwera zakłada, że notatki znajdują się w katalogu `~/notes`. Jeśli użytkownik przechowuje je w ścieżce `~/Documents/Notes`, wywołanie narzędzia zakończy się cichym błędem (nie odnaleziono pliku) lub zapisze dane w niewłaściwej lokalizacji.

**Niejednoznaczność parametrów.** Użytkownik prosi: „usuń starą notatkę z raportu TPS”. Model próbuje wywołać `notes_delete(title: "TPS report")`, ale w systemie istnieją trzy notatki o takim tytule (z lat 2023, 2024 i 2025). Narzędzie nie może zgadywać – przerwanie działania z powodu błędu niejednoznaczności jest irytujące dla użytkownika, a usunięcie wszystkich trzech notatek byłoby katastrofalne.

Komponent **Roots** rozwiązuje pierwszy problem: klient deklaruje podczas inicjalizacji zestaw ścieżek URI, do których dostęp ma serwer. Komponent **Elicitation** rozwiązuje drugi problem: serwer wstrzymuje wykonanie narzędzia i wysyła żądanie `elicitation/create`, prosząc użytkownika o wskazanie właściwego dokumentu.

## Koncepcja

### Katalogi główne (Roots)

Klient deklaruje obsługę katalogów głównych podczas inicjalizacji żądaniem `initialize`:

```json
{
  "capabilities": {"roots": {"listChanged": true}}
}
```

Serwer może następnie odpytać klienta za pomocą `roots/list`:

```json
{"roots": [{"uri": "file:///Users/alice/Documents/Notes", "name": "Notes"}]}
```

Serwery mają obowiązek traktować te ścieżki jako twardą granicę uprawnień: każda próba odczytu lub zapisu pliku poza zadeklarowanymi katalogami głównymi powinna być odrzucona przez serwer. Ograniczenie to nie jest technicznie wymuszane przez proces klienta (serwer to niezależny proces uruchamiany na maszynie), ale serwery zgodne ze specyfikacją muszą bezwzględnie przestrzegać tej reguły.

Gdy użytkownik dodaje lub usuwa katalog w konfiguracji klienta, wysyłane jest powiadomienie `notifications/roots/list_changed`. Serwer powinien wtedy odpytać klienta metodą `roots/list` i zaktualizować swoje granice dostępu.

### Dlaczego katalogi główne należą do komponentów klienta?

Katalogi główne są definiowane po stronie klienta, ponieważ reprezentują uprawnienia i zakres zgody użytkownika. Użytkownik wskazuje w aplikacji klienckiej (np. Claude Desktop): „pozwalam temu serwerowi notatek na dostęp wyłącznie do tych dwóch folderów”. Serwer nie ma możliwości samodzielnego rozszerzenia tego zakresu.

### Formularze wywoływania (Elicitation): Domyślny tryb formularza

Metoda `elicitation/create` przyjmuje strukturę formularza oraz komunikat dla użytkownika:

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

Klient wyświetla formularz użytkownikowi, pobiera uzupełnione dane i odsyła wynik:

```json
{
  "action": "accept",
  "content": {"note_id": "note-14", "confirm": true}
}
```

Trzy możliwe statusy akcji użytkownika: `accept` (użytkownik zatwierdził i uzupełnił dane), `decline` (użytkownik odrzucił/zamknął formularz) oraz `cancel` (użytkownik przerwał wykonywanie całego narzędzia).

Schematy formularzy w pierwszej wersji standardu muszą być płaskie – obiekty zagnieżdżone nie są wspierane. Zestawy SDK zazwyczaj odrzucają struktury zawierające więcej niż jedną warstwę właściwości.

### Wywoływanie w trybie adresu URL (URL Mode - SEP-1036)

Standard wprowadzony 25.11.2025 r. Zamiast schematu formularza serwer przesyła adres URL:

```json
{
  "method": "elicitation/create",
  "params": {
    "message": "Sign in to GitHub",
    "url": "https://github.com/login/oauth/authorize?client_id=..."
  }
}
```

Klient otwiera wskazany adres URL w przeglądarce i oczekuje na powrót użytkownika. Jest to przydatne do realizacji procesów autoryzacji OAuth, potwierdzania płatności czy podpisywania dokumentów, gdzie prosty formularz jest niewystarczający.

Uwaga dotycząca wersji eksperymentalnych: format odpowiedzi dla SEP-1036 nie jest ostatecznie ustalony; część SDK zwraca adres URL wywołania zwrotnego (callback URL), a część token autoryzacyjny. Przed wdrożeniem produkcyjnym należy dokładnie zapoznać się z dokumentacją używanej wersji SDK.

### Kiedy stosować formularze wywoływania (Elicitation)?

- Potwierdzanie nieodwracalnych akcji (np. usuwanie danych – flaga destructive + wywołanie formularza).
- Rozstrzyganie niejednoznaczności (wybór jednego elementu z listy dopasowań).
- Wstępna konfiguracja przy pierwszym uruchomieniu (pobieranie kluczy API, ścieżek lub preferencji).
- Integracja z zewnętrznymi systemami autoryzacji (tryb URL).

### Kiedy NIE stosować wywoływania?

- Do uzupełniania parametrów narzędzia, o które model mógłby samodzielnie dopytać użytkownika na czacie. W takich przypadkach pozwól modelowi na standardową konwersację.
- Do operacji o wysokiej częstotliwości. Wyświetlenie formularza przerywa proces generowania; nie należy go wywoływać w pętli.
- Do walidacji, którą serwer może przeprowadzić samodzielnie. Lepiej zwrócić błąd z narzędzia i pozwolić modelowi wyjaśnić problem użytkownikowi na czacie.

### Integracja Human-in-the-Loop

Połączenie formularzy wywoływania (Elicitation) oraz próbkowania (Sampling) pozwala na wdrożenie pełnego modelu Human-in-the-Loop w MCP. Procesy agentyczne serwera mogą być wstrzymywane w celu pobrania decyzji użytkownika (elicitation) lub konsultowane z modelem klienta (sampling). Faza 13 · 11 omawia próbkowanie, ta lekcja skupia się na wywoływaniu. Połączenie obu technik daje pełną kontrolę nad pętlą wykonawczą.

## Instrukcja użycia

Plik `code/main.py` rozbudowuje serwer notatek o:

- Obsługę żądania `roots/list` wysyłanego po odebraniu powiadomienia o zmianie katalogów głównych.
- Narzędzie `notes_delete` wykorzystujące `elicitation/create` do wyboru właściwej notatki w przypadku wielu dopasowań.
- Narzędzie `notes_setup` wykorzystujące wywoływanie w trybie URL do otwarcia strony konfiguracyjnej (proces zasymulowany).
- Walidację ścieżek blokującą operacje na plikach zlokalizowanych poza zadeklarowanymi katalogami głównymi (roots).

Skrypt demonstracyjny prezentuje trzy scenariusze: poprawne usunięcie (jedno dopasowanie), rozstrzyganie niejednoznaczności (trzy dopasowania – wywołanie formularza) oraz próba zapisu pliku poza dozwoloną ścieżką (odmowa dostępu).

## Wynik wdrożenia

W ramach tej lekcji powstaje plik `outputs/skill-elicitation-form-designer.md`. Narzędzie to, na podstawie specyfikacji akcji wymagającej weryfikacji użytkownika, projektuje strukturę formularza elicitation oraz komunikaty dla użytkownika.

## Ćwiczenia

1. Uruchom `code/main.py`. Przetestuj ścieżkę ujednoznaczniania parametrów i upewnij się, że odpowiedź z formularza użytkownika trafia z powrotem do kodu narzędzia.

2. Dodaj nowe narzędzie `notes_archive`, które przed wykonaniem zawsze wymaga potwierdzenia akcji przez użytkownika (flaga destructive). Oceń jakość UX w porównaniu do dopytania użytkownika przez model na czacie.

3. Zaimplementuj wywoływanie w trybie URL dla wstępnej autoryzacji w serwisie GitHub (OAuth flow). Uwzględnij eksperymentalny charakter SEP-1036 i dodaj weryfikację wersji SDK.

4. Rozbuduj obsługę powiadomienia `roots/list_changed` – po odebraniu powiadomienia serwer powinien natychmiast zweryfikować i zamknąć uchwyty do plików, które znalazły się poza nowym zakresem uprawnień.

5. Przeanalizuj dyskusję wokół propozycji SEP-1036 w repozytorium GitHub protokołu MCP. Wskaż jedno otwarte zagadnienie wpływające na sposób obsługi adresów callback przez serwery.

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|----------------|--------------------------------------|
| Katalog główny (Root) | „Zakres uprawnień” | Ścieżka URI zadeklarowana przez klienta, do której dostęp ma serwer |
| `roots/list` | „Zapytanie o katalogi” | Metoda, w której serwer pobiera listę dozwolonych ścieżek od klienta |
| Zmiana katalogów | `notifications/roots/list_changed` | Powiadomienie wysyłane przez klienta po modyfikacji dozwolonych ścieżek |
| Wywoływanie (Elicitation) | „Formularz w locie” | Inicjowane przez serwer zapytanie o ustrukturyzowane dane od użytkownika |
| `elicitation/create` | „Utworzenie wywołania” | Metoda JSON-RPC służąca do żądania wyświetlenia formularza |
| Tryb formularza | „Formularz schematowy” | Płaski formularz generowany w kliencie na podstawie JSON Schema |
| Tryb URL | „Przekierowanie OAuth” | Eksperymentalny tryb (SEP-1036) otwierający zewnętrzną stronę w przeglądarce |
| Statusy decyzji | `accept` / `decline` / `cancel` | Trzy możliwe odpowiedzi użytkownika na żądanie formularza |
| Ujednoznacznienie | „Wybór z listy” | Scenariusz, w którym użytkownik musi wskazać jeden z wielu pasujących obiektów |
| Płaski formularz | „Formularz jednowarstwowy” | Wymóg specyfikacji zabraniający stosowania zagnieżdżonych obiektów w schemacie |

## Dalsze czytanie

- [Model Context Protocol — Roots Specification](https://modelcontextprotocol.io/specification/draft/client/roots) — dokumentacja techniczna komponentu roots.
- [Model Context Protocol — Elicitation Specification](https://modelcontextprotocol.io/specification/draft/client/elicitation) — dokumentacja techniczna komponentu elicitation.
- [Cisco — What's New in MCP: Elicitation, Structured Content, and OAuth](https://blogs.cisco.com/developer/whats-new-in-mcp-elicitation-structured-content-and-oauth-enhancements) — omówienie rozszerzeń z wersji specyfikacji z listopada 2025.
- [MCP — GitHub SEP-1036](https://github.com/modelcontextprotocol/modelcontextprotocol) — specyfikacja i status prac nad trybem URL (eksperymentalne).
- [The New Stack — How Elicitation in MCP Brings Human-in-the-Loop to AI Tools](https://thenewstack.io/how-elicitation-in-mcp-brings-human-in-the-loop-to-ai-tools/) — analiza interfejsów użytkownika i integracji z procesami biznesowymi.
