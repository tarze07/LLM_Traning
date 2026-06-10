---

name: skill-constitutional-rules-engine
description: Deklaratywny silnik reguł YAML dla ograniczeń wyjściowych z ważnością, wyjaśnieniem, operacjami utrwalacza i różnicą strukturalną
version: 1.0.0
phase: 19
lesson: 86
tags: [safety, rules, constitutional]

---

# Silnik zasad konstytucyjnych

Konstytucja jest plikiem YAML. Każda reguła ma `name`, `severity` (niski | średni | wysoki), `applies_when` (predykat), `must` (predykat), `explanation` i opcjonalnie `fix`.

## Predykaty

atomowy:

-`contains_regex`/`not_contains_regex`
-`starts_with_regex`/`ends_with_regex`
-`max_words`/`min_words`

Skład:

-`all_of: [...predicates]`
-`any_of: [...predicates]`
-`not_: predicate`

## Napraw operacje

-`append_if_missing: <suffix>`
-`prepend_if_missing: <prefix>`
-`replace_regex: { pattern: <regex>, replacement: <text> }`

## Moc silnika

`Engine.evaluate(text) -> EngineReport` zwraca jeden `RuleResult` na regułę z `status` w `pass`, `violation`, `not_applicable`. `report.violations()` filtruje naruszenia, a `report.max_severity()` zwraca najgorszą obecną wagę.

## Artefakt

`outputs/rules_report.json` zawiera wersję roboczą, poprawioną i ustrukturyzowaną różnicę w każdym przypadku.