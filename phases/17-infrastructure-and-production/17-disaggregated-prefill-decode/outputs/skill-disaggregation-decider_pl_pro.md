---

name: disaggregation-decider
description: Podejmowanie decyzji o wdrożeniu zdezagregowanej architektury prefill/decode (za pomocą Dynamo lub llm-d) dla danego obciążenia i klastra GPU. Szacowanie proporcji prefill:decode, kosztów transferu KV-cache i prognozowanych oszczędności.
version: 1.0.0
phase: 17
lesson: 17
tags: [disaggregated-serving, dynamo, llm-d, nixl, kv-transfer, prefill-decode]

---

Na podstawie profilu obciążenia (rozkład długości promptów/odpowiedzi, model, stopień współbieżności), topologii klastra (GPU, infrastruktura sieciowa, dostępność RDMA) oraz dotychczasowych kosztów utrzymania, podejmij decyzję o wdrożeniu dezagregacji.

Przygotuj:

1. Rekomendację (Dezagregacja: Tak/Nie) wraz z punktowym uzasadnieniem. Warunek brzegowy: prompty > 512 tokenów ORAZ generowane odpowiedzi > 200 tokenów. Czynniki infrastrukturalne: dostępność sieci RDMA (przetwarzanie wyłącznie po TCP podnosi próg rentowności).
2. Wybór stosu technologicznego: NVIDIA Dynamo (zarządzany orkiestrator nad silnikami vLLM/SGLang/TRT-LLM) lub llm-d (rozwiązanie natywne dla Kubernetes). Dobierz rozwiązanie do standardów operacyjnych zespołu.
3. Proporcje prefill do decode (Prefill-to-Decode Ratio): Na podstawie danych z Dynamo Planner Profiler lub własnych obliczeń (obciążenie obliczeniowe prefill w TFLOPS vs przepustowość decode w GB/s). Przykład: stosunek 2:1 (dwie instancje prefill na jedną decode) dla systemów z ciężkim RAG; 1:2 dla zadań z długimi odpowiedziami.
4. Plan transferu KV-cache: Zdefiniowanie protokołu transportowego (NIXL przez InfiniBand / RDMA / TCP). Oblicz narzut czasowy (opóźnienie transferu) dla 99. percentyla (P99) rozmiaru promptu.
5. Integrację z routerem zorientowanym na cache (Cache-Aware Router): Router (opisany w fazie 17 · 11) musi znajdować się na wejściu systemu. Dezagregacja bez dopasowywania prefiksów cache pozbawia system kluczowych oszczędności.
6. Prognozę oszczędności: Kalkulację w porównaniu do tradycyjnej architektury kolokowanej (np. oszczędności na poziomie 30-40% przy zachowaniu identycznego SLA).

Kryteria odrzucenia planu:
- Wdrażanie dezagregacji dla zadań z krótkimi promptami (<512 tokenów). Odrzuć – narzut czasowy transferu sieciowego zniweluje zyski.
- Projekt bez routera uwzględniającego lokalizację cache (cache-aware). Odrzuć – losowy routing uniemożliwia lokalne dopasowanie KV-cache.
- Ignorowanie topologii sieci klastra (rack packing). Odrzuć – transfer KV-cache między szafami serwerowymi (multi-rack hops) drastycznie podnosi opóźnienia w porównaniu z komunikacją RDMA w obrębie jednego racka.

Zasady odmowy/zastrzeżenia:
- Jeśli klaster dysponuje mniej niż 4 układami GPU, odrzuć projekt – zbyt mała skala infrastruktury, by wydzielanie dedykowanych pul maszyn przyniosło zysk.
- W przypadku braku sieci RDMA/InfiniBand zaznacz, że korzystanie z TCP podnosi próg opłacalności do promptów o długości >2K tokenów.
- Jeśli zespół nie posiada kompetencji do zarządzania niezależnie skalowanymi pulami GPU w Kubernetes, odrzuć llm-d i zarekomenduj orkiestrację przy użyciu NVIDIA Dynamo.

Format końcowy: Jednostronicowa decyzja architektoniczna określająca status wdrożenia (Tak/Nie), rekomendowany stos technologiczny, proporcje pul maszyn, protokół transportu KV-cache, logikę routera oraz szacowane oszczędności. Raport należy zakończyć zdefiniowaniem kluczowej metryki kontrolnej: opóźnienia transferu KV-cache w percentylu P99.
