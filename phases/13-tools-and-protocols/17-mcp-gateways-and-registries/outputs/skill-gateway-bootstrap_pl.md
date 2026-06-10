---

name: gateway-bootstrap
description: Utwórz specyfikację konfiguracji bramy, biorąc pod uwagę użytkowników, zaplecze i ograniczenia dotyczące zgodności.
version: 1.0.0
phase: 13
lesson: 17
tags: [mcp, gateway, rbac, audit, policy]

---

Biorąc pod uwagę plan MCP przedsiębiorstwa (użytkownicy, zaplecze, ograniczenia zgodności), utwórz specyfikację konfiguracji bramy.

Wyprodukuj:

1. Lista zaplecza. Każdy z własnym rejestrem (Official / Glama / Custom), nazwą kanoniczną (reverse-DNS), przypiętymi skrótami opisu.
2. Lista użytkowników. Każdy z rolą i zestawem dozwolonych narzędzi.
3. Macierz RBAC. Jeden wiersz na użytkownika x narzędzie zaplecza z funkcją zezwalania/odmawiania.
4. Limity stawek. Limity seryjne i stałe na użytkownika; limity na narzędzie w przypadku drogich narzędzi.
5. Plan audytu. Miejsce docelowe dziennika (plik, OpenTelemetry, SIEM), przechowywanie, przechwycone pola.

Twarde odrzucenia:
- Dowolny backend spoza oficjalnego rejestru bez wyraźnej zgody administratora.
- Dowolna reguła RBAC zezwalająca wszystkim użytkownikom na wszystkie narzędzia. Eksplozja przywilejów.
- Dowolny plan audytu bez niezmiennej pamięci. Zgodność nie powiodła się.

Zasady odmowy:
- Jeśli populacja programistów przekracza 100 bez zdefiniowanych ról, odmów ładowania początkowego i wymagaj co najmniej trzech ról.
- Jeśli plan nie identyfikuje dostawcy tożsamości OAuth 2.1, odmów i zaleć najpierw przyjęcie Keycloak lub Auth0.
- Jeśli jakikolwiek backend używa stdio, odmów proxy przez bramę HTTP; serwery stdio działają lokalnie według programisty.

Dane wyjściowe: jednostronicowy dokument konfiguracyjny z listą zaplecza, listą użytkowników, macierzą RBAC, limitami szybkości i planem audytu. Zakończ pojedynczą zasadą, którą zespół powinien wdrożyć w pierwszej kolejności.