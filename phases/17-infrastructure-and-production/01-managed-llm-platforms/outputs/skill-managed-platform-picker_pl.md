---

name: managed-platform-picker
description: Wybierz zarządzaną platformę LLM (Bedrock, Azure OpenAI, Vertex AI) i drugą pod kątem nadmiarowości, biorąc pod uwagę obciążenie pracą, umowę SLA i wymagania dotyczące zgodności, a następnie przygotuj plan instrumentacji FinOps.
version: 1.0.0
phase: 17
lesson: 01
tags: [bedrock, azure-openai, vertex-ai, ptu, finops, managed-platforms]

---

Biorąc pod uwagę profil obciążenia (wymagane modele, tokeny miesięczne, umowa SLA TTFT na poziomie P50/P99, ograniczenia zgodności, istniejący zasięg chmury), przygotuj rekomendację platformy.

Wyprodukuj:

1. Platforma podstawowa. Nazwij platformę, konkretne modele, które obsługuje, i określ, czy jednostki przepustowości na żądanie, czy zapewnione jednostki przepustowości (PTU) / zapewniona przepustowość są odpowiednie, biorąc pod uwagę wykorzystanie. Przytocz obliczenia progu rentowności (PTU przy około 40-60% trwałego wykorzystania).
2. Platforma wtórna. Nazwij rezerwę minimalną dla dwóch dostawców. Uzasadnij parowanie — nadmiarowość musi obejmować nakładanie się modeli (Claude na platformie Bedrock + GPT na platformie Azure OpenAI to typowa para) i nakładanie się regionów.
3. Oprzyrządowanie FinOps. Określ, co włączyć pierwszego dnia: profile wnioskowania aplikacji Bedrock, zakresy platformy Azure + rezerwacje PTU jako obiekty kosztowe, projekt Vertex na zespół + eksport rozliczeń BigQuery. Nazwij wymiary atrybucji — na użytkownika, na zadanie, na dzierżawcę.
4. Kontrola SLA. Porównaj docelowy TTFT P99 z opublikowanymi testami porównawczymi (Azure OpenAI PTU ≈ 50 ms P50; Bedrock on-demand ≈ 75 ms P50). Jeśli umowa SLA jest bardziej rygorystyczna niż można zapewnić na żądanie, wymagaj PTU.
5. Kontrola zgodności. W razie potrzeby sprawdź BAA, SOC 2 Type II, HIPAA, miejsce zamieszkania danych w UE. Należy pamiętać, że wszystkie trzy są zgodne z wartościami wyjściowymi, ale zasady przechowywania i możliwość rezygnacji z monitorowania nadużyć różnią się.
6. Ścieżka migracji. Wymień jeden odwracalny krok, który zespół może wykonać w tym tygodniu (np. wdrożenie za pośrednictwem dostawcy abstrakcji bram AI; nagłówki atrybucji instrumentów) i jeden krok długoterminowy (zaangażowanie PTU; przełączanie awaryjne między regionami).

Twarde odrzucenia:
- Polecanie pojedynczej platformy bez nazwanej platformy zastępczej. Odmów i nalegaj na minimum dwóch dostawców.
- Odbiór PTU bez szacunkowego wykorzystania. Odmów i poproś o dane dotyczące trwałego wykorzystania.
- Ignorowanie profili wnioskowania aplikacji podłoża skalnego, gdy atrybucja jest wymieniona jako wymaganie - są to najczystsze powierzchnie natywne.

Zasady odmowy:
— Jeśli obciążenie wymaga Claude, Gemini i GPT jako P0, nazwij rzeczywistość trzech platform (Bedrock + Vertex + Azure OpenAI za bramą), zamiast udawać, że jedna platforma może obsługiwać wszystkie trzy.
- Jeżeli SLA wynosi TTFT P99 < 100 ms, a oczekiwany budżet nie jest w stanie obsłużyć PTU, odmów obietnicy SLA – wyjaśnij pułap wariancji na żądanie.
- Jeśli klient poprosi o „użycie najtańszego dostawcy”, odmów – cena jest wielowymiarowa (stawka za token + dedykowana pojemność + obciążenie atrybucyjne + koszt blokady).

Dane wyjściowe: jednostronicowa decyzja obejmująca platformę podstawową, platformę dodatkową, PTU w porównaniu z usługą na żądanie, listę oprzyrządowania, umowę SLA/weryfikację zgodności i dwa etapy migracji. Zakończ pojedynczym miernikiem, który wychwyci odchylenia od planu (trwałe wykorzystanie, marnotrawstwo PTU lub pokrycie atrybucji).