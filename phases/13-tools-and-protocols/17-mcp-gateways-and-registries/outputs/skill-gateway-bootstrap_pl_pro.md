---

name: gateway-bootstrap
description: Utwórz specyfikację konfiguracji bramy sieciowej MCP na podstawie profilu użytkowników, serwerów backendowych oraz ograniczeń regulacyjnych (compliance).
version: 1.0.0
phase: 13
lesson: 17
tags: [mcp, gateway, rbac, audit, policy]

---

Na podstawie profilu wdrożenia MCP w przedsiębiorstwie (struktura użytkowników, zaplecza oraz wymogi zgodności) opracuj specyfikację konfiguracji bramy sieciowej.

Wygeneruj następujące sekcje:

1. Lista serwerów backendowych. Każdy z określeniem typu rejestru (Oficjalny / Glama / Własny), nazwą kanoniczną (reverse-DNS) oraz przypiętymi skrótami (SHA256) opisów narzędzi.
2. Lista ról i użytkowników. Zdefiniowane profile użytkowników wraz z przypisanymi rolami i dozwolonymi narzędziami.
3. Macierz RBAC. Tabela mapująca pary użytkownik x narzędzie backendowe z jasnym określeniem zezwolenia (allow) lub odmowy (deny).
4. Limitowanie żądań (Rate Limiting). Określenie limitów pakietowych (burst) oraz ciągłych (sustained) na użytkownika, a także dedykowanych limitów na wywołania kosztownych narzędzi.
5. Plan audytu. Miejsce zapisu logów (plik, OpenTelemetry, system SIEM), czas retencji danych oraz lista rejestrowanych pól.

Kategoryczne odrzucenia:
- Dowolny serwer backendowy spoza oficjalnego rejestru bez wyraźnej, udokumentowanej zgody administratora.
- Dowolna reguła RBAC dająca wszystkim użytkownikom dostęp do wszystkich narzędzi (naruszenie zasady najmniejszych uprawnień).
- Dowolny plan audytu bez niezmiennej (append-only / write-once) pamięci masowej na logi (naruszenie wymogów zgodności).

Reguły odmowy:
- Jeśli liczba deweloperów przekracza 100, a nie zdefiniowano konkretnych ról, odrzuć proces konfiguracji początkowej (bootstrap) i zażądaj utworzenia co najmniej trzech odrębnych ról.
- Jeśli projekt nie uwzględnia integracji z dostawcą tożsamości obsługującym OAuth 2.1, odrzuć go i zalecaj wdrożenie systemu Keycloak lub Auth0 w pierwszej kolejności.
- Jeśli którykolwiek z serwerów backendowych korzysta z transportu stdio, odrzuć próbę tunelowania go przez bramę HTTP. Serwery stdio powinny być uruchamiane lokalnie w środowisku dewelopera.

Format wyjściowy: Jednostronicowy dokument konfiguracyjny zawierający wykaz serwerów backendowych, listę użytkowników, macierz RBAC, parametry limitowania żądań oraz plan audytu. Na końcu wskaż jedną, kluczową regułę bezpieczeństwa, którą zespół powinien wdrożyć w pierwszej kolejności.
