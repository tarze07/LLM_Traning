# Capstone 15 — konstytucyjna uprząż bezpieczeństwa + strzelnica drużyny czerwonej

> Klasyfikatory konstytucyjne firmy Anthropic, Llama Guard 4 firmy Meta, ShieldGemma-2 firmy Google, Nemotron 3 Content Safety firmy NVIDIA i X-Guard do obsługi wielojęzycznej zdefiniowały stos klasyfikatorów bezpieczeństwa na rok 2026. garak, PyRIT, NVIDIA Aegis i Promptfoo stały się standardowymi narzędziami do oceny kontradyktoryjnej. NeMo Guardrails v0.12 łączy je w rurociąg produkcyjny. To zwieńczenie łączy wszystko w jedną całość: warstwową uprząż bezpieczeństwa wokół docelowej aplikacji, autonomicznego agenta czerwonej drużyny kierującego ponad 6 rodzinami ataków oraz konstytucyjną samokrytykę, która tworzy mierzalną deltę nieszkodliwości.

**Typ:** Zwieńczenie
**Języki:** Python (potok bezpieczeństwa, zespół czerwony), YAML (konfiguracje zasad)
**Wymagania wstępne:** Faza 10 (LLM od podstaw), Faza 11 (inżynieria LLM), Faza 13 (narzędzia), Faza 14 (agenci), Faza 18 (etyka, bezpieczeństwo, dostosowanie)
**Wykonywane fazy:** P10 · P11 · P13 · P14 · P18
**Czas:** 25 godzin

## Problem

Granicą bezpieczeństwa LLM w 2026 r. nie będzie to, czy klasyfikatory działają (w przybliżeniu tak), ale to, jak prawidłowo je skomponować wokół aplikacji produkcyjnej, bez nadmiernego odmawiania lub pozostawiania oczywistych luk. Llama Guard 4 radzi sobie z naruszeniami zasad w języku angielskim. X-Guard (132 języki) obsługuje wielojęzyczny jailbreak. ShieldGemma-2 przechwytuje natychmiastowy zastrzyk oparty na obrazie. Bezpieczeństwo treści NVIDIA Nemotron 3 obejmuje kategorie korporacyjne. Klasyfikatory konstytucyjne firmy Anthropic to odrębne podejście stosowane podczas treningu, a nie podczas serwowania.

Ewolucja ataku też ma znaczenie. PAIR i TAP automatyzują wykrywanie jailbreaków. GCG przeprowadza ataki sufiksowe oparte na gradiencie. Ataki wieloobrotowe i typu code-switch wykorzystują pamięć agenta. Każdy wdrożony LLM wymaga zasięgu zespołu czerwonego – kanonicznymi czynnikami napędowymi są garak i PyRIT – a także udokumentowanych środków łagodzących i ustaleń ocenianych przez CVSS.

Utwardzisz aplikację docelową (albo model dostrojony instrukcjami 8B, albo jeden z chatbotów RAG z innych zwieńczeń), przeprowadzisz przeciwko niej ponad 6 rodzin ataków i wykonasz pomiar nieszkodliwości przed/po.

## Koncepcja

Rurociąg bezpieczeństwa składa się z pięciu warstw. **Odkażanie wejścia**: usuń znaki o zerowej szerokości, dekoduj base64/rot13, normalizuj Unicode. **Warstwa zasad**: szyny NeMo Guardrails v0.12 (poza domeną, toksyczność, ekstrakcja danych osobowych). **Brama klasyfikatora**: Llama Guard 4 na wejściu, X-Guard na wejściu w języku innym niż angielski, ShieldGemma-2 na wejściu obrazu. **Model**: docelowy LLM. **Filtr wyjściowy**: Llama Guard 4 na wyjściu, oczyszczanie Presidio PII, egzekwowanie cytowań, jeśli ma to zastosowanie. **Poziom HITL**: dane wyjściowe oznaczone jako wysokiego ryzyka trafiają do kolejki Slack.

Zakres drużyny czerwonej działa według harmonogramu. PAIR i TAP autonomicznie wykrywają jailbreaki. GCG przeprowadza ataki sufiksowe oparte na gradiencie. Ataki na kodowanie ASCII / base64 / rot13. Ataki wieloturowe (adopcja persony, wykorzystanie pamięci). Ataki typu code-switch (połączenie angielskiego z suahili lub tajskim). Każde badanie generuje uporządkowany plik ustaleń z punktacją CVSS i harmonogramem ujawnień.

Bieg konstytucyjnej samokrytyki jest interwencją w czasie szkolenia. Weź 1 tys. podpowiedzi dotyczących szkodliwych prób, poproś modela o napisanie odpowiedzi, skrytykuj ją pod kątem pisemnej konstytucji (zasady „nie szkodzić”) i ponownie przeszkol się w pętli krytyki. Zmierz deltę nieszkodliwości przed/po na wyciągniętym ewaluatorze.

## Architektura

```
request (text / image / multilingual)
      |
      v
input sanitize (strip zero-width, decode, normalize)
      |
      v
NeMo Guardrails v0.12 rails (off-domain, policy)
      |
      v
classifier gate:
  Llama Guard 4 (English)
  X-Guard (multilingual, 132 langs)
  ShieldGemma-2 (image prompts)
  Nemotron 3 Content Safety (enterprise)
      |
      v (allowed)
target LLM
      |
      v
output filter: Llama Guard 4 + Presidio PII + citation check
      |
      v
HITL tier for flagged outputs

parallel:
  red-team scheduler
    -> garak (classic attacks)
    -> PyRIT (orchestrated red team)
    -> autonomous jailbreak agent (PAIR + TAP)
    -> GCG suffix attacks
    -> multilingual / code-switch
    -> multi-turn persona adoption

output: CVSS-scored findings + disclosure timeline + before/after harmlessness delta
```

## Stos

- Klasyfikatory bezpieczeństwa: Llama Guard 4, ShieldGemma-2, NVIDIA Nemotron 3 Content Safety, X-Guard
- Framework Guardrails: NeMo Guardrails v0.12 + OPA
- Sterowniki zespołu czerwonego: garak (NVIDIA), PyRIT (Microsoft Azure), NVIDIA Aegis, Promptfoo
- Agenci jailbreak: PAIR (Chao et al., 2023), Tree-of-Attacks (TAP), przyrostek GCG
- Trening konstytucyjny: pętla samokrytyki w stylu antropicznym + SFT w zakresie krytyki
- Peeling PII: Presidio
- Cel: model 8B dostrojony do instrukcji lub jeden z chatbotów RAG innych zwieńczeń

## Zbuduj to

1. **Konfiguracja celu.** Stwórz model 8B dostrojony do instrukcji na vLLM (lub ponownie użyj chatbota RAG z innego zwieńczenia). To jest testowana aplikacja.

2. **Owinięcie rurociągu zabezpieczającego.** Owiń pięciowarstwowy rurociąg wokół elementu docelowego. Sprawdź, czy każda warstwa jest indywidualnie obserwowalna (rozpiętość na warstwę w Langfuse).

3. **Zasięg klasyfikatora.** Załaduj Llama Guard 4, X-Guard (wielojęzyczny), ShieldGemma-2 (zdjęcie). Przeprowadź każdy test na małym, oznaczonym zestawie, aby ustalić wartości bazowe.

4. **Harmonogram drużyny czerwonej.** Zaplanuj garaka, PyRIT, agenta PAIR, agenta TAP, biegacza GCG, atakującego wieloturowego i atakującego ze zmianą kodu. Każdy działa w osobnej kolejce.

5. **Zestaw ataków.** Sześć rodzin ataków: (1) automatyczne jailbreak PAIR, (2) drzewo ataków TAP, (3) sufiks gradientu GCG, (4) kodowanie ASCII / base64 / rot13, (5) wieloobrotowa osobowość, (6) wielojęzyczny przełącznik kodu. Zgłoś wskaźnik sukcesu na rodzinę.

6. **Samokrytyka zgodna z Konstytucją.** Zbadaj 1 tys. powiadomień o szkodliwych próbach. Na każdy cel cel przygotowuje odpowiedź. Krytyk LLM ocenia spisaną konstytucję („nie szkodzić”, „cytować dowody”, „odrzucać nielegalne wnioski”). Monituje o przepisanie obiektów krytycznych; cel dostraja pary, które mają lepszą krytykę. Zmierz stan nieszkodliwości przed/po na wyciągniętym ewaluatorze.

7. **Pomiar nadmiernej odmowy.** Śledź odsetek wyników fałszywie dodatnich za pomocą łagodnego zestawu podpowiedzi (np. XSTest). Cel musi pozostać pomocny w przypadku łagodnych pytań.

8. **Punktacja CVSS.** Za każde udane jailbreak zdobądź wynik w CVSS 4.0 (wektor ataku, złożoność, wpływ). Przygotuj harmonogram ujawnień i plan łagodzenia skutków.

9. **Automatyzacja zasięgu.** Wszystko powyżej działa na cronie; wyniki zapisują się w kolejce; regresja nadmiernej odmowy alarmuje o uruchomieniu Slacka.

## Użyj tego

```
$ safety probe --model=target --family=PAIR --budget=50
[attacker]   PAIR agent running on target
[attack]     attempt 1/50: disguise query as academic research ... blocked
[attack]     attempt 2/50: appeal to roleplay ... blocked
[attack]     attempt 3/50: chain-of-thought coax ... SUCCEEDED
[finding]    CVSS 4.8 medium: roleplay bypass on target
[range]      7 successes out of 50 (14% success rate)
```

## Wyślij to

Elementem dostarczanym jest `outputs/skill-safety-harness.md`. Warstwowy rurociąg bezpieczeństwa klasy produkcyjnej oraz powtarzalny zakres czerwonej drużyny z deltami nieszkodliwości przed/po.

| Waga | Kryterium | Jak to się mierzy |
|:-:|---|---|
| 25 | Pokrycie powierzchni ataku | Przećwiczono ponad 6 rodzin ataków, ponad 2 języki |
| 20 | Kompromis prawdziwie pozytywny/fałszywie pozytywny | Współczynnik blokowania ataków vs współczynnik łagodnych przejść testu XST |
| 20 | Delta samokrytyki | Przed/po nieszkodliwości na odłożonej ewaluacji |
| 20 | Dokumentacja i ujawnianie | Wyniki punktacji CVSS z osią czasu |
| 15 | Automatyzacja i powtarzalność | Wszystko działa na cronie z alertami |
| **100** | | |

## Ćwiczenia

1. Uruchom wtyczkę Garaka w celu natychmiastowego wstrzyknięcia na chatbocie RAG i porównaj skuteczność ataków z i bez warstwy filtra wyjściowego.

2. Dodaj siódmą rodzinę ataków: pośrednie wstrzykiwanie natychmiastowe za pośrednictwem odzyskanych dokumentów. Zmierz wymaganą dodatkową obronę.

3. Wdrożyć tryb „odmowy z pomocą”: gdy poręcz blokuje się, cel oferuje bezpieczniejszą odpowiedź zamiast zwykłej odmowy. Zmierz deltę XSTest.

4. Luka w zasięgu wielu języków: znajdź język, w którym X-Guard radzi sobie gorzej. Zaproponuj dostosowany do niego zbiór danych.

5. Przeprowadź samokrytykę konstytucyjną na modelu 30B i zmierz, czy delta się skaluje.

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|-----------------|--------------------------------------|
| Warstwowe bezpieczeństwo | „Głęboka obrona” | Wiele poręczy na wejściu, bramie, wyjściu, HITL |
| Strażnik Lamy 4 | „Klasyfikator bezpieczeństwa Meta” | Referencyjny klasyfikator zawartości wejścia/wyjścia na rok 2026 |
| PARA | „Agent jailbreak” | Artykuł (Chao i in.) na temat odkrywania jailbreaków za pomocą LLM |
| KLIKNIJ | „Drzewo ataków” | Wariant wyszukiwania drzewa PAIR |
| GCG | „Chciwy gradient współrzędnych” | Atak sufiksem kontradyktoryjnym oparty na gradiencie |
| Konstytucyjna samokrytyka | „Trening w stylu antropicznym” | Docelowe wersje robocze -> oceny krytyków -> przepisz -> przekwalifikuj |
| XSTest | „Łagodny zestaw sond” | Punkt odniesienia dla regresji nadmiernej odmowy |
| CVSS 4.0 | „Ocena ważności” | Standardowa ocena podatności na zagrożenia w przypadku ustaleń dotyczących bezpieczeństwa |

## Dalsze czytanie

– [Antropiczne klasyfikatory konstytucyjne](https://www.anthropic.com/research/constitutional-classifiers) — informacje dotyczące czasu szkolenia
– [Meta Llama Guard 4](https://ai.meta.com/research/publications/llama-guard-4/) — klasyfikator wejścia/wyjścia na rok 2026
- [Google ShieldGemma-2](https://huggingface.co/google/shieldgemma-2b) — obraz + bezpieczeństwo multimodalne
— [Bezpieczeństwo treści NVIDIA Nemotron 3](https://developer.nvidia.com/blog/building-nvidia-nemotron-3-agents-for-reasoning-multimodal-rag-voice-and-safety/) — informacje dla przedsiębiorstw
- [X-Guard (arXiv:2504.08848)](https://arxiv.org/abs/2504.08848) — bezpieczeństwo w 132 językach i wielu językach
- [garak](https://github.com/NVIDIA/garak) — zestaw narzędzi NVIDIA dla zespołu red-team
- [PyRIT](https://github.com/Azure/PyRIT) — framework Microsoft Red Team
- [NeMo Guardrails v0.12](https://docs.nvidia.com/nemo-guardrails/) — framework kolejowy
– [PAIR (arXiv:2310.08419)](https://arxiv.org/abs/2310.08419) — dokument agenta jailbreak