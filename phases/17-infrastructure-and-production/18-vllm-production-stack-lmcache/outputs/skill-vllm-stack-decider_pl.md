---

name: vllm-stack-decider
description: Zdecyduj o układzie wdrożenia vLLM — wykres Helm stosu produkcyjnego, obciążenie KV (natywny procesor lub LMCache), integracja routera/obserwowalności — biorąc pod uwagę obciążenie pracą i wielkość floty.
version: 1.0.0
phase: 17
lesson: 18
tags: [vllm, production-stack, lmcache, kv-offload, connector-api]

---

Biorąc pod uwagę obciążenie pracą (kształt podpowiedzi, współbieżność, wzorzec ponownego wykorzystania prefiksów), flotę (silniki, typ procesora GPU) i kontekst operacyjny (natywny dla Kubernetes, wielu dzierżawców, budżet), utwórz plan stosu vLLM.

Wyprodukuj:

1. Stos. Użyj wykresu Helm stosu produkcyjnego vLLM (zalecanego w przypadku nowych wdrożeń) lub przeprowadź własny. Podaj, którzy operatorzy/CRD mają zastosowanie.
2. Odciążenie KV. Wybierz:
   - Brak (krótkie podpowiedzi, niska współbieżność — obciążenie przewyższa korzyści).
   - Natywne odciążanie procesora vLLM (ciśnienie HBM na jednym silniku, proste).
   - Złącze LMCache (ponowne użycie prefiksu na wielu silnikach, monity wymagające wywłaszczania lub współdzielone monity dla wielu dzierżawców).
3. Monitorowanie wykorzystania HBM. Ustaw `--gpu-memory-utilization` z zapasem; alarm na poziomie 92%+, utrzymujący się jako sygnał wyprzedzający.
4. Integracja routera. Router obsługujący pamięć podręczną (faza 17 · 11). Potwierdź skonfigurowanie kanału zdarzeń KV.
5. Obserwowalność. Zeskrobanie Prometheusa na silnik, atrybuty Otel GenAI (faza 17 · 13), szablon pulpitu nawigacyjnego Grafana ze stosu produkcyjnego.
6. Oczekiwany wpływ. Określ ilościowo oczekiwany wzrost przepustowości w funkcji prądu — odwołaj się do kształtu testu porównawczego 16x H100 (LMCache pomaga, gdy ślad KV przekracza HBM).

Twarde odrzucenia:
- Wdrażanie LMCache bez współdzielonych prefiksów i wywłaszczania. Odmowa — obciążenie ogólne, bez korzyści.
- Uruchamianie vLLM bez monitorowania ciśnienia HBM. Odmów – pierwsze wywłaszczenie będzie niespodzianką.
- Ręczne walcowanie stosu produkcyjnego, gdy wykres Helma obejmuje przypadek użycia. Odmów – wymyśl na nowo koszty.

Zasady odmowy:
- Jeśli flota ma <2 silniki, odrzuć LMCache — chodzi o ponowne wykorzystanie wielu silników; Natywny do użytku jednosilnikowego.
— Jeśli obciążenie zawiera monity < 1 tys. tokenów i < 100 współbieżności, odmów jakiegokolwiek odciążenia — wystarczy zapas HBM.
- Jeśli zespół nie ma możliwości K8, odrzuć stos produkcyjny — zacznij od jednosilnikowego vLLM + prostego proxy.

Wynik: jednostronicowy stos nazewnictwa planów, wybór odciążenia KV, monitorowanie HBM, integracja routerów, obserwowalność, oczekiwany wpływ. Zakończ pojedynczą bramą: wykorzystanie HBM P99 w ciągu ostatnich 24 godzin.