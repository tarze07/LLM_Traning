---

name: failure-detector
description: Generuj detektory trybów awarii dla śladów agentów, podłączone do magazynu śledzenia, oznaczając pięć powtarzających się trybów branżowych oraz sygnatury specyficzne dla domeny.
version: 1.0.0
phase: 14
lesson: 26
tags: [failure-modes, masft, detection, observability]

---

Mając domenę produktu i magazyn śledzenia, utwórz detektory trybów awarii agentów.

Wyprodukuj:

1. Detektor na tryb: `hallucinated_action`, `scope_creep`, `cascading_errors`, `context_loss`, `tool_misuse`, `success_hallucination`.
2. Detektory specyficzne dla domeny (np. „utworzono PR bez łączenia problemu” w przypadku narzędzia deweloperskiego, „wysłano wiadomość e-mail do > 5 odbiorców bez potwierdzenia” w przypadku narzędzia marketingowego).
3. Tagger, który stosuje wszystkie detektory do każdego śladu i emituje rozkład.
4. Alerty oparte na progach: jeśli >=5% dzisiejszych śladów oznacza tag trybu, stronę lub otwiera zgłoszenie.
5. Przechowywanie próbek: dla każdego oznaczonego śladu przechowuj dane wejściowe, wyjściowe i migawki stanu do wglądu operatora.

Twarde odrzucenia:

- Detektory wymagające wywołań LLM na ślad w produkcji. Używaj detektorów opartych na wzorcach; zarezerwować sędziego LLM do przeglądu próbek.
- Tagowanie tylko w przypadku awarii. Większość niepowodzeń generuje prawidłowo wyglądające dane wyjściowe. Wymagane jest sprawdzenie podpisu dotyczącego treści i stanu.
- Przechowywanie oznaczonych śladów bez redagowania informacji umożliwiających identyfikację. Próbki awarii niosą ze sobą najgorszą treść; szorować przed przechowywaniem.

Zasady odmowy:

- Jeśli użytkownik chce, aby „wszystkie ślady były przechowywane na zawsze”, odmów ze względu na koszty i zgodność. Próbka według tagu + stawka.
- Jeśli produkt nie ma „znanej dobrej” linii bazowej, odrzuć powiadomienia o dryfowaniu. Drift potrzebuje referencji.
- Jeśli czujki nie są wersjonowane, odmów. Regresje detektora zakłócają sygnał bez ostrzeżenia.

Dane wyjściowe: `detectors.py`, `tagger.py`, `alerts.py`, `retention.py`, `README.md` wyjaśniające progi, zasady przechowywania, przekazywanie alertów. Zakończ słowami „co dalej czytać”, wskazując Lekcję 24 (backendy obserwowalności) lub Lekcję 27 (wstrzykiwanie podpowiedzi) w przypadku kontradyktoryjnych trybów awarii.