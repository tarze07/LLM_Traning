---

name: multi-region-router
description: Zaprojektuj wieloregionowy plan routingu LLM z lokalizacją pamięci podręcznej KV, granicami miejsca zamieszkania, manifestem DR i kwartalną analizą przełączania awaryjnego.
version: 1.0.0
phase: 17
lesson: 11
tags: [multi-region, kv-cache, routing, dr, bedrock-cri, vllm-router, llm-d, gorgo]

---

Biorąc pod uwagę zakres regionów, granice rezydencji, oczekiwaną różnorodność pamięci podręcznej prefiksów i umowę SLA TTFT, utwórz wieloregionowy plan routingu i odzyskiwania po awarii.

Wyprodukuj:

1. Wybór routera. Wybierz router obsługujący pamięć podręczną (router vLLM, router llm-d) i opisz kanał zdarzeń KV. Podaj algorytm mieszania przedrostków (np. przewijanie 512 tokenów) i rozstrzyganie rozstrzygnięć (najmniejsza głębokość kolejki).
2. Polityka routingu. Minimalizacja wstępnego napełniania + RTT na poziomie regionalnym czy globalna (w stylu GORGO)? Uzasadnij rozkładem długości podpowiedzi — długie podpowiedzi (> 8 tys. tokenów) korzystają z routingu między regionami; krótkie podpowiedzi nie.
3. Podział miejsca zamieszkania. Przed jakąkolwiek optymalizacją: które żądania są powiązane z jakimi regionami ze względów prawnych (RODO, HIPAA). Zabroń routingu między rezydencjami, nawet jeśli poprawi się TTFT.
4. Komercyjna warstwa CRI. Zalecenia, czy włączyć wnioskowanie międzyregionalne Bedrock lub bramę wieloklastrową GKE jako warstwę dostępności. Wyraźnie zaznacz, że ta warstwa NIE jest optymalizacją TTFT.
5. Manifest DR. Minimum trzy pliki (repozytorium HF + konfiguracja silnika + manifest wdrożenia). Sprawdź, czy tokenizer, konfiguracje kwantyzacji, RoPE, szablony czatów i adaptery LoRA są dołączone. Określ magazyn (replikacja międzyregionalna S3, wieloregionowy GCS).
6. Ćwiczenie trybu awaryjnego. Kadencja kwartalna. Kto go uruchamia, co jest mierzone (RTO, RPO, czas nagrzewania pamięci podręcznej). Cel: 30-minutowy RTO dopasowany do rzeczywistego ćwiczenia JPMorgan z 2024 r.

Twarde odrzucenia:
- Ignorowanie miejsca zamieszkania w celu optymalizacji routingu. Odmów – naruszenie RODO jest ważniejsze od zysku TTFT.
— Twierdzenie, że Bedrock CRI „rozwiązuje” routing między regionami. Odmów — CRI to dostępność, a nie TTFT.
- Tylko ciężarki zapasowe. Odmów — podaj statystykę niepowodzeń DR na poziomie 32% i wymagaj manifestu składającego się z trzech plików.

Zasady odmowy:
- Jeśli zakres obejmuje tylko jeden region, odrzuć plan — pojedynczy region ma różne tryby awarii (obejmuje to faza 17 · 03).
- Jeśli miejsce zamieszkania i umowa SLA TTFT są niezgodne (np. miejsce zamieszkania w UE wymusza wstępne wypełnienie zimnego prefiksu na żądanie z P99 TTFT < 100 ms przy monitach 8K), odmów obiecania umowy SLA i eskaluj wymagania dotyczące produktu.

Dane wyjściowe: jednostronicowy plan nazewnictwa routera, zasady routingu, partycje rezydencji, stan warstwy CRI, manifest DR, kwartalny właściciel ćwiczeń. Zakończ pojedynczym wskaźnikiem, o którym ma być wyświetlany alert: współczynnik trafień w pamięci podręcznej prefiksów w różnych regionach spada poniżej progu określonego w planie.