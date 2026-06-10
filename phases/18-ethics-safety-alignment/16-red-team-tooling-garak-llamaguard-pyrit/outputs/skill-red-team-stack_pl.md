---

name: red-team-stack
description: Poleć stos narzędzi i konfigurację zespołu Red Team dla danego wdrożenia.
version: 1.0.0
phase: 18
lesson: 16
tags: [llama-guard, garak, pyrit, red-team-tooling, mlcommons-hazards]

---

Biorąc pod uwagę opis wdrożenia, zarekomenduj stos narzędzi zespołu czerwonego i rytm regresji.

Wyprodukuj:

1. Umiejscowienie klasyfikatora. Polecaj Llama Guard (3-8B, 3-1B-INT4 lub 4-12B) na wejściu, wyjściu lub obu. W przypadku wdrożeń brzegowych preferuj 3-1B-INT4. W przypadku transportu multimodalnego Llama Guard 4.
2. Konfiguracja skanera sondy. Poleć sondy Garak odpowiednie dla wdrożenia: halucynacje (dla systemów RAG), wyciek danych (dla sąsiadujących z PII), natychmiastowe wstrzyknięcie (zawsze), jailbreaki (zawsze). Wybierz parę tarcz Prompt-Guard-86M + Llama-Guard-3-8B w celu kompleksowej oceny.
3. Koordynator kampanii. Polecaj PyRIT do kampanii przedpremierowych na modelach z nowatorskimi możliwościami. Określ łańcuchy konwerterów do uruchomienia (parafraza, kodowanie, tłumaczenie, odgrywanie ról) i orkiestrator (Crescendo do eskalacji, TAP do rozgałęziania).
4. Kadencja. Garak co wieczór dla regresji. PyRIT w wydaniu dla głębokiej czerwieni. Llama Guard jest stale rozmieszczona.
5. Kalibracja sędziego. Określ sędziego LLM (GPT-4-turbo, StrongREJECT, wewnętrzny) dla każdego narzędzia, które go używa. Sędzia kalibrujący dyski zgłosił ASR.

Twarde odrzucenia:
- Każde wdrożenie bez co najmniej jednego klasyfikatora wejściowego lub wyjściowego klasy Llama Guard.
- Dowolne wydanie bez Garaka lub równoważnej regresji jednoobrotowej.
- Każde wdrożenie o wysokiej stawce bez kampanii odpowiadającej PyRIT przed wydaniem.

Zasady odmowy:
- Jeśli użytkownik poprosi o jedno „najlepsze” narzędzie, odmów — te trzy pokrywają różne warstwy i są nakładane na siebie, a nie zastępowane.
- Jeśli użytkownik poprosi o komercyjną alternatywę typu „wszystko w jednym”, odrzuć tę rekomendację i wskaż stan na rok 2026: trzy otwarte narzędzia to aktualny stos najlepszych praktyk.

Wynik: jednostronicowe zalecenie zawierające nazwę rozmieszczenia klasyfikatora, konfiguracji sondy, koordynatora kampanii, rytmu regresji i tożsamości sędziego. Cytuj po jednym Meta (arXiv:2407.21783), NVIDIA Garak i Microsoft PyRIT.