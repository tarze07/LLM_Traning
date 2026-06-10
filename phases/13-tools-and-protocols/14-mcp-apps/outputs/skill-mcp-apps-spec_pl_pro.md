---

name: mcp-apps-spec
description: Przygotuj pełny kontrakt aplikacji MCP dla narzędzia wymagającego interaktywnego widoku graficznego (UI).
version: 1.0.0
phase: 13
lesson: 14
tags: [mcp, apps, ui-resources, csp, iframe-sandbox]

---

Na podstawie specyfikacji narzędzia wymagającego interaktywnego interfejsu graficznego (np. oś czasu, formularz, dashboard, mapa, wykres) utwórz kontrakt aplikacji MCP.

Wygeneruj:

1. Kanoniczny adres URI z protokołem `ui://`. Zdefiniuj unikalny adres wskazujący na zasób interfejsu użytkownika (np. `ui://notes/timeline`).
2. Struktura odpowiedzi narzędzia. Zdefiniuj obiekt odpowiedzi zawierający tablicę `content[]` z tekstem wprowadzającym (`text`) oraz blokiem `ui_resource`, a także uzupełniony obiekt metadanych `_meta.ui`.
3. Konfiguracja Content Security Policy (CSP). Przygotuj minimalną listę dozwolonych źródeł dla dyrektyw `default-src`, `script-src`, `connect-src`, `img-src` oraz `style-src`. Unikaj stosowania `'unsafe-inline'`, o ile to możliwe.
4. Wykaz uprawnień. Określ wymagany dostęp do kamery, mikrofonu, geolokalizacji lub sieci (pozostaw pusty, jeśli dodatkowe uprawnienia sprzętowe nie są konieczne).
5. Komunikacja postMessage. Określ, które metody z przestrzeni `host.*` będą wywoływane przez kod w ramce iframe oraz jakie dane będą zwracane przez aplikację hosta.
6. Lista kontrolna bezpieczeństwa (Security Checklist). Wdrożenie wizualnego odróżnienia od hosta, zapobieganie ataku clickjacking, rygorystyczne reguły connect-src oraz sanityzacja kodu HTML w przypadku renderowania danych wprowadzonych przez użytkownika.

Kryteria odrzucenia (Twarde reguły):
- Zdefiniowanie reguł CSP z maską `default-src *` (poważna podatność bezpieczeństwa).
- Żądanie uprawnień (`permissions`), które nie są niezbędne do prawidłowego działania interfejsu (naruszenie zasady minimalnych uprawnień).
- Ładowanie zewnętrznych skryptów w zasobie `ui://` (wszystkie zależności muszą być spakowane lokalnie).
- Renderowanie kodu HTML zawierającego dane wprowadzone przez użytkownika bez uprzedniej sanityzacji (podatność typu XSS).

Zasady odmowy usługi:
- Jeśli interfejs użytkownika ma służyć wyłącznie prezentacji statycznych danych, odmów projektowania aplikacji MCP i zaleć zwrócenie standardowej treści tekstowej.
- Jeśli cel może zostać zrealizowany przy użyciu natywnych widżetów hosta (np. paski postępu, okna potwierdzenia), rekomenduj ich użycie w pierwszej kolejności.
- Jeśli aplikacja docelowa (host) nie wspiera jeszcze standardu aplikacji MCP (stan na rok 2026: stabilne wersje VS Code, Zed, Windsurf), zdefiniuj alternatywną ścieżkę generowania danych tekstowych (fallback).

Format wyjściowy: Jednostronicowy kontrakt zawierający definicję URI `ui://`, strukturę odpowiedzi narzędzia w JSON, reguły CSP, listę uprawnień, schemat metod postMessage oraz listę kontrolną bezpieczeństwa. Na końcu wskaż minimalną wersję aplikacji klienckiej (hosta) zdolnej do wyrenderowania tego interfejsu.
