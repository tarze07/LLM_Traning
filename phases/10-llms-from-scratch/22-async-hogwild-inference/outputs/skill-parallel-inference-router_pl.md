---

name: parallel-inference-router
description: Poprowadź obciążenie rozumowaniem pomiędzy strategiami głosowania, drzewa myśli, wielu agentów, Hogwild! i spekulatywnym dekodowaniem.
version: 1.0.0
phase: 10
lesson: 22
tags: [parallel-inference, hogwild, speculative-decoding, tree-of-thought, multi-agent, reasoning]

---

Biorąc pod uwagę uzasadniony profil obciążenia (budżet tokenów na zadanie, charakterystykę równoległości zadań, rodzinę modeli, cel wdrożenia, budżet opóźnień), zaleć strategię lub kombinację wnioskowania równoległego.

Wyprodukuj:

1. Klasyfikacja zadań. Długie rozumowanie (ponad 5 tys. tokenów), średni ciąg myślowy (1 tys.-5 tys.), krótki czat (poniżej 1 tys.) lub klasyfikacja. Podejmuje decyzję za pierwszym podejściem.
2. Oś równoległości. Wewnątrz sekwencji (dekodowanie spekulatywne) vs w sekwencji (głosowanie, Hogwild!, wielu agentów). W przypadku większości obciążeń najpierw korzysta się z osi wewnątrz sekwencji.
3. Rekomendacja strategii. Wybierz spośród: tylko dekodowanie spekulatywne (bezpieczne ustawienie domyślne dla dowolnego obciążenia powyżej 100 tokenów), spekulatywne + Hogwild! (długie rozumowanie o strukturze możliwej do zrównoleglenia), drzewo myśli (jawne problemy rozgałęzień i przycinania), wieloagentowy (problemy ze specjalizacją ról), zespół do głosowania (klasyfikacja o wysokiej stawce).
4. Ustawienia parametrów. Do dekodowania spekulatywnego: rodzina robocza (domyślnie EAGLE-3) i `N` (umiejętność fazy 10 · 15). Dla Hogwild!: liczba pracowników N (2 do 4, rzadko więcej), szablon monitu o koordynację, potwierdzenie wdrożenia na jednym węźle.
5. Łączne oszacowanie przyspieszenia. Jeśli łączysz dekodowanie spekulatywne z Hogwild!, zgłoś przyspieszenie multiplikatywne (typowy zakres: 3x spec * 1,5-2x Hogwild! = 4,5-6x).

Twarde odrzucenia:
- Dziki! dla dowolnego obciążenia poniżej 2000 tokenów. Dominuje obciążenie koordynacyjne.
- Dziki! na modelach pozbawionych rozumowania (brak wyłaniającej się koordynacji).
- Wieloagentowy framework dla problemów, które nie mają naturalnego rozkładu ról.
- Drzewo myślenia bez wyraźnej logiki rozgałęziania i przycinania (w przeciwnym razie strategia ogranicza się do liniowego CoT).
- Uciekam Hogwildzie! między węzłami (synchronizacja pamięci podręcznej między węzłami jest zbyt wolna).

Zasady odmowy:
- Jeśli Twoim obciążeniem są badania eksperymentalne, polecam Hogwild! jako eksperyment, a nie zakład produkcyjny. Przyspieszenie zależy od zadania, a wdrożenie w świecie rzeczywistym jest rzadkie (stan na kwiecień 2026 r.).
- Jeśli użytkownik poprosi o gwarantowane przyspieszenie, odmów i wyjaśnij, że tylko dekodowanie spekulacyjne ma właściwość silnej gwarancji (zachowana jest dystrybucja wyników). Hogwild! jest empiryczny.
- Jeśli użytkownik ma ograniczoną pamięć VRAM, odmów Hogwild! N>2 — każdy proces roboczy potrzebuje własnej pamięci aktywacyjnej, mimo że pamięć podręczna jest współdzielona.

Wynik: jednostronicowa rekomendacja zawierająca klasyfikację zadań, oś równoległości, strategię, parametry i łączne szacunki przyspieszenia. Zakończ akapitem „wyzwalacz wycofywania” wymieniającym konkretną metrykę opóźnienia lub dokładności, która uzasadniałaby powrót do samego dekodowania spekulatywnego w przypadku Hogwild! nie opłaca się w pierwszych 100 żądaniach produkcyjnych.