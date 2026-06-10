---

name: diff-attention-integrator
description: Plan integracji umożliwiający dodanie Differential Attention V2 do nowego biegu przedtreningowego lub dostrojenia LoRA.
version: 1.0.0
phase: 10
lesson: 16
tags: [differential-attention, diff-transformer, long-context, flash-attention, pre-training, lora]

---

Biorąc pod uwagę architekturę modelu (ukryty, głowice, głowice KV, warstwy, d_head), docelową długość kontekstu, halucynację lub profil długiego kontekstu (tryby awarii na istniejących ewaluacjach) i budżet szkoleniowy (dostępne tokeny, godziny GPU), utwórz plan integracji dla DIFF V2.

Wyprodukuj:

1. Tryb integracji. Szkolenie od podstaw przed szkoleniem, wymiana architektury w trakcie szkolenia lub dostrajanie LoRA na projekcjach Q. Uzasadnij wybór biorąc pod uwagę budżet szkoleniowy i dostępne obciążenia.
2. Różnica w architekturze. Konkretna lista zmian pole po polu: które prognozy rosną, które pozostają takie same, jaką liczbę parametrów dodajesz i gdzie odejmowanie jest umieszczane w bloku uwagi. Uwzględnij harmonogram `lambda_init` według głębokości warstwy (`0.8 - 0.6 * exp(-0.3 * (depth - 1))` jest domyślnym ustawieniem papieru; dostosuj według głębokości, jeśli telemetria warstwowa wykazuje niestabilność).
3. Wybór jądra. Potwierdź obsługę FlashAttention 2 lub 3, biorąc pod uwagę podwojenie liczby pracowników w wersji 2. Odrzuć niestandardową ścieżkę jądra V1, chyba że użytkownik wyraźnie potrzebuje jej w celu zapewnienia odtwarzalności.
4. Budżet pamięci. Pamięć podręczna KV pozostaje na poziomie podstawowym (głowice KV niezmienione). Oblicz różnicę pamięci aktywacji na token (dodatkowe głowice Q, dodatkowe obliczenia). Podawaj liczby bezwzględne w kontekście docelowym.
5. Plan stabilizacji treningu. Opisz, co należy monitorować: dryf `lambda` na warstwę, entropia uwagi na głowę, wariancja gradientu w projekcjach Q. Nazwij konkretną metrykę, która powinna wywołać wycofanie uwagi do punktu bazowego, jeśli dane telemetryczne wskazują na rozbieżność.

Twarde odrzucenia:
- Dodanie uwagi DIFF do wstępnie wytrenowanego modelu bez ciągłego szkolenia wstępnego. Dryf dystrybucji wyników — nie jest to naprawa typu drop-in.
- DIFF V1 dla każdej nowej serii po kwietniu 2026. V2 jest wyraźnie lepszy we wszystkich zmierzonych wymiarach.
- Integracja DIFF bez włączania danych szkoleniowych o długim kontekście. Korzyść pokazuje tylko powyżej 32 tys.
- Zmiana `lambda_init` na wartość ujemną bez kontrolowanego eksperymentu. Ujemna init odejmuje więcej niż poziom szumów i załamuje szkolenie.

Zasady odmowy:
- Jeśli kontekst docelowy jest poniżej 16 tys., odmów integracji i zaleć standardową uwagę. Koszt dodanego parametru nie jest uzasadniony argumentem dotyczącym poziomu szumów.
- Jeżeli użytkownik nie może dostarczyć danych oceniających o długim kontekście (LIŃKA, igła w stogu siana, MultiNeedle), odmów i najpierw poproś o dane kalibracyjne.
- Jeśli użytkownik korzysta ze stosu w wersji wcześniejszej niż FlashAttention-2, odmów i zalecaj aktualizację stosu przed próbą integracji.

Dane wyjściowe: jednostronicowy tryb listy planu integracji, delta licznika parametrów, wpływ pamięci podręcznej KV, potwierdzenie FlashAttention, harmonogram `lambda` i 3-metryczna płytka monitorująca. Zakończ akapitem „kryterium sukcesu” podającym konkretną liczbę ewaluacyjną o długim kontekście (delta punktu procentowego na RULER 64k lub odpowiednik), która uzasadniałaby utrzymanie DIFF V2 w architekturze zamiast przywracania.