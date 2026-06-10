---

name: seq2seq-picker
description: Wybierz architekturę encoder-decoder vs decoder-only dla zadań sekwencja do sekwencji (seq2seq).
version: 1.0.0
phase: 7
lesson: 8
tags: [transformers, t5, bart, seq2seq]

---

Na podstawie opisu zadania seq2seq (tłumaczenie / podsumowanie / zamiana mowy na tekst (ASR) / ekstrakcja ustrukturyzowana / redagowanie/przepisywanie tekstu), rozkładu długości sekwencji wejściowych i wyjściowych oraz priorytetów dotyczących jakości i opóźnień wygeneruj:

1. Rekomendowana architektura: encoder-decoder (np. T5 / BART / styl Whisper), dostrojony instrukcyjnie model decoder-only lub model encoder-only z szablonem promptu. Podaj jednozdaniowe uzasadnienie.
2. Cel pre-trainingu: maskowanie fragmentów (span corruption dla T5), odszumianie (denoising dla BART), przewidywanie kolejnego tokena (autoregresyjne dla decoder-only) lub „pomiń pre-training, dostrój istniejący punkt kontrolny (checkpoint)”. Wskaż konkretny checkpoint.
3. Formatowanie danych wejściowych: prefiks zadania (task prefix - styl T5) vs prompt systemowy (styl decoder-only) vs surowe tokeny (styl BART). Uwzględnij obsługę tokenów specjalnych BOS/EOS.
4. Strategia dekodowania: wyszukiwanie wiązkowe (beam search) z określeniem szerokości wiązki (beam width) i kary za długość (dla zadań tłumaczenia/podsumowania) lub próbkowanie jądrowe (nucleus sampling/top-p) / min-p (dla zadań konwersacyjnych). Wskaż wybrane podejście.
5. Ewaluacja: metryka adekwatna do zadania (BLEU / ROUGE / WER / F1 / Exact Match). Podaj rozmiar zbioru testowego.

Odmawiaj rekomendowania modeli typu encoder-only do zadań generowania tekstu. Odmawiaj rekomendowania architektury encoder-decoder w przypadkach, gdy dane wejściowe stanowią historię konwersacji – w tym scenariuszu naturalnym wyborem jest architektura decoder-only. Oznacz jako błąd każdą rekomendację architektury decoder-only do zadań zamiany mowy na tekst (speech-to-text), która nie wskazuje modelu Whisper jako punktu odniesienia (baseline).
