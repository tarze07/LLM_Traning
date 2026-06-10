---

name: ai-tutor
description: Wyślij adaptacyjnego multimodalnego osobistego nauczyciela dla konkretnego przedmiotu ze śledzeniem wiedzy Bayesa, wykresem programu nauczania, filtrami bezpieczeństwa i mierzonym dwutygodniowym badaniem skuteczności.
version: 1.0.0
phase: 19
lesson: 17
tags: [capstone, tutor, adaptive, bkt, fsrs, livekit, multimodal, coppa]

---

Biorąc pod uwagę przedmiot (algebra K-12 lub wprowadzający Python), zbuduj osobistego nauczyciela z tekstem, głosem i danymi fotomatematycznymi, Bayesowskim modelem ucznia śledzącym wiedzę, wyborem koncepcji opartym na wykresie programu nauczania, pamięcią zgodną z COPPA i filtrami bezpieczeństwa. Przeprowadź dwutygodniowe badanie skuteczności z udziałem 10 uczniów.

Plan budowy:

1. Wykres programu nauczania w Neo4j: 50-150 węzłów koncepcyjnych z wymaganymi krawędziami i dołączoną treścią OER (OpenStax, Open Textbook).
2. Model ucznia: Bayesowskie śledzenie wiedzy z priorytetami dotyczącymi zgadywania/pomyłek/szybkości uczenia się według koncepcji; stan trwały na ucznia.
3. Polityka nauczyciela (LangGraph na Claude Sonnet 4.7 z buforowaniem podpowiedzi): read_signal ->select_concept (przejście po wykresie) -> scaffold (Socratic) -> update_mastery.
4. Pamięć: trwała epizodyczna pamięć agenta + magazyn semantyczny; Automatyczne usuwanie zgodne z COPPA po 1 roku; usuwanie dostępne dla rodziców.
5. Głos: Pracownik LiveKit Agents z Whisper-v3-turbo ASR i Cartesia Sonic-2 TTS; ponownie wykorzystać rurociąg Capstone 03.
6. Fotomatematyka: dots.ocr lub PaliGemma 2 do rozpoznawania równań; przekazywać ustrukturyzowane dane wejściowe nauczycielowi.
7. Bezpieczeństwo: wejście/wyjście Llama Guard 4; filtr dostosowany do wieku, blokujący samookaleczenia/dorosłość/przemoc; izolacja pamięci o zasięgu ucznia.
8. Cotygodniowe raporty postępu w formacie PDF na ucznia.
9. Badanie skuteczności: 10 uczniów, test wstępny (standaryzowany poziom wyjściowy składający się z 30 pytań), 2 tygodnie sesji (3/tydzień), post-test; porównać z nieadaptacyjną kohortą liniową.

Rubryka oceny:

| Waga | Kryterium | Pomiar |
|:-:|---|---|
| 25 | Delta wzmocnienia uczenia się | Delta przed/po teście w dwutygodniowym badaniu z udziałem 10 uczniów |
| 20 | Wierność sokratejska | Ocena rubryk na próbkach transkrypcji |
| 20 | Multimodalny UX | Spójność głosu + zdjęcia + tekstu od końca do końca |
| 20 | Bezpieczeństwo i prywatność | Wskaźnik zdawalności Llama Guard 4 + utrzymanie ze świadomością COPPA + izolacja między uczniami |
| 15 | Zakres programu nauczania i jakość wykresów | Pokrycie koncepcji + wymagana spójność wykresu |

Twarde odrzucenia:

- Zasady korepetytora, które zrzucają odpowiedzi zamiast zadawać kolejne pytanie. Sokratejski to trudny wymóg.
- Modele uczniów, które nie są aktualizowane podczas interakcji. BKT to podłoga.
- Pamięć bez przechowywania zgodnego z COPPA. Nie do przyjęcia dla publiczności K-12.
- Twierdzenia dotyczące skuteczności bez nieadaptacyjnej kohorty wyjściowej.

Zasady odmowy:

- Odmów wdrożenia bez Llama Guard 4 zarówno na wejściu, jak i na wyjściu.
- Odmawiaj utrwalania danych ucznia bez powierzchni usuwania dostępnej dla rodziców.
- Odmów twierdzenia, że ​​jest „adaptacyjny” bez jednoczesnego przedstawienia nieadaptacyjnej linii bazowej.

Dane wyjściowe: repozytorium zawierające wykres programu nauczania, model ucznia BKT, politykę nauczyciela LangGraph, multimodalne procedury obsługi danych wejściowych, potok głosowy LiveKit, potok bezpieczeństwa, panel rodzicielski, moduł badania skuteczności, okablowanie przed i po teście oraz zapis dokumentujący deltę przyrostu uczenia się w porównaniu z liniową linią bazową z przedziałami ufności.