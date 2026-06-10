---

name: disaggregation-decider
description: Zdecyduj, czy zastosować zdezagregowane wstępne wypełnianie/dekodowanie (Dynamo lub llm-d) dla danego obciążenia i klastra. Określ ilościowo współczynniki wstępnego wypełnienia: dekodowania, koszt transferu KV i oczekiwane oszczędności.
version: 1.0.0
phase: 17
lesson: 17
tags: [disaggregated-serving, dynamo, llm-d, nixl, kv-transfer, prefill-decode]

---

Biorąc pod uwagę profil obciążenia (rozkład długości podpowiedzi/wyjść, model, współbieżność), topologię klastra (procesory graficzne, sieć szkieletowa, dostępność RDMA) i bieżący koszt obsługi, należy podjąć decyzję o dezagregacji.

Wyprodukuj:

1. Dezagregować? Tak/Nie z numerowanym uzasadnieniem. Linia bazowa: podpowiedzi > 512 ORAZ wyniki > 200. Struktura: dostępna pomoc RDMA; Tylko protokół TCP wydłuża próg rentowności.
2. Wybór stosu. NVIDIA Dynamo (zarządzany orkiestrator powyżej vLLM/SGLang/TRT-LLM) lub llm-d (usługi natywne Kubernetes). Dopasuj do kontekstu operacyjnego.
3. Stosunek wstępnego wypełnienia do dekodowania. Użyj odczytów programu Dynamo Planner Profiler lub oblicz na podstawie kształtu obciążenia (wstępne wypełnienie TFLOPS vs dekodowanie bajtów/s). Przykład: 2 wstępne wypełnienie: 1 dekodowanie dla ciężkich RAG; 1:2 dla dużej wydajności.
4. Plan transferu KV. Transport nazwany (NIXL przez InfiniBand / RDMA / TCP). Oblicz podatek od przeniesienia na żądanie dla swojego monitu P99.
5. Integracja routera. Router obsługujący pamięć podręczną (faza 17 · 11) musi znajdować się z przodu — dezagregacja bez dopasowania prefiksów powoduje utratę wygranej w pamięci podręcznej.
6. Oczekiwane oszczędności. Oblicz w porównaniu z kolokowaną linią bazową; przytocz opublikowany przypadek (30-40% przy tej samej umowie SLA).

Twarde odrzucenia:
- Dezagregacja obciążeń z krótkim monitem (<512 tokens). Refuse — the transfer tax dominates.
- Deploying without a cache-aware router. Refuse — blind routing negates the KV locality.
- Ignoring topology (rack packing). Refuse — KV transfer over multi-rack hops costs more than RDMA on the same rack.

Refusal rules:
- If the cluster has < 4 GPUs, refuse — not enough pool diversity for disaggregation to pay off.
- If no RDMA/InfiniBand and no plans, note that TCP raises the break-even to prompts >2K; ponowna ocena.
— Jeśli zespół nie może obsługiwać dwóch pul procesorów graficznych ze skalowaniem według ról, odrzuć llm-d i wybierz Dynamo jako zarządzaną alternatywę.

Dane wyjściowe: jednostronicowa decyzja zawierająca szczegółowe informacje na temat Y/N, wyboru stosu, proporcji, transportu, routera i oczekiwanych oszczędności. Zakończ pojedynczą metryką w celu sprawdzenia: opóźnienie transferu KV P99; bramka po przekroczeniu progu określonego w planie.