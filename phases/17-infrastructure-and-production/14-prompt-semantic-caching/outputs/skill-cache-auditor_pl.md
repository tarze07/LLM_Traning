---

name: cache-auditor
description: Przeprowadź audyt szablonu podpowiedzi LLM i wzorca ruchu pod kątem możliwości buforowania. Zalecenia szybkiej restrukturyzacji, wyboru TTL, poprawki zrównoleglenia i progu pamięci podręcznej semantycznej.
version: 1.0.0
phase: 17
lesson: 14
tags: [caching, prompt-cache, semantic-cache, anthropic, openai, parallelization, ttl]

---

Biorąc pod uwagę szablon podpowiedzi, wzorzec ruchu (wskaźnik przybycia, współczynnik równoległy) i dostawcę (Anthropic, OpenAI, Gemini, vLLM na własnym serwerze), przeprowadź audyt pamięci podręcznej.

Wyprodukuj:

1. Struktura przedrostka. Podziel szablon na sekcje statyczne (buforowane) i dynamiczne (niebuforowane). Oznacz dowolną zawartość dynamiczną znajdującą się obecnie w przedrostku i zaproponuj przepisanie.
2. Wybór TTL. Antropiczne 5 minut (1,25x zapis) vs 1 godzina (2x zapis). Wybierz na podstawie współczynnika przybycia — 1-godzinne wygrane, jeśli prefiks zostanie ponownie użyty w ciągu godziny.
3. Audyt równoległy. Zliczaj żądania równoległe ze wspólnym prefiksem. Jeśli N > 2 i równolegle, wymagaj wzorca serializacji-najpierw-potem-fanout. Określ ilościowo oczekiwaną obniżkę rachunku.
4. Wybór pamięci podręcznej semantycznej. Zdecyduj, czy L1 jest tego wart. Czat otwarty: może nie (niskie trafienie). Ustrukturyzowane FAQ/wsparcie: tak. Ustaw próg cosinusa, zacznij od 0,95; dostrajaj w dół tylko z ocenami jakości odpowiedzi.
5. Oczekiwane oszczędności. Oblicz miesięczną różnicę w wartości $ w stosunku do wartości bazowej braku pamięci podręcznej, biorąc pod uwagę bieżący ruch i przewidywane współczynniki trafień.
6. Obserwowalne. Jedna metryka panelu kontrolnego, która wychwytuje regresje: współczynnik trafień w pamięci podręcznej L2 w ciągu ostatniej godziny; ostrzegaj, jeśli spadnie > 20%.

Twarde odrzucenia:
- Twierdzenie o „50% oszczędności” bez obliczania oczekiwanego współczynnika trafień i premii za zapis. Odmów — oblicz dla każdej warstwy.
- Pozostawienie zawartości dynamicznej w przedrostku, gdy proste przepisanie ją przenosi. Odmów podpisania.
- Wywoływanie żądań równoległych ze współdzielonym prefiksem bez wzorca pierwszej serializacji. Odmów — podaj 5-10-krotną inflację rachunku.

Zasady odmowy:
- Jeśli monit zawiera >80% zawartości dynamicznej, odmów obietnicy oszczędzania pamięci podręcznej. W najlepszym wypadku polecam buforowanie semantyczne.
- Jeśli próg semantycznej pamięci podręcznej spadnie poniżej 0,85 bez oceny jakości odpowiedzi, odrzuć - ryzyko halucynacji pamięci podręcznej.
- Jeśli dostawca nie obsługuje jawnej kontroli pamięci podręcznej (innej niż Anthropic, innej niż Gemini-v1) i tylko automatycznego buforowania, należy pamiętać, że współczynnik trafień jest oportunistyczny i nie jest gwarantowany.

Wynik: jednostronicowy audyt zawierający przepisanie prefiksu, TTL, wzorzec równoległości, próg L1, oczekiwane oszczędności, możliwe do zaobserwowania. Zakończ zaleceniem kwartalnego przeglądu: monity o ponowny audyt po każdej zmianie szablonu.