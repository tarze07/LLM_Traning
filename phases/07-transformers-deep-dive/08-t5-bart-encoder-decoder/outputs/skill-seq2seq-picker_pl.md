---

name: seq2seq-picker
description: Wybierz koder-dekoder vs tylko dekoder dla nowego zadania sekwencja po sekwencji.
version: 1.0.0
phase: 7
lesson: 8
tags: [transformers, t5, bart, seq2seq]

---

Biorąc pod uwagę zadanie seq2seq (tłumaczenie / podsumowanie / zamiana mowy na tekst / wyodrębnienie strukturalne / przepisanie), rozkład długości wejścia i wyjścia oraz priorytety jakości i opóźnienia, wynik:

1. Architektura. Jeden z: koder-dekoder (T5 / BART / w stylu Whisper), dostrojony tylko do instrukcji dekoder, tylko koder + szablon podpowiedzi. Powód w jednym zdaniu.
2. Cel przedszkoleniowy. Uszkodzenie zakresu (T5), odszumianie (BART), następny token (tylko dekoder) lub „pomiń wstępne szkolenie, dostrój istniejący punkt kontrolny”. Nazwij punkt kontrolny.
3. Formatowanie wejściowe. Ciąg prefiksu zadania (styl T5) vs monit systemowy (tylko dekoder) vs surowe tokeny (BART). Uwzględnij obsługę BOS/EOS.
4. Strategia dekodowania. Kara za szerokość i długość wyszukiwania wiązki (tłumaczenie/podsumowanie) lub jądro/min-p (zadania podobne do czatu). Podaj, które z zadań.
5. Ewaluacja. Metryka odpowiednia do zadania: BLEU / ROUGE / WER / F1 / dokładne dopasowanie. Uwzględnij rozmiar podziału testowego.

Odmów polecania wyłącznie enkodera dla wyjść generatywnych. Odmów polecania kodera-dekodera, gdy dane wejściowe są już rozmową — dekoder naturalnie pasuje tylko do pamięci konwersacji. Oznacz dowolny wybór dekodera obsługującego wyłącznie mowę na tekst, nie wspominając o Whisper jako linii bazowej do pokonania.