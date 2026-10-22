# pdf2md

Konwerter książek PDF (skan + warstwa OCR albo „cyfrowy” PDF z Worda) do
Markdowna. Powstał na potrzeby dwóch książek Jacka Schwagera w
`docs/trading/_books/`, ale radzi sobie też z innymi plikami o podobnym
układzie.

## Wymagania

- Python 3.9+
- `pip install pymupdf wordfreq`

`wordfreq` służy do podejmowania decyzji przy dzieleniu wyrazów na końcach
wersów (czy dywiz jest prawdziwy, np. `sell-side`, czy to złamanie wyrazu,
np. `consis-tency`).

## Użycie

```powershell
python tools\pdf2md\pdf2md.py "docs\trading\_books\Jack Schwager - Stock Market Wizards.pdf"
python tools\pdf2md\pdf2md.py "docs\trading\_books\Jack Schwager - The New Market Wizards.pdf"
```

Domyślnie wynik trafia obok PDF-a, pod nazwą pliku z rozszerzeniem `.md`.

Opcje:

| opcja | znaczenie |
|---|---|
| `-o plik.md` | ścieżka wyniku |
| `--style 1\|2\|auto` | wymuszenie układu (domyślnie wykrywany) |
| `--no-map` | ignoruje wbudowaną mapę rozdziałów (dla innych książek) |
| `--title "..."` | tytuł książki w nagłówku (dla nieznanych plików) |

Diagnostyka: `PDF2MD_STATS=1` wypisuje, ile razy zadziałała każda poprawka OCR.

## Co robi

1. **Wykrywa układ** — styl 1 to dwukolumnowy skan Finereadera (żywa pagina,
   wcięcia akapitów, pogrubione pytania, indeks w kolumnach), styl 2 to tekst
   z znacznikami `==== pytanie ====`.
2. **Usuwa paginę** — numery stron, żywą paginę (także „rozstrzeloną”:
   `S T U A R T W A L T O N`), resztki spisu treści z kropkami.
3. **Składa akapity** — po wcięciu, odstępie i długości wersu; skleja też
   akapity rozcięte przez łamanie stron.
4. **Skleja wyrazy** — decyduje, czy dywiz na końcu wersu jest prawdziwy
   (`wordfreq`), naprawia też „dywiz + spacja” w środku wyrazu.
5. **Odtwarza strukturę** — rozdziały/części/podrozdziały po foncie i rozmiarze
   pisma, numeracja lekcji poprawiana sekwencyjnie.
6. **Pytania prowadzącego** jako cytaty blokowe (`> **...**`), hasła
   glosariusza jako pogrubienia, indeks jako zagnieżdżone listy.
7. **Generuje spis treści** z linkami-anchorami (slugi w stylu GitHuba).
8. **Poprawia typowe błędy OCR** — tablica `OCR_FIXES` (np. `leam` → `learn`,
   `$I million` → `$1 million`, `tolcl` → `told`).

## Ograniczenia

- To **nie** jest uniwersalny konwerter PDF → Markdown. Nie wyciąga obrazków
  ani tabel — obie książki Schwagera są czysto tekstowe. Do dokumentów z
  wykresami/tabelami lepiej użyć `pymupdf4llm`, `marker` albo `docling`.
- `B1_CHAPTERS` (mapa strona → tytuł rozdziału) i `B1_DROP_COLS` są dopasowane
  do konkretnego skanu „Stock Market Wizards”. Dla innych plików używaj
  `--no-map` — wtedy tytuły rozdziałów są wykrywane z pisma (działa nieźle,
  ale bywa, że trzeba je ręcznie poprawić).
- `OCR_FIXES` to poprawki specyficzne dla tych dwóch skanów. Przy nowej
  książce warto je przejrzeć i dodać własne.
- W samych PDF-ach zdarzają się braki w warstwie tekstowej (nakładające się
  ramki tekstowe obcinają fragmenty zdań) — konwerter tego nie odzyska.

## Struktura kodu

- `page_lines()` — wyciąganie wersów ze spanów, rozbijanie „sklejonych”
  kolumn, scalanie fragmentów w jednej linii,
- `b1_*` — styl 1 (skan dwukolumnowy): `b1_items()` buduje akapity,
  `b1_index_items()` układa indeks kolumnami,
- `b2_*` — styl 2: `split_markers()` zamienia `====` na osobne linie,
  `b2_convert()` składa sekcje i pytania,
- `merge_mid_sentence()`, `join_hyphen()`, `fix_span_hyphen()` — sklejanie
  tekstu rozciętego przez łamanie stron i wersów,
- `apply_ocr_fixes()` — końcowe poprawki słownikowe.
