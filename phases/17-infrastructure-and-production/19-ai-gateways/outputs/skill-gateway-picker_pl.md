---

name: gateway-picker
description: Wybierz bramę AI (LiteLLM, Portkey, Kong AI, Cloudflare/Vercel) biorąc pod uwagę skalę, budżet opóźnień, zgodność, stan operacji i tolerancję cenową.
version: 1.0.0
phase: 17
lesson: 19
tags: [ai-gateway, litellm, portkey, kong, cloudflare, vercel, bifrost, fallback, rate-limit, guardrails]

---

Biorąc pod uwagę RPS (bieżący i przewidywany okres 12 miesięcy), budżet opóźnień, zgodność (wymagany własny hosting?), wymagania dotyczące zabezpieczeń (redakcja danych osobowych, wykrywanie jailbreak, audyt) i tolerancję cenową, sporządź rekomendację dotyczącą bramy.

Wyprodukuj:

1. Brama podstawowa. Nazwij narzędzie. Uzasadnij za pomocą sufitu, sufitu i dopasowania funkcji RPS.
2. Łańcuch awaryjny. Trzej dostawcy w kolejności; OpenAI → Antropiczne → hostowane na własnym serwerze jest kanoniczne. Oblicz oczekiwaną dostępność.
3. Polityka limitów stawek. Zalecane okno przesuwne >500 RPS; wiadro tokenów dopuszczalne w przeciwnym razie. Poziomowanie na dzierżawcę.
4. Poręcze. Świstoklik, jeśli wymagany jest PII/jailbreak; Kong w razie potrzeby skala + poręcze; LiteLLM, tylko dla poziomu deweloperskiego.
5. Przekazanie obserwowalności. Wskaż fazę 17. · Wybierz 13; potwierdź, że konwencje Otel GenAI są przestrzegane.
6. Migracja. W przypadku przejścia z integracji na poziomie aplikacji wdrożenie etapowe (1% kanarek na bramce, rozwinięcie w przypadku powodzenia).

Twarde odrzucenia:
- LiteLLM przy >2000 obr./s. Odmów — test porównawczy Kong pokazuje awarie kaskadowe; najpierw migruj.
- Świstoklik przy TTFT P99 < 100 ms SLA. Odmów — 30 ms narzutu pochłania zbyt dużo budżetu.
- Cloudflare AI Gateway dla regulowanego klienta lokalnego. Odmów — tylko zarządzane; brak własnego gospodarza.

Zasady odmowy:
- Jeśli niejednoznaczność skali jest duża (obecnie 100 RPS, planowane ponad 2 tys. w ciągu 6 miesięcy), przed podjęciem decyzji o rozpoczęciu korzystania z LiteLLM wymagany jest plan migracji.
- Jeśli zgodność wymaga SOC 2 typu II, a wybrana brama to tylko OSS bez zarządzanej umowy SLA, wymagane jest własne zaświadczenie klienta SOC 2.
- Jeśli zespół nie ma Kubernetesa i wybierze własnego hosta Kong, odmów — polecam zarządzany Kong lub Portkey zarządzany.

Wynik: jednostronicowa decyzja zawierająca bramę, łańcuch awaryjny, zasady dotyczące limitów szybkości, stan poręczy, przepływ obserwowalności, plan migracji. Zakończ jedną metryką: opóźnienie bramy P99 w ciągu ostatniej godziny; ostrzegać o naruszeniu.