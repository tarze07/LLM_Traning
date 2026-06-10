---

name: multi-region-router
description: Zaprojektuj wieloregionowy plan routingu dla modeli LLM z uwzględnieniem lokalności pamięci podręcznej KV, granic suwerenności danych (data residency), manifestu DR oraz harmonogramu kwartalnych testów odzyskiwania po awarii.
version: 1.0.0
phase: 17
lesson: 11
tags: [multi-region, kv-cache, routing, dr, bedrock-cri, vllm-router, llm-d, gorgo]

---

Na podstawie rozpiętości geograficznej regionów, granic suwerenności danych, oczekiwanego zróżnicowania prefiksów w pamięci podręcznej oraz wymagań SLA dla parametru TTFT, opracuj wieloregionowy plan routingu i odzyskiwania po awarii (DR).

Wygeneruj:

1. Wybór routera. Wybierz router uwzględniający stan cache (np. vLLM Router, llm-d) i opisz mechanizm obsługi zdarzeń pamięci KV. Zdefiniuj algorytm hashowania prefiksów (np. hashowanie pierwszych 512 tokenów) oraz regułę rozstrzygania remisów w routingu (wybór repliki z najkrótszą kolejką zadań).
2. Polityka routingu. Określ strategię optymalizacji: minimalizacja sumy czasu prefillu i opóźnienia sieciowego (RTT) na poziomie regionalnym czy globalnym (podejście w stylu GORGO)? Uzasadnij decyzję rozkładem długości promptów (np. długie prompty > 8k tokenów mogą kwalifikować się do przekierowania między regionami, podczas gdy krótkie prompty powinny być obsługiwane lokalnie).
3. Podział ze względu na suwerenność danych (Data Residency). Przed przystąpieniem do optymalizacji zdefiniuj, które zapytania są przypisane do konkretnych regionów ze względów prawnych (np. RODO/GDPR, HIPAA). Kategorycznie zabroń routingu wykraczającego poza te granice prawne, nawet w scenariuszach skutkujących skróceniem TTFT.
4. Wykorzystanie usług typu Cross-Region Inference (CRI). Przedstaw rekomendację dotyczącą włączenia komercyjnych usług (np. AWS Bedrock Cross-Region Inference lub GKE Multi-Cluster Gateway) jako warstwy zapewniającej wysoką dostępność. Wyraźnie podkreśl, że usługi te NIE służą do optymalizacji czasu TTFT.
5. Manifest DR. Przygotuj strukturę złożoną z minimum trzech elementów (zawartość repozytorium Hugging Face + konfiguracja silnika + manifest wdrożeniowy). Upewnij się, że pliki tokenizera, parametry kwantyzacji, ustawienia RoPE, szablony konwersacji oraz adaptery LoRA są uwzględnione. Określ sposób przechowywania kopii (np. międzyregionalna replikacja S3 lub wieloregionowy GCS).
6. Testy odzyskiwania po awarii (DR Drill). Harmonogram: co kwartał. Określ rolę odpowiedzialną za przeprowadzenie testu oraz mierzone wskaźniki (RTO – Recovery Time Objective, RPO – Recovery Point Objective, czas nagrzewania cache KV). Wyznacz docelowy czas RTO na poziomie max 30 minut, odwołując się do wyników testu JPMorgan z 2024 r.

Kategoryczne odrzucenia:
- Ignorowanie wymogów lokalizacji danych (data residency) w celu optymalizacji opóźnień routingu. Naruszenie przepisów RODO/GDPR jest poważniejszym błędem niż pogorszenie wskaźnika TTFT.
- Twierdzenie, że usługi klasy Bedrock CRI „rozwiązują” problem routingu między regionalnymi pamięciami podręcznymi. CRI zarządza dostępnością, a nie lokalnością cache KV pod kątem czasu TTFT.
- Tworzenie kopii zapasowych wyłącznie dla wag modelu. Uwzględnij fakt, że 32% awarii systemów DR wynika z braku innych niezbędnych plików i wymagaj stosowania 3-elementowego manifestu.

Zasady odmowy wdrożenia (odrzucenie rekomendacji):
- Jeśli projekt obejmuje uruchomienie infrastruktury wyłącznie w jednym regionie, odrzuć plan – pojedynczy region podlega zupełnie innym mechanizmom awarii (zagadnienie to pokrywa Faza 17 · 03).
- Jeśli wymogi lokalizacji danych wykluczają się z umową SLA (np. konieczność przetwarzania danych w UE wymusza wykonanie pełnego prefillu od zera, co uniemożliwia osiągnięcie TTFT < 100 ms dla promptu o długości 8K), odmów zagwarantowania SLA i zgłoś konieczność modyfikacji założeń produktowych.

Wynik: jednostronicowy plan wdrażania zawierający nazwę routera, zasady routingu, podział na strefy suwerenności danych, konfigurację usług CRI, strukturę manifestu DR oraz przypisanie roli odpowiedzialnej za testy DR. Zakończ pojedynczą kluczową metryką do monitorowania: spadek współczynnika trafień cache prefiksów (prefix cache hit rate) w poszczególnych regionach poniżej progu założonego w planie.
