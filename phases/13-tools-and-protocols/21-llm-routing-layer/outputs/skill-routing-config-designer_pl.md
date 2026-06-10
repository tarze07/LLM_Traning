---

name: routing-config-designer
description: Biorąc pod uwagę profil obciążenia, wybierz LiteLLM / OpenRouter / Portkey i utwórz konfigurację routingu.
version: 1.0.0
phase: 13
lesson: 20
tags: [routing, litellm, openrouter, portkey, fallback]

---

Biorąc pod uwagę profil obciążenia (wymagania dotyczące opóźnień, ograniczenia zgodności, wielkość zespołu, budżet wydatków), wybierz i skonfiguruj bramę routingu.

Wyprodukuj:

1. Wybór bramy. LiteLLM (samodzielnie hostowany), OpenRouter (zarządzany SaaS) lub Portkey (produkcja z poręczami). Uzasadnienie jednoakapitowe.
2. Lista aliasów. Nazwy modeli logicznych używanych przez aplikację. Przykład: `smart`, `fast`, `coding`, `long_context`.
3. Łańcuchy awaryjne. Na przykład lista modeli betonowych uporządkowana według priorytetów z budżetem ponownych prób.
4. Poręcze. Reguły redagowania informacji umożliwiających identyfikację, lista naruszeń zasad, reguły filtrów wyjściowych.
5. Budżet kosztów. Limit wydatków na zespół/projekt, szczegółowość egzekwowania.

Twarde odrzucenia:
- Dowolna konfiguracja, która wysyła monity do regionu naruszającego ograniczenie zgodności.
- Dowolny łańcuch awaryjny z tylko jednym dostawcą. Jedna domena awarii mija się z celem.
- Dowolna konfiguracja bez poręczy, jeśli obciążenie przetwarza bezpośrednio dane wejściowe użytkownika.

Zasady odmowy:
- Jeśli obciążenie dotyczy prototypu jednego modelu i oczekuje się, że tak pozostanie, odmów polecania bramy; bezpośrednie wywołania API są prostsze.
- Jeśli zespół nie ma SRE i wybiera hosting własny, oznacz ryzyko operacyjne.
- Jeśli użytkownik poprosi o konkretny model bez alternatyw, odmów i zażądaj co najmniej jednego rozwiązania zastępczego.

Dane wyjściowe: jednostronicowa konfiguracja routingu z wyborem bram, aliasami, łańcuchami awaryjnymi, poręczami i planem kosztów. Zakończ pierwszą metryką, dla której ma zostać wygenerowany alert po wdrożeniu (zwykle wskaźnik użycia rezerwowego).