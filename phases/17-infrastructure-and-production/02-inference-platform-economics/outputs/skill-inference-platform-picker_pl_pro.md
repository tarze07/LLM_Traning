---

name: inference-platform-picker
description: Wybierz platformę wnioskowania (Fireworks, Together AI, Baseten, Modal, Replicate, Anyscale lub dedykowane układy scalone), biorąc pod uwagę profil obciążenia, wymagania SLA, budżet oraz ograniczenia operacyjne. Narzędzie normalizuje i porównuje ceny w modelach za token, minutowych oraz za zapytanie.
version: 1.0.0
phase: 17
lesson: 02
tags: [inference, fireworks, together, baseten, modal, replicate, anyscale, economics]

---

Na podstawie profilu obciążenia (model, dzienna liczba tokenów, poziom stałego wykorzystania, SLA dla wskaźnika TTFT, zmienność/skokowość ruchu, wymagania regulacyjne oraz preferencja stosu technologicznego - czysty Python vs stos mieszany) przygotuj rekomendację wyboru platformy.

Przygotuj:

1. **Platforma główna.** Wskaż rekomendowaną platformę oraz konkretny model rozliczeń (serwer bezserwerowy, dedykowane GPU lub przetwarzanie wsadowe). Uzasadnij wybór specyfiką obciążenia — np. „Wybór bezserwerowego Fireworks, ponieważ SLA wymaga wskaźnika TTFT < 500 ms przy wysokim natężeniu ruchu”.
2. **Koszt efektywny.** Przelicz wybrany model cenowy na ujednoliconą stawkę za milion tokenów ($/M tokens). Porównaj ze sobą co najmniej dwie alternatywne platformy. Wskaż, kiedy model minutowy (per-minute) staje się bardziej opłacalny niż model tokenowy (per-token) (tj. przy stałym wykorzystaniu GPU powyżej ~30%) lub odwrotnie.
3. **Strategia obsługi zimnego startu (cold start).** Dla rozwiązań bezserwerowych (Fireworks, Modal, Replicate) określ oczekiwane opóźnienia zimnego startu oraz metody optymalizacji (wstępne podgrzewanie zasobów [warm-up], ustawienie `min_workers=1`, migracja na żywo). Dla platform dedykowanych (Baseten, Anyscale) pomiń tę sekcję, zaznaczając jednak kompromisy związane z ciągłym opłacaniem bezczynnych zasobów.
4. **Platforma zapasowa (second choice).** Wskaż drugiego dostawcę oraz określ jasny warunek, przy którym nastąpi przełączenie na tę platformę (np. „przejście na platformę Baseten w przypadku pozyskania kontraktu enterprise wymagającego zgodności z HIPAA i dedykowanych procesorów GPU”).
5. **Brama API (Gateway).** Rekomendacja wdrożenia bramy AI Gateway (LiteLLM, Portkey, Kong AI Gateway) w celu uniezależnienia aplikacji od zmian u dostawców i uniknięcia vendor lock-in. Rekomendowane jako domyślne, chyba że natężenie ruchu wynosi poniżej 500 zapytań na sekundę (RPS).

Bezwzględne odrzucenie rekomendacji w przypadku:

- Porównywania stawek za tokeny ze stawkami minutowymi bez uprzedniego przeliczenia kosztów (normalizacji). Wymagaj przeliczenia na efektywny koszt za milion tokenów ($/M tokens).
- Rekomendowania platformy Fireworks jako „najszybszej” bez weryfikacji SLA dla wskaźnika TTFT w oparciu o oficjalne benchmarki.
- Rekomendowania dedykowanych układów scalonych (Groq, Cerebras, SambaNova) dla zadań, w których opóźnienia nie są kluczowym problemem. Układy te charakteryzują się wyższym kosztem, który ma uzasadnienie wyłącznie w przypadku bardzo rygorystycznych, interaktywnych SLA.

Zasady weryfikacji i odmowy:

- Jeśli system wymaga zgodności z regulacjami (SOC 2 Type II, HIPAA), a klient sugeruje wybór Modal lub Replicate, odmów – żadne z nich nie oferuje standardów korporacyjnych na poziomie usług Baseten lub Anyscale. Zaproponuj Baseten.
- Jeśli szacowany ruch wynosi mniej niż 100 tys. tokenów dziennie, odmów rekomendowania platform rozliczanych minutowo (Baseten, Modal, Anyscale). W tym scenariuszu ekonomia tego modelu nie ma uzasadnienia – domyślnym wyborem powinny być serwisy typu marketplace (np. OpenRouter, DeepInfra) lub zarządzane platformy hiperskalera.
- Jeśli celem klienta jest wyłącznie „wybór najtańszego dostawcy”, odrzuć takie uproszczenie – wskaż, że funkcja kosztu wnioskowania jest wielowymiarowa (cena za token, czas zimnego startu, narzut na atrybucję kosztów, wdrożenie bramy API oraz wydajność DX).

Format wyjściowy: Jednostronicowa rekomendacja określająca platformę główną, koszt efektywny, plan obsługi zimnego startu, platformę zapasową oraz konfigurację bramy API. Zakończ podaniem kluczowej metryki pozwalającej zidentyfikować błędny wybór (np. percentyl P99 zimnego startu, rzeczywista stawka za token lub odchylenie od zakładanego poziomu wykorzystania GPU).
