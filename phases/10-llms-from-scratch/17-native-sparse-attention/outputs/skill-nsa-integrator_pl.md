---

name: nsa-integrator
description: Plan integracji dla Native Sparse Attention w długim kontekście przedtreningowym.
version: 1.0.0
phase: 10
lesson: 17
tags: [nsa, sparse-attention, long-context, pre-training, kernel-aligned, deepseek]

---

Biorąc pod uwagę specyfikację przedszkoleniową o długim kontekście (kontekst docelowy, architektura podstawowa, dostępne tokeny szkoleniowe, topologia procesora GPU, cel wdrożenia), utwórz plan integracji NSA.

Wyprodukuj:

1. Rozmiar bloku kompresyjnego `l`. Wybierz 32, 64 lub 128. Uzasadnij w kontekście docelowym: `l = 32` dla 16 tys.–32 tys., `l = 64` dla 64–128 tys., `l = 128` dla 256 tys. i więcej. Większy `l` oznacza mniej skompresowanych kluczy, ale grubszy sygnał routingu.
2. Liczba wybranych k najlepszych. Wybierz liczbę od 8 do 32. Wartość domyślna artykułu to 16. Uzasadnij w oparciu o docelowy zestaw zadań: zadania wymagające dużego rozumowania (matematyka, kodowanie) korzystają z wyższego współczynnika `k`, ponieważ precyzja wyboru jest ważniejsza. Zadania wymagające intensywnego odzyskiwania działają przy niższym `k`.
3. Okno przesuwne `W`. Wybierz 256, 512 lub 1024. Domyślnie 512. Krótszy w przypadku treści o dużej strukturze (kodzie), gdzie wystarczający jest kontekst lokalny; dłużej dla prozy.
4. Brama MLP. Określ szerokość i inicjalizację. Domyślnie: warstwa liniowa od `hidden` do 3, z aktywacją `sigmoid` lub `softplus`. Ostrzegaj, jeśli ciężary bramki opadną na korzyść jednej gałęzi — oznacza to, że `l`, `k` lub `W` jest źle dostrojone.
5. Wybór jądra. Potwierdź dostępność jądra Triton lub CUDA dla docelowego akceleratora. Odrzuć powrót do gęstej uwagi podczas wnioskowania (całym celem NSA jest zapisanie obliczeń dekodowania). Jeśli istnieją tylko jądra do przodu, a nie do tyłu, odmów szkolenia wstępnego i zaleć kontynuację szkolenia na istniejących gęstych punktach kontrolnych.

Twarde odrzucenia:
- NSA na modelu wstępnie przeszkolonym z dużą uwagą, bez ciągłego szkolenia wstępnego. Nie można przykręcić przy wyciąganiu wniosków.
- Kontekst docelowy poniżej 16 tys. Dominuje trójgałęziowy napowietrznik.
- Wdrożenia oparte wyłącznie na wnioskowaniu na stosach bez obsługi jądra NSA. Zamiast tego polecam MLA lub okno przesuwne.

Zasady odmowy:
- Jeśli dane oceniające w długim kontekście (RULER, LongBench, igła w stogu siana) nie są dostępne, odmów i najpierw poproś o dane kalibracyjne.
- Jeżeli w dystrybucji kontekstu danych szkoleniowych dominują krótkie sekwencje, należy odmówić i zalecić ponowne ważenie danych przed integracją NSA.
- Jeśli akcelerator jest starszy niż A100, odmów — zalety jądra NSA zakładają hierarchie pamięci H100/H200/MI300.

Dane wyjściowe: jednostronicowy plan integracji zawierający listę `l`, `k`, `W`, konfigurację bramy, ścieżkę jądra i oczekiwane oszczędności obliczeniowe w kontekście docelowym. Zakończ akapitem „kryterium sukcesu”: konkretną liczbą RULER lub LongBench (punkty procentowe w porównaniu z dopasowaną wartością bazową gęstej uwagi), która uzasadnia utrzymanie NSA. Uwzględnij wyzwalacz wycofywania — próg metryki, poniżej którego architektura powinna zostać przywrócona do MLA lub gęstego GQA.