---

name: cross-policy-diff
description: Dokonaj porównania między zasadami dla określonej możliwości, korzystając z OpenAI Readedness Framework v2, Anthropic RSP v3.0 i DeepMind FSF v3 jako odniesienia.
version: 1.0.0
phase: 15
lesson: 20
tags: [preparedness-framework, fsf, rsp, cross-policy, scaling-policy]

---

Biorąc pod uwagę konkretną zdolność graniczną (np. „autonomię dalekiego zasięgu”, „autonomiczną replikację i adaptację”, „automatyzację badań i rozwoju”), należy stworzyć różnicę między politykami pokazującą, w jaki sposób każda z trzech struktur klasyfikuje tę zdolność i jakie środki zaradcze uruchamiają.

Wyprodukuj:

1. **Klasyfikacja OpenAI PF v2.** Śledzone lub badawcze. Jeśli śledzono, nazwij wyzwalacze raportu Możliwości i zabezpieczenia. W przypadku badań należy zwrócić uwagę, że językiem polityki są „potencjalne” środki zaradcze.
2. **Klasyfikacja Anthropic RSP v3.0.** Który próg (ASL-3, AI R&D-4, zakodowany na stałe zakaz)? Jakie środki zaradcze (przypadek potwierdzający, bezpieczeństwo + wdrożenie)? Potwierdź, czy zobowiązanie występuje na poziomie antropijno-jednostronnym, czy na poziomie rekomendacji branżowych.
3. **Klasyfikacja DeepMind FSF v3.** Która domena (Cyber, Bio, ML R&D, CBRN)? Który poziom możliwości CCL lub śledzenia? Czy wywoływano zwodnicze monitorowanie osiowania?
4. **Podsumowanie zbieżności.** Czy w ramach trzech polityk jest zgodna co do ważności zdolności, czy też istnieje znacząca różnica zdań? Która klasyfikacja jest najbardziej rygorystyczna, a która najmniej?
5. **Zależność pomiaru.** Każda klasyfikacja zależy od pomiaru zdolności. Nazwij, w jaki sposób mierzona jest zdolność i który dostawca ewaluacji (METR, Apollo, wewnętrzny, zewnętrzny) jest właścicielem tego pomiaru.

Twarde odrzucenia:
- Twierdzenia dotyczące zgodności między politykami w oparciu o podobieństwo języka ogłoszeń bez dowodów na poziomie dokumentu.
- Dowolna klasyfikacja, która nie może wskazywać na konkretną klauzulę w dokumencie źródłowym.
- Traktowanie „kategorii badawczej” (OpenAI) jako równoważnej „kategorii śledzonej” – ma to różne konsekwencje operacyjne.

Zasady odmowy:
- Jeśli użytkownik nie może przedstawić fragmentów dokumentów źródłowych dla każdej klasyfikacji, odmów i najpierw zażądaj cytatów.
- Jeśli użytkownik traktuje istnienie polityki jako dowód zastosowania łagodzenia w praktyce, odmówi i zażąda dowodu zastosowania konkretnych środków łagodzących.
- Jeśli twierdzi się, że zdolność jest „objęta” ramami, ale słowo to nie pojawia się w dokumencie, należy odmówić i zażądać konkretnego odniesienia do klauzuli.

Format wyjściowy:

Zwróć dokument różnicowy zawierający:
- **Definicja możliwości** (jedno zdanie)
- **Wiersz OpenAI PF v2** (klasyfikacja, wyzwalacz, klauzula źródłowa)
- **Wiersz Anthropic RSP v3.0** (klasyfikacja, czynnik wyzwalający, zalecenie jednostronne a zalecenie)
- **wiersz DeepMind FSF v3** (domena, CCL/TCL, udział w zwodniczym dostosowaniu)
- **Podsumowanie konwergencji** (zgoda + znacząca różnica zdań)
- **Własność pomiaru** (dostawca eval, kadencja eval)
- **Rekomendacja czytelnika** (najbardziej rygorystyczna, najmniej rygorystyczna, uzasadniona)