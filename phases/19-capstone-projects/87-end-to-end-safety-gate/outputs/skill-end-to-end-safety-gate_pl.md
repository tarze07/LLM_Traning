---

name: skill-end-to-end-safety-gate
description: Bramka bezpieczeństwa z trzema punktami kontrolnymi składająca się z detektora wejściowego, filtra tokenów strumieniowych, klasyfikatora wyjściowego i silnika reguł z deterministyczną tabelą agregacji i śledzeniem na żądanie
version: 1.0.0
phase: 19
lesson: 87
tags: [safety, harness, composition]

---

# Kompleksowa bramka zabezpieczająca

## Cykl życia

1. pre-gen - uruchom detektor lekcji 83 w wierszu poleceń
   - jeśli pewność >= próg_bloku: zwróć odmowę, wyemituj śledzenie, zatrzymaj
2. podczas generacji - strumień z modelu, buforuj dwa fragmenty, skanuj w poszukiwaniu znanych szkodliwych kontynuacji
   - jeśli dopasowane: zakończ iterator, zaznacz ślad, traktuj jako średni poziom ważności
3. post-gen – jeśli nie ma wcześniejszego zakończenia, uruchom router klasyfikatora z lekcji 85 i silnik reguł z lekcji 86 na ukończonym wyjściu
4. agregacja – przyjmij maksymalną ważność dla pre, podczas, post.classifier, post.rules
5. zastosuj — mapuj, aby blokować, redagować, ostrzegać lub zezwalać

## Tabela agregacji

| Stan sygnału | Akcja |
|---|---|
| dowolna wysoka dotkliwość | blok |
| dowolne średnie nasilenie | zredagować |
| każda niska dotkliwość | ostrzegam |
| nic | pozwolić |

## Struktura śledzenia

```text
RequestTrace
  request_id: str
  prompt: str
  pre_gen: { category, confidence, fired[] }
  during_gen: { terminated_early, matched_pattern, partial_chunks }
  post_gen: { classifier_action, classifier_severity, rules_max_severity, rules_violations[] } | null
  final_action: block | redact | warn | allow
  final_output: str
  latency_ms: float
```

## Artefakt

`outputs/gate_trace.json` zawiera podsumowanie i jeden ślad na żądanie, w tym 50 elementów taksonomii i 10 łagodnych podpowiedzi.