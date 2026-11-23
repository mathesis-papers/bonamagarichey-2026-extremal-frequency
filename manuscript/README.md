# Extremal letter frequency for one forbidden word

**Boundary corrections and a length-three extension of Bóna–Maga–Richey's extremal-frequency analysis**

Haobo Ma (ChronoAI Pte Ltd, Singapore) and Wenlin Zhang (National University of Singapore; ChronoAI Pte Ltd, Singapore).

The note classifies all binary forbidden words of lengths one, two and three. The maximizing words are respectively `0`, `00`, and the pair `001,100`. For each integer `m >= 2`, let `r_m` solve `r_m + ... + r_m^m = 1`. The families `0^m`, `10^m`, and `0^m1` have frequency `f_m = 1 / sum(i*r_m^i)`. Their bit-complements have frequency `1-f_m`, and `f_m` decreases strictly to `1/2`. A separate corollary treats singleton forbidden symbols over every finite alphabet. Comparison with all binary forbidden words of length at least four is not established by these arguments.

The frequencies are classical: the note credits Lekkerkerker, St. John, Chang, Kovačević, Baril–Kirgizov–Vajnovszki, and Richey at their precise statements. It gives self-contained proofs of the displayed classifications and consequences.

## Build

The main source is `note.tex`; all bibliography entries are included in it. Build with Tectonic 0.17.0:

```sh
tectonic note.tex
```

Alternatively, run `pdflatex note.tex` twice. No separate BibTeX database is needed.

## Mathematical coverage

The [pinned Lean declaration](https://github.com/the-omega-institute/trureturing/blob/d4a6bd75fd78850fed8cf60aebb6ce7fceffa2e1/D5/S1/Words/Forbidden/BonaMagaRicheyExtremalFrequency.lean) `D5.S1.Words.Forbidden.BonaMagaRicheyExtremalFrequency.result` negates the all-positive-length maximization statement using length one. The length-two and length-three classifications, run-frequency identities, strict monotonicity, and finite-alphabet corollary have written proofs in the note.

`verify.py` uses Python 3's standard library. It compares exact integer counts and first moments with independent recurrences and supplies rational enclosures for the relevant algebraic values:

```sh
python3 verify.py --output verification-generated.json
cmp verification.json verification-generated.json
```

The output states every finite range. These finite identities accompany, rather than replace, the infinite-limit proofs. `SHA256SUMS` identifies the source, metadata and deterministic mathematical output.

## License

Copyright © 2026 Haobo Ma and Wenlin Zhang. Creative Commons Attribution 4.0 International (CC BY 4.0; `cc-by-4.0`).
