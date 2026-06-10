---

name: hierarchy-fitness
description: Zdecyduj, czy zadanie wieloagentowe pasuje do struktury hierarchicznej, płaskiej czy sekwencyjnej. Wskaż kluczowe tryby awarii.
version: 1.0.0
phase: 16
lesson: 06
tags: [multi-agent, hierarchy, crewai, langgraph, decomposition-drift]

---

Na podstawie opisu zadania oraz opcjonalnej struktury organizacyjnej zarekomenduj optymalny wzorzec koordynacji (potok sekwencyjny, płaski nadzorca lub struktura hierarchiczna) i określ konkretne tryby awarii, przed którymi należy zabezpieczyć system.

Wygeneruj:

1. **Analiza struktury zadania.** Czy zadanie ma charakter liniowy, dzieli się na niezależne gałęzie, czy też wymaga zagnieżdżonych zespołów o własnych celach cząstkowych? Uzasadnij odpowiedź.
2. **Rekomendacja wzorca.** Wskaż właściwy wzorzec (sekwencyjny, płaski nadzorca lub hierarchiczny). W przypadku hierarchii określ głębokość drzewa (preferowane są maksymalnie 2 poziomy zagnieżdżenia; 3 poziomy dopuszcza się wyłącznie przy szczególnych wymaganiach audytowych).
3. **Plan dekompozycji.** Zaprojektuj strukturę dekompozycji zadań dla menedżera najwyższego szczebla. Dla każdej gałęzi wskaż podkierownika oraz przypisz mu precyzyjnie zawężony zakres odpowiedzialności.
4. **Budżet uzgodnień (consensus budget).** Określ limit rund poprawek i negocjacji, po przekroczeniu którego menedżer najwyższego szczebla musi podjąć ostateczną decyzję. Domyślna wartość to 2.
5. **Zabezpieczenia (Guardrails).** Wskaż trzy minimalne mechanizmy obronne: wdrożenie agenta kanarka na każdym poziomie, śledzenie łańcucha pochodzenia informacji (lineage) przy syntezie oraz automatyczny alert przy wykryciu dryfu dekompozycji.
6. **Analiza trybów awarii.** Które z ryzyk {błąd przydziału zadań, dryf znaczeniowy, pętla decyzyjna} jest najbardziej prawdopodobne przy wybranym kształcie zadania? Opisz jeden konkretny objaw oraz sposób łagodzenia dla każdego z tych trybów.

Twarde kryteria odrzucenia:

- Odrzuć projekty proponujące głębokość hierarchii > 2 bez przedstawienia silnych wymagań regulacyjnych lub organizacyjnych.
- Odrzuć projekty hierarchiczne dla zadań, które mają charakter liniowy. Takie procesy powinny być realizowane za pomocą potoków sekwencyjnych.
- Odrzuć projekty, które nie definiują jasnego budżetu uzgodnień.

Zasady obsługi przypadków szczególnych:

- Jeśli zadanie jest na tyle proste, że może je obsłużyć jeden agent (poniżej ~10 wywołań narzędzi), odrzuć hierarchię i zaleć architekturę jednoagentową.
- Jeśli poszczególne kroki zadania nie mają wyraźnych granic kompetencyjnych i są od siebie silnie zależne, odrzuć strukturę hierarchiczną na rzecz wspólnego czatu grupowego (Group Chat).
- Jeśli użytkownik próbuje wdrożyć głęboką hierarchię tylko dlatego, że „tak wygląda struktura ludzka w firmie”, wskaż, że hierarchie ludzkie nie przekładają się wprost na wydajność modeli LLM i zarekomenduj bardziej płaską strukturę.

Wynik: jednostronicowy raport syntetyczny. Rozpocznij od rekomendacji wzorca, a zakończ wskazaniem trzech największych zagrożeń i metod ochrony przed nimi.
