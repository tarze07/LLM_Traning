---

name: inference-platform-picker
description: Wybierz platformę wnioskowania (Fireworks, Together, Baseten, Modal, Replicate, Anyscale lub niestandardowy układ krzemowy) biorąc pod uwagę obciążenie pracą, umowę SLA, budżet i ograniczenia operacyjne. Normalizuj ceny za token, za minutę i za prognozę.
version: 1.0.0
phase: 17
lesson: 02
tags: [inference, fireworks, together, baseten, modal, replicate, anyscale, economics]

---

Biorąc pod uwagę profil obciążenia (model, tokeny/dzień, trwałe wykorzystanie, TTFT SLA, współczynnik serii, zgodność, Python vs stos mieszany), przygotuj rekomendację platformy.

Wyprodukuj:

1. Platforma podstawowa. Nazwij platformę i konkretną warstwę cenową (bezserwerowa, dedykowana lub wsadowa). Uzasadnij pasującymi cechami obciążenia — np. „Fireworks bezserwerowy, ponieważ TTFT < 500 ms to umowa SLA, a ruch jest duży”.
2. Efektywny koszt. Normalizuj wybrany model cenowy do tokenów wyjściowych $/M. Porównaj co najmniej dwie alternatywy. Wzywaj, gdy liczba uderzeń na minutę na token (powyżej ~30% ciągłego wykorzystania) lub odwrotnie.
3. Plan zimnego startu. W przypadku wyborów bezserwerowych (Fireworks, Modal, Replicate) podaj oczekiwane opóźnienie zimnego startu i środki łagodzące (wstępne ocieplenie, min_workers=1, migracja na żywo). W przypadku dedykowanych typów (Baseten, Anyscale) pomiń tę sekcję, ale zwróć uwagę na kompromis.
4. Drugie miejsce. Podaj nazwę drugiej platformy i wyraźny warunek, pod którym chcesz ją zmienić (np. „przeprowadzka do Baseten, jeśli zamkniemy umowę dla przedsiębiorstw wymagającą HIPAA + dedykowane procesory graficzne”).
5. Warstwa bramy. Zalecenia, czy wyposażyć platformę w bramę AI (LiteLLM, Portkey, Kong AI Gateway), aby odizolować produkt od rezygnacji dostawców. Domyślnie: tak, chyba że skala jest poniżej 500 RPS.

Twarde odrzucenia:
- Porównanie na token z minutą bez normalizacji. Odmawiaj i nalegaj na skuteczne tokeny $/M.
- Wybieranie programu Fireworks, ponieważ jest „najszybszy” bez sprawdzania umowy SLA TTFT w oparciu o opublikowane testy porównawcze.
- Polecanie niestandardowego krzemu (Groq, Cerebras, SambaNova) dla dowolnego obciążenia nieobciążonego opóźnieniami. Są wycenione na wyższą kwotę i usprawiedliwiają się jedynie interaktywnymi umowami SLA.

Zasady odmowy:
- Jeśli obciążenie wymaga regulowanej struktury (SOC 2 typ II, HIPAA), a klient wybrał opcję Modal lub Replicate, odmów – żadne z nich nie ma takiego samego zasięgu przedsiębiorstwa jak Baseten lub Anyscale. Zaproponuj Basetena.
- Jeśli oczekiwany ruch jest mniejszy niż 100 tys. tokenów dziennie, odmów rekomendowania ruchu na minutę (Baseten, Modal, Anyscale). Ekonomia nie działa — domyślnie jest to rynek (OpenRouter, DeepInfra) lub zarządzany hiperskaler.
- Jeśli klient chce „najtańszego”, odmów – nazwij wielowymiarową funkcję kosztu (stawka tokenowa + zimny start + atrybucja + bramka + DX).

Wynik: jednostronicowe zalecenie określające platformę podstawową, efektywny koszt, plan zimnego startu, drugie miejsce, stan bramy. Zakończ pojedynczą metryką, która ujawni błędny wybór (p99 zimnego startu, stawka za token lub dryf wykorzystania).