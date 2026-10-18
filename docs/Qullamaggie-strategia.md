# Qullamaggie — strategia odtworzona z transkrypcji (2017–2023)

Dokument opisuje metody **Kristjana Kullamägi (Qullamaggie)** na podstawie 443 transkrypcji
jego streamów. Ma służyć jako podstawa do napisania algorytmów i backtestów, dlatego oprócz
opisu strategii zawiera parametry, pseudokod i listę niejasności.

---

## 0. Zakres i metoda

| Element | Wartość |
|---|---|
| Źródło | `transkrypcje/Qullamaggie/` |
| Liczba transkrypcji | **443 pliki TXT** |
| Zakres dat filmów | **2017-02-01 → 2023-12-15** |
| Objętość | 11,9 MB, **12 474 168 znaków** |
| Kanał | 588 filmów w uploads; 443 mają transkrypcję, 145 bez transkrypcji (głównie brak napisów) |
| Pokrycie roczne | 2017: 38, 2018: 2, 2019: 36, 2020: 204, 2021: 129, 2022: 24, 2023: 10 |

Lata **2018** oraz **2022–2023** są reprezentowane znacznie słabiej niż 2020–2021, dlatego
wnioski dla tych okresów mają niższą pewność i wymagają ostrożności przy backtestach.

**Metoda:** cały korpus przeskanowany pod kątem słów kluczowych (setupy, stop, sprzedaż,
rozmiar pozycji, selekcja, reżim rynkowy); następnie pełna lektura ok. 30 najbogatszych
metodycznie odcinków, w tym serii „Swing Trading School” (sierpień 2020), streamów o EP
(2022–2023) oraz odcinków o sprzedaży i obronie kapitału. Kluczowe liczby sprawdzono
w kontekście źródłowym.

**Oznaczenia pewności:**

- **[A] jawne** — powtarzana reguła, często formułowana wprost („always”, „my rule”, „I only”).
- **[B] wnioskowane** — regularność widoczna w przykładach transakcji, ale bez jednej definicji.
- **[C] niejasne** — ASR zniekształcił sens, liczby są sprzeczne albo reguła zmieniała się w czasie.

**Uwaga o jakości:** transkrypcje są automatyczne (ASR), bez interpunkcji. Tickers, ceny,
procenty i nazwy wskaźników bywają przekłamane (np. „vivap/evap” = VWAP, „high tide flag” =
high tight flag, „EP” bywa „EPS/DP”). Nie należy traktować pojedynczego cytatu liczbowego
jako twardego faktu — dokument podaje powtarzalne wzorce, nie stenogram transakcji.

---

## 1. Streszczenie w dziesięciu punktach

1. **Handluje momentum liderami, nie „tanimi” spółkami.** Względna siła, czysty trend i ruch
   są ważniejsze od fundamentów, choć fundamenty dają „paliwo” (EP).
2. **Najpierw reżim rynkowy.** Gdy Nasdaq/QQQ nie są w trendzie (10 SMA poniżej 20 SMA,
   spadające nachylenie), nie bierze nowych longów albo zmniejsza rozmiar.
3. **Rdzeniem jest Episodic Pivot (EP).** News/earnings + gap zwykle ≥10% + ogromny wolumen
   + wcześniejsza baza/zaniedbanie. Wejście na high pierwszej świecy 5-min, stop na low of day.
4. **Drugi filar to breakout z bazy/flagi/high tight flag.** Wcześniejszy duży ruch →
   konsolidacja z higher lows → zawężenie → wybicie na wolumenie.
5. **ORB (Opening Range Breakout) służy do egzekucji i daytradingu.** High/low pierwszych
   1/5/30/60 minut; long na ORH, short na ORL, stop po przeciwnej stronie zakresu.
6. **Ryzyko na trade: zwykle 0,3–1% konta (domyślnie ~0,5%).** Pozycja rzadko >20–25% konta;
   max ~1% average daily volume; stop zwykle low/high of day, nie szerszy niż ~1 ATR/ADR.
7. **Po 3–5 dniach sprzedaje 1/3–1/2, przenosi stop na break-even, resztę trailinguje
   10-day/10 EMA (małe spółki) lub 20-day (większe).** Pierwsze zamknięcie poniżej MA = wyjście.
8. **Nie ma sztywnego targetu.** Sprzedaje w siłę, redukuje paraboliczne ruchy, wychodzi przy
   failed breakout, słabości względnej i utracie MA. Celuje w 10R+ („home runy” 20–50R).
9. **Shorty są opcjonalne i trudniejsze.** Tylko wyczerpane, paraboliczne liderzy po 4–5 dniach
   wzrostów; nie ma „EP shorta”. Wejście na pierwszej czerwonej świecy / utracie VWAP / ORL.
10. **Niska skuteczność jest wpisana w system.** Skuteczność ~20–35%, większość setupów failuje;
    wynik robią nieliczne duże R. Dlatego liczy się proces, dziennik i konsekwencja.

---

## 2. Filozofia i źródło przewagi

- **Momentum + event-driven.** „Buy stocks that are going up and short stocks that are going
  down”; nie szuka dołków ani szczytów (2020-06-04).
- **Prostota.** „All you need is a five-minute chart” (2023-05-18); 10/20/50 SMA, VWAP,
  wolumen, ADR/ATR. Bez egzotycznych wskaźników.
- **Asymetria.** Małe straty, duże zyski; „if I can't realistically make 10× my initial risk,
  I'm probably not going to take the trade” (2020-07-30). Wiele swingów daje 20–50R.
- **Koncentracja i selektywność.** 10–15 pozycji, „never gonna have 30 positions again”
  (2023-05-23). Lepiej mniej, większych pozycji w najlepszych setupach.
- **Cena i wolumen trumpują fundamenty.** „Volume always trumps numbers” (2023-05-23);
  słabe wyniki mogą działać, jeśli reakcja ceny i wolumenu jest wyjątkowa.
- **Nie przywiązywać się do pozycji.** „Never marry a position”, „love your stops”
  (2023-05-18). Przegrane zamyka tego samego dnia.

---

## 3. Reżim rynkowy — filtr nadrzędny

### 3.1 Główny filtr: Nasdaq/QQQ 10/20 SMA

- **Zielono:** 10-day SMA rośnie, 20-day SMA rośnie, 10 > 20. Wtedy można brać nowe longi.
- **Ostrzeżenie:** 10 < 20 albo jedno z nachyleń skręca w dół → mniejszy rozmiar, tylko najlepsze setupy.
- **Czerwono:** oba nachylenia w dół / przecięcie → brak nowych longów, gotówka, ewentualnie shorty.
- W 2023 dodał **nachylenie 100-day** jako drugi filtr, żeby odsiać końcówki rajdów w bessie
  (2023-12-01).
- „Green zones / black zones” z crossoveru 10/20: „keep you in 80% of good times and out of
  80% of bad times” (2023-06-08).

### 3.2 Szerokość i przywództwo

- Wiele sektorów i spółek wybija jednocześnie = zdrowe otoczenie; pojedyncze wybicia = wysoki fail rate.
- **Liderzy vs laggardy:** gdy liderzy spadają, a laggardy rosną („leaders down, laggards up”),
  to ostrzeżenie o końcu ruchu (2020-05-27).
- **Dywergencja:** liderzy zieloni, gdy Nasdaq jest poniżej wczorajszych minimów = siła
  (2020-10-02).
- **Breadth:** zawężanie liczby wybijających się sektorów = redukcja ekspozycji (2021-01-20).

### 3.3 Ekspozycja portfela

- Sekwencja w potwierdzonym uptrendzie: **0% → 20–30% → full invested**; margines dopiero
  po zbudowaniu bufora zysku (2023-12-01).
- W złym rynku: gotówka tygodniami/miesiącami; „you wait for these periods… the rest of the
  time you just wait” (2023-12-01).
- W 2022 (bessa) nawet dobre EP failowały — mniejszy size, mniej transakcji, więcej shortów.

**Konsekwencja algorytmiczna:** filtr rynku jest nadrzędny wobec sygnału spółki. Ten sam setup
w „czerwonym” reżimie ma być odrzucany lub realizowany z 1/3–1/2 normalnego ryzyka.

---

## 4. Uniwersum i selekcja spółek

### 4.1 Twarde filtry (parametry do algorytmu)

| Filtr | Wartość z transkrypcji | Pewność | Uwagi |
|---|---|---|---|
| Cena | ≥ ~$8; penny/<$3 odrzucane | B | brak jednego twardego progu; zależy od konta |
| ADR (average daily range) | **min. 4–5%, najlepiej 6–7%+** | A | „Booking 2.7% — don't waste your time”; małe konto = wyżej |
| Dollar volume | **≥ $80M** w jego skanie; **$10–20M** dla małych kont; absolutne min. ~$10–15M | A | poniżej = za cienko, poślizg |
| Średni wolumen (skan EP) | **min. 1 mln akcji** (5-day average) | A | skan na małe/spółki o dużym ruchu |
| RS / ranking | top **1–2%** w horyzoncie 1/3/6 mies.; percentyl **90–95+** | B | różne sformułowania w różnych latach |
| MA | 10/20/50 rosnące, kąt ~**45°**, 10 > 20; „clean chart” | A | 10 SMA musi „dogonić” cenę, min. 2–3 dni |
| Baza | 2–3 tygodnie do 3–4 miesięcy (mid/large cap); dłuższa wymaga EP/katalizatora | B | brak twardego progu głębokości |
| Fundamenty | triple-digit EPS/revenue growth; min. mid-high double digit; guidance; 8 kwartałów + estymaty 2 lata | A | fundamenty dają „rocket fuel”, ale nie zastępują setupu |
| Float / market cap | brak twardego filtra; unikać nano-capów i ultra-thin | B | mały float = ryzyko squeezu przy shortach, nie filtr longów |
| Płynność pozycji | max **1% average daily volume** | A | kluczowe dla małych spółek |

**Definicje do implementacji:**

- **ADR(20)** = średnia z `(high - low) / close` za 20 sesji, wyrażona w % (nie mylić z ATR,
  który uwzględnia gapy i poprzednie zamknięcie). Qullamaggie mówi „ADR”, ale przy stopach
  używa też odległości w ATR.
- **Dollar volume** = `close * volume`, uśrednione za 20 sesji.
- **RS rank** = percentyl stopy zwrotu spółki względem uniwersum w horyzoncie 1/3/6 miesięcy.
- **Tightness** = zawężanie zakresu świec i higher lows; brak jednego wzoru — można mierzyć
  np. `ATR(5)/ATR(20)` lub szerokość konsolidacji / ATR.
- **Dzienne 10/20/50** traktować jako SMA; na wykresie 60-min używa EMA 10/20/65. Transkrypcje
  mieszają „MA/EMA”, więc parametry trzeba testować osobno.

### 4.2 Jak powstaje watchlista

- **Skany:** największe wzrosty 1/3/6 mies.; „momentum watchlist”; EP scan (7%+ day, high volume);
  liquid ADR/foreign; liquid ETFs; lower-liquidity/high-ADR (2020-09-16).
- **Skan EP (2023):** 50% wzrostu w **14 sesjach** w lookbacku **150 sesji** (~6 mies.),
  5-day average volume ≥1 mln → ~444 wyników. Wariant: 50% w **22 sesjach** w lookbacku
  2 miesięcy, min. 1 mln → ~205 wyników. Parametry są celowo zmieniane (88/110 sesji).
- **Premarket:** 15–30 minut przed otwarciem przegląda gappers +10–15%, newsy, earnings,
  gorące sektory; wejście dopiero po otwarciu, gdy widać wolumen.
- **Listy tematyczne:** np. 120 spółek AI/quantum przed ruchem sektora (2023-12-01).
- **Back watchlist:** każdy wart uwagi breakout wpisuje z datą i śledzi przez miesiąc, żeby
  budować bibliotekę wzorców i sprawdzać follow-through (2020-08-17, 2017-02-13).
- **Lista fundamentalna:** 30–50 najszybciej rosnących spółek; na niej szuka setupów
  (2021-01-20).

### 4.3 Czego unika

- **Wolne spółki i niskie ADR** — „waste of time”, brak dużych ruchów.
- **Za cienkie / nano-cap / low float** — problem z płynnością i poślizgiem; long tylko małym
  rozmiarem, short dopiero po prawdziwym blow-off.
- **Choppy / range / brak trendu** — „if a stock is in a range, ignore it”.
- **Extended / parabolic** — nie goni po dużym ruchu; czeka na konsolidację lub pullback.
- **Earnings w ciągu kilku dni** — nie kupuje breakoutu przed wynikami; trzyma przez earnings
  tylko z dużym buforem zysku.
- **Binarne biotech** — nie trzyma przez catalyst; wyjątkiem są EP na wynikach, które lubi,
  ale traktuje jako wysokie ryzyko.
- **Chińskie ADR** — nie zakaz (BABA, JD, PDD, NIO bywają grane), ale ryzyko regulacyjne i
  „battleground stocks” powoduje, że często przepuszcza.
- **Meme stocks** — tylko krótkoterminowo; długoterminowo „sucker” (2021-01-20).
- **Za dużo pozycji** — 30 pozycji to błąd; max zwykle 10–15.

---

## 5. Setup 1: Episodic Pivot (EP) — rdzeń strategii

### 5.1 Definicja

**EP = nagły, dużego kalibru ruch na newsie/earnings, któremu towarzyszy wyjątkowy wolumen
i który zaskakuje rynek.**

- News może być „mało ważny” — liczy się reakcja: CXAI +600% w 2 dni po przeciętnym
  komunikacie (2023-05-18).
- **Gap:** „most of the EPs I trade are gap openings of 10% or more”; bywają 50%, 100%, 200%
  (MDGL ~225%). Gap nie jest warunkiem koniecznym — EP może zacząć się intraday.
- **Wolumen:** recordowy lub wielokrotnie powyżej średniej; 4× average dla Celsiusa to
  „only about four times” i wciąż 5 gwiazdek (2023-05-18). „Volume always trumps numbers”
  (2023-05-23).
- **Baza/trend:** najlepsze EP wychodzą z wielomiesięcznej bazy/zaniedbania, z higher lows;
  spółka w trendzie spadkowym „is never a good EP” (2023-05-23).
- **Relative strength:** EP, które trzyma się podczas pullbacku rynku, jest lepsze (2023-05-19).
- **Minimum ruchu:** w jednym z odcinków mówi o **7–8%** jako minimum dla EP (2021-03-31);
  w praktyce najczęściej szuka 10%+ gapu.
- **Fail rate:** „sometimes they fail. In fact, they often fail” (2023-05-18).

### 5.2 Ocena jakości (5 gwiazdek)

| Element | Znaczenie |
|---|---|
| Wzrost EPS/revenue | triple-digit lub bardzo wysoki; minimum mid-high double digit |
| Guidance | duża podwyżka prognoz — często ważniejsza niż sam wynik |
| Baza | wielomiesięczna/ wieloletnia, higher lows, zaniedbanie |
| Wolumen | recordowy, wyraźnie ponad average; im większy, tym lepiej |
| Temat/sektor | gorący motyw (AI, quantum, weight-loss, crypto itp.) |

- **5 gwiazdek:** np. YEXT — „biggest volume ever”, wieloletnia baza, dobry wynik.
- **4 gwiazdki:** IOT — baza + higher lows + gap + duży wolumen + przyzwoite wyniki.
- **Ocena jest dyskrecjonalna**, nie ma jednego wzoru; algorytm powinien użyć score'u.

### 5.3 Skan EP

- **Skan bazowy [A]:** spółka wzrosła **≥50% w 14 sesjach** w ciągu ostatnich **150 sesji**;
  średni 5-dniowy wolumen **≥1 mln**. Wynik: ~444 spółki do przejrzenia.
- **Skan alternatywny [A]:** **≥50% w 22 sesjach** w ciągu ostatnich 2 miesięcy; min. 1 mln
  wolumenu; ~205 wyników. Parametry można zmieniać (88/110 sesji).
- **Skan przedopenowy [A]:** gappers **+10–15%**, news/earnings, gorący sektor; przegląd
  15–30 minut przed otwarciem. To nie jest sygnał wejścia — tylko lista kandydatów.
- **Skan nie jest świętym Graalem:** „max 3–4 scan” (2022-04-19); trzeba patrzeć na wykres,
  bazę i wolumen.

### 5.4 Wejście (entry)

- **Główny trigger [A]:** high **pierwszej świecy 5-min** (opening range high). Kupuje, gdy
  cena przebije ten poziom; stop = **low of day**.
  - APLD: najpierw zszedł pod low dnia, potem ~godzinę po open przebił high pierwszej świecy
    5-min; stop na LOD (2023-05-18).
- **Timing [B]:** większość dobrych EP startuje w pierwszych **3–10 minutach**; część dopiero
  30 min–2 h po open (GTLB ~1 h). „70–80% of my trading happens in the first 10–15 minutes”,
  większość w 30–45 min (2023-05-23).
- **Potwierdzenie [A]:** wolumen w pierwszych minutach; np. 300–400 tys. akcji na 1-min bar
  przy ~1 mln ADV (2023-06-08). Bez wolumenu nie ma EP.
- **Secondary entry [B]:** jeśli przegapił pierwsze wybicie — ORH 5-min/60-min, pullback do
  50-day, „pocket pivot” (2023-05-19, 2023-12-01). To plan B, nie rdzeń.
- **Nie gonić [A]:** jeśli stop (LOD) jest dalej niż ~1 ATR/ADR, odpuścić lub czekać na pullback
  (2020-08-06).
- **Przykłady:** IMGN kupiony na ORH ~$11; Carvana część premarket, dokupiona po ORH
  (2023-06-08).

### 5.5 Stop loss

- **Low of day (LOD)** — domyślny stop dla longów EP i swingów; „always or pretty much always”
  (2020-05-29). Short: high of day.
- **Brak stałego % stopa.** Rozmiar dobierany tak, by stop na LOD dawał akceptowalne ryzyko.
- **Filtr odległości [B]:** stop nie powinien być szerszy niż ~1 ATR/ADR; zwykle 0,25–0,5 ADR.
  Jeśli LOD jest zbyt daleko — czekać na dip albo odpuścić.
- **Gap przez stop:** brak jednoznacznej reguły w transkryptach; trzeba przyjąć założenie
  backtestowe (np. wyjście na open lub poślizg).
- **Nie uśredniać w dół.** „You should never buy stocks on weakness” (2020-08-06).

### 5.6 Prowadzenie pozycji

- **Dzień 1:** jeśli EP jako jedyny cofa się, gdy rynek i podobne spółki rosną — wyjść
  (przykład SRPT, 2023-05-19).
- **Po 3–5 dniach [A]:** sprzedać **1/3–1/2**, przenieść stop na **break-even**.
  - „in three to five days you're gonna sell a third or half and move your stop to break even”
    (2020-08-06).
  - MDGL: +50% w 3–4 sesje → trim (2023-05-19).
- **Trailing [A]:**
  - małe spółki / mikrocaps: **10-day SMA / 10 EMA**, a w 2023 dla mikrocaps także
    **10/20 EMA na 60-min**;
  - większe spółki: **20-day SMA** („usually the 20 works better on larger cap stocks”,
    2023-05-19);
  - wolniejsze: 50-day;
  - pierwsze zamknięcie poniżej MA = wyjście z reszty.
- **Dodawanie [B]:** tylko na potwierdzeniu siły (ORH, breakout), nie do stratnej pozycji.
- **Brak sztywnego targetu.** Sprzedaje części w siłę; „trim and trail” w trendzie
  (2023-06-08).

### 5.7 Wyjścia poza stopem

- **Failed EP / brak follow-through** — szczególnie gdy spółka nie reaguje na dobry news.
- **Słabość względna** — lider nie rośnie, gdy rynek/peers rosną; „day-1 relative weakness”.
- **Utrata 10/20/50 MA** — zależnie od charakteru spółki.
- **Paraboliczny climax** — 30% nad 10-day, 40–50% nad 20-day → agresywna sprzedaż w siłę
  (2020-06-24, 2021-02-10).
- **Reżim rynkowy czerwony** — redukcja ekspozycji, brak nowych longów.
- **Earnings** — trzymać tylko z buforem zysku; bez bufora redukować przed wynikami.
- **Gap-up, który wraca i nie utrzymuje poziomu** — często „one-time thing and over”
  (2023-06-09).

### 5.8 Czego nie robić na EP

- **Nie shortować EP.** „There is no such thing as an EP short” (2021-03-31); gap-downy są
  znacznie trudniejsze niż gap-upy.
- **Nie brać EP w spółce w downtrendzie** — „stock that's going down is never a good EP”
  (2023-05-23).
- **Nie kupować tylko dlatego, że gap jest duży** — potrzebny wolumen, baza i reakcja.
- **Nie trzymać przez binarne dane biotech** bez planu wyjścia.

---

## 6. Setup 2: breakout z bazy / flagi / high tight flag

### 6.1 Sekwencja

1. **Wcześniejszy duży ruch** — lider momentum, top 1–2% w horyzoncie 1/3/6 mies.
2. **Konsolidacja** — „a couple of weeks” do 3–4 miesięcy; higher lows; coraz ciaśniejszy zakres.
3. **Moving averages doganiają** — 10/20/50 rosnące, 10 > 20; cena „surfuje” po 10/20.
4. **Wybicie** — na wolumenie powyżej średniej; najlepiej z „big volume candle”.
5. **Wejście** — na range high / ORH; stop LOD.

### 6.2 Warianty

- **High Tight Flag (HTF):** duży ruch (często 2–3× w krótkim czasie) → ciasna flaga z higher
  lows → 10/20 doganiają → wybicie. „Always want tightness before a breakout” (2020-09-16).
- **Pullback do 10/20/50:** uptrend + higher lows + odbicie; wejście na pierwszej zielonej
  świecy 5-min, stop pod jej low (2021-06-03).
- **Gap-down reversal:** gap down po earnings w wsparcie, potem reclaim ORH; pierwsza zielona
  świeca 5-min jako trigger (2020-08-06).
- **Pocket pivot:** wybicie wewnątrz bazy, bez anticipacji (2021-01-20, 2021-03-31).
- **Stair-step:** step up → sideways → step up; kupuj następny step (2020-08-17).
- **IPO / recent IPO breakout** oraz **bottom bounce / secondary breakout** z dołów: grane
  w 2017, często microcapy i wysoki short interest; niższa jakość, mniejszy rozmiar
  (2017-02-13, 2017-04-02).

### 6.3 Filtry jakości

- **Tightness:** zakres konsolidacji coraz mniejszy, higher lows, brak szerokich/choppy świec.
- **Volume dry-up** w konsolidacji, potem wyraźny wzrost na wybiciu.
- **RS:** spółka trzyma się lepiej niż Nasdaq w dniu słabości; lider wybija przed indeksem.
- **Sektor:** gorący sektor podnosi jakość setupu; pojedyncza spółka w słabym sektorze ma
  niższą skuteczność.
- **Baza zbyt długa** (5+ miesięcy) wymaga EP/katalizatora, inaczej „dead money”.

### 6.4 Zarządzanie

Takie samo jak EP: stop LOD, partial 1/3–1/2 po 3–5 dniach, break-even, trailing 10/20 MA,
brak sztywnego targetu. Różnica: breakout często wymaga więcej cierpliwości i ma niższą
skuteczność w „straight-up” rynku; najlepszy jest po korekcie (2023-06-09).

---

## 7. Setup 3: ORB / daytrading

### 7.1 Definicje zakresu

| Zakres | Znaczenie | Uwagi |
|---|---|---|
| **1-min ORB** | high/low pierwszej świecy 1-min | najszybszy, najwięcej fałszywych wybić |
| **5-min ORB** | high/low pierwszych 5 minut | główny trigger EP i daytradingu |
| **30-min ORB** | high/low pierwszych 30 minut | używane jako „pierwsza świeca 60-min” na platformach z wyrównaniem do godzin |
| **60-min ORB** | high/low pierwszej godziny (lub pierwszej częściowej świecy 60-min) | wolniejszy, wyższa skuteczność, szerszy stop |

- „It can be both — I use combination of both” (2020-06-11) — 1-min i 5-min.
- „The first 60-minute candle is always 30 minutes” (2020-06-04) — konwencja platformy;
  algorytm powinien jawnie zdefiniować okno (np. 9:30–10:00 lub 9:30–10:30).

### 7.2 Long ORB

- **Warunki:** cena powyżej VWAP, względna siła, wolumen, gap up lub high-tide-flag.
- **Wejście:** przebicie **ORH** (najczęściej 5-min); można dodać na kolejnych ORH
  (1-min → 5-min → 60-min).
- **Stop:** **ORL** (opening range low); alternatywnie LOD.
- **Zarządzanie:** partial 1/3 przy ~1,5R (przykład Zoom, 2020-06-11; [B]); stop na break-even;
  trailing 10/20 EMA na 60-min; wyjście w pierwszych 1–1,5 h sesji.
- **Przykłady:** CLH — ORH 16.80 (1-min) i 17.80 (5-min); NCLH — gap down ~20%, long ORH,
  partiale w „pops”; AMC — „perfect high tide flag break” na 60-min (2021-06-03).

### 7.3 Short ORB

- **Warunki:** cena poniżej VWAP, słabość względna, wyczerpanie po parabolicznym ruchu.
- **Wejście:** przebicie **ORL**; alternatywnie pierwsza czerwona świeca 5-min, break
  poprzedniej świecy 5-min, utrata VWAP, odrzucenie na 60-min EMA.
- **Stop:** **ORH** / high of day / high lokalnej świecy 60-min.
- **Zarządzanie:** cover częściami w słabość; reclaim VWAP = zamknięcie shorta.
- **Przykłady:** Nikola — short ORL + dokładanie; TQQQ — short ORL, stop 94.50 (premarket high);
  AMC — short po odrzuceniu VWAP i pierwszej czerwonej 5-min (2021-06-03).

### 7.4 Gap-down reversal (long)

- Czekać na **pierwszą zieloną świecę 5-min**; kupić, stop pod jej low.
- Przykład: NCLH, gap down ~20%, long ORH (2020-06-11).

### 7.5 Kiedy nie handlować intraday

- **Chop / brak follow-through** — „worst type of market”; breakouts i breakdowns nie mają
  kontynuacji (2020-07-30).
- **Pierwsze 30 minut na shortach wyczerpanych nazw** — za wcześnie, czekać na squeeze.
- **Day 1/day 2 parabolii** — ignore; czekać na wyczerpanie i pierwszy sygnał słabości.
- **Halty/SSR** — egzekucja się psuje; unikać.
- **Wydarzenia binarne** — nie shortować przed danymi.
- **Brak setupów** — nie handlować „na siłę”.

### 7.6 Różnica swing vs daytrade

| Element | Swing (EP/breakout) | Daytrade (ORB) |
|---|---|---|
| Horyzont | dni–tygodnie | minuty–godziny |
| Główny trigger | ORH 5-min, breakout bazy | ORH/ORL 1/5/60-min |
| Stop | LOD/HOD | ORL/ORH, LOD/HOD, lokalna świeca |
| Zarządzanie | partial po 3–5 dniach, trailing 10/20 MA | partial 1,5R, BE, 10/20 EMA 60-min |
| Target | brak sztywnego; 10R+ | 1,5R + trailing; często 2–5R |
| Ryzyko | 0,3–1% | 0,3–0,5% |

---

## 8. Setup 4: shorty (opcjonalne)

### 8.1 Kontekst

- **Wyczerpany, paraboliczny lider**, nie tania spółka w downtrendzie.
- **4–5 dni wzrostów z rzędu** / duży ruch; **30% nad 10-day**, **40–50% nad 20-day** =
  strefa paraboliczna (2020-06-24, 2021-02-10).
- **Tight przed breakoutem:** im ciaśniejsza baza przed wybiciem, tym lepszy short po failu.
- **Gap up na earnings** = „sell the news”; idealny scenariusz (2020-08-05, ETSY).
- **Failed pullback:** gdy kolejna próba cofnięcia „fails and they keep going straight up”,
  to często zapowiada lepszy short (2020-08-19).
- **Nie shortować EP** — „no such thing as an EP short” (2021-03-31).

### 8.2 Wejście

- Pierwsza **czerwona świeca 5-min** po gapie / szczycie.
- **Break ORL** (opening range low) lub break poprzedniej świecy 5-min.
- **Utrata VWAP** / lower highs + odrzucenie na 60-min 10/20 EMA (2020-08-10).
- **60-min low break** z stopem na high świecy 60-min (2020-06-04).
- Starter, potem dodawanie po potwierdzeniu; nie uśredniać w stratę.

### 8.3 Stop i wyjście

- Stop: **high of day** / ORH / lokalny high; nie szerszy niż ~1 ATR.
- Cover: reclaim VWAP / 60-min range = zamknięcie; częściowe pokrycie 1/3–2/3 w słabość.
- Targety: 10-day/20-day MA, okrągłe poziomy; w szybkich ruchach 5–10% na raz.
- **Borrow:** koszt i dostępność locates są częścią decyzji; brak borrow = brak trade.
- **Low float / thin** — tylko po prawdziwym blow-off, nie dlatego że „już dużo spadło”.
- Shorty są dla doświadczonych; „do not get to short” dla początkujących (2020-08-10).

---

## 9. Tabela porównawcza setupów

| Setup | Kontekst / warunki | Trigger wejścia | Stop | Zarządzanie | Horyzont | Pewność |
|---|---|---|---|---|---|---|
| **EP** | news/earnings, gap ≥10%, rekordowy wolumen, baza/higher lows, RS | high pierwszej świecy 5-min | low of day | partial 1/3–1/2 po 3–5 dniach, BE, trail 10/20 MA | dni–tygodnie | A |
| **Breakout / HTF** | duży wcześniejszy ruch, 2–3 tyg.–4 mies. bazy, tightness, 10/20/50 rosnące | range high / ORH | LOD / ORL | jak EP; brak sztywnego targetu | tygodnie | A/B |
| **Pullback do 10/20/50** | uptrend, higher lows, MA jako wsparcie | pierwsza zielona świeca 5-min / reclaim MA | low świecy / swing low | trail MA, partial w siłę | dni–tygodnie | B |
| **Gap-down reversal** | gap down w mocny support, potem reclaim | pierwsza zielona świeca 5-min | low tej świecy | jak swing; szybkie partiale | dni | B |
| **ORB long** | momentum, gap/HTF, powyżej VWAP, wolumen | ORH 1/5/30/60 min | ORL / LOD | partial 1,5R, BE, 10/20 EMA 60-min | minuty–godziny | A |
| **ORB short** | słabość, poniżej VWAP, wyczerpanie | ORL / pierwsza czerwona 5-min / utrata VWAP | ORH / HOD | cover częściami, reclaim VWAP = exit | minuty–godziny | B |
| **Short paraboliczny** | 4–5 dni wzrostów, 30% nad 10-day, 40–50% nad 20-day, tight przed wybiciem | pierwsza czerwona 5-min / ORL / 60-min EMA | HOD / ORH | cover 1/3–2/3 w słabość, target 10/20-day | godziny–dni | B |

---

## 10. Ryzyko, rozmiar pozycji i dźwignia

### 10.1 Ryzyko na trade

- **0,3–0,5% konta** — jego typowy przedział w 2020 (2020-07-30).
- **0,5–1,2%** — w innym odcinku; „I would never risk more than 1%… most trades 0.5–1.2%”
  (2020-02-28).
- **1% lub więcej** w bardzo agresywnych okresach (2020-03-05).
- **Wniosek do algorytmu:** domyślnie **0,5%**, maks. **1%**; w „czerwonym” reżimie 0,25–0,5%.

### 10.2 Rozmiar pozycji

- Typowo **10–20% konta** na spółkę; **max 20–25%**; mid cap max ~20% overnight
  (2019-10-28, 2020-03-16, 2020-06-03).
- **5–20%** w normalnych warunkach; większe pozycje tylko w najwyższej jakości setupach.
- **10–15 pozycji**; „never gonna have 30 positions again” (2023-05-23).
- **Max 1% average daily volume** na pozycję (2023-05-18).
- **Margines** tylko po buforze zysku; w dobrym rynku ekspozycja 100%+, w złym 0–30%.
- Wzór: `size = (account * risk_pct) / (entry - stop)`, z dodatkowym limitem
  `size <= 0.01 * ADV20` i `position_value <= 0.25 * account`.

### 10.3 Skuteczność i R

- Win rate **~22–35%**; fail rate **~65–78%** (2020-07-30, 2020-08-05).
- Cel: **10R+**; „home runy” 20–50R; kilka takich transakcji pokrywa wiele małych strat.
- Przykłady: AAL 15 centów ryzyka na 3–4 USD ruchu (20–26R); Tesla 10–15 USD na 500 USD
  (33–50R) — to ilustracje, nie reguły.
- **Nie zwiększać rozmiaru po serii strat**; w chop zmniejszać.

---

## 11. Prowadzenie pozycji i wyjścia — tabela decyzyjna

| Sygnał / moment | Akcja | Pewność |
|---|---|---|
| Wejście | stop na LOD (long) / HOD (short) | A |
| Stop od wejścia > ~1 ATR/ADR | odpuść albo czekaj na pullback | B |
| Dzień 1: spółka słabsza niż rynek/peers | wyjdź lub zmniejsz | A |
| Po 3–5 dniach | sprzedaj 1/3–1/2, stop na break-even | A |
| Close < 10-day/10 EMA (małe spółki) | wyjdź z reszty | A |
| Close < 20-day (większe spółki) | wyjdź z reszty | A |
| Close < 50-day (wolne spółki) | wyjdź | B |
| 30% nad 10-day / 40–50% nad 20-day | sprzedawaj w siłę (parabolic) | A |
| Failed breakout / utrata VWAP / brak reclaim | wyjdź | A |
| Reżim rynkowy „czerwony” | brak nowych longów, redukcja | A |
| Earnings bez bufora zysku | zmniejsz lub wyjdź przed | B |
| Nowy szczyt / siła | przesuń stop, nie zamykaj bez sygnału | A |
| Brak setupów | gotówka, cierpliwość | A |

**Brak sztywnego targetu** — jedyne „targety” w transkryptach to oczekiwania (np. Carvana
40–50), nie reguły. Algorytm musi mieć własną politykę partiali/trailingu.

---

## 12. Psychologia i proces

- **Dziennik i statystyki:** prowadzi logi transakcji, analizuje drawdowny, wraca do watchlist
  po tygodniach/miesiącach.
- **Cierpliwość:** „the market doesn't care how smart you are”; czekanie na setup jest częścią
  strategii; w bessie siedzi w gotówce.
- **Straty:** „get used to losing”; najlepsi traderzy dobrze „tracą” (małe, kontrolowane straty).
- **Nie mścić się:** po stracie nie zwiększa rozmiaru „na odbicie”; wraca tylko przy nowym
  setupie.
- **Sprzedaż jest trudniejsza niż kupno:** przyznaje, że sprzedaje za wcześnie; rozwiązaniem
  są reguły (partial + trailing), nie próba trafienia szczytu.
- **Nie majstruje przy regułach:** „you won't outsmart the 10-day/10–20-day MA”
  (2020-12-18).
- **Overriding tylko w climaxie:** paraboliczny ruch uzasadnia sprzedaż wcześniej niż MA.

---

## 13. Ewolucja strategii 2017–2023

| Okres | Charakterystyka | Wnioski |
|---|---|---|
| **2017** | swing breakout z baz/flag, microcapy, watchlisty, ORH, stop LOD; brak jeszcze pełnego modelu EP | fundamenty metody już są: trend, baza, wolumen, LOD |
| **2018** | tylko 2 transkrypcje (przerwa) | brak danych do wniosków |
| **2019** | growth momentum, earnings breakouts, pierwsze EP, 10–20% konta na trade | EP zaczyna być nazwane |
| **2020** | najbogatszy rok: Swing Trading School, EP, HTF, daytrading ORB, ogromny bull | pełny zestaw reguł: 3–5 dni, 10-day trail, ADR, dollar volume |
| **2021** | memy, crypto, paraboliczne shorty, duże zmiany ekspozycji | shorty i zarządzanie ryzykiem |
| **2022** | bessa, EP failują, mniej longów, więcej gotówki/shortów | filtr rynku i adaptacja rozmiaru |
| **2023** | EP dominuje; breakouts „haven't really been working since 2021”; mikrocaps + AI/quantum; 20-day trail dla larger caps, 60-min EMA dla mikrocaps | powrót do korzenia: EP + reżim |

**Wniosek:** zestaw setupów jest stały, ale **wagi i parametry zależą od reżimu**. Algorytm
powinien mieć przełącznik reżimu (trend/range/bear) i osobne statystyki dla każdego.

---

## 14. Model algorytmiczny

### 14.1 Dane wejściowe

- **Dzienne:** OHLCV (split-adjusted), 10/20/50/100/200 SMA, ATR(14), ADR(20), dollar volume(20),
  relative strength rank (1/3/6 mies.), 52-week high, base detection.
- **Intraday:** 1/5/30/60-min OHLCV, VWAP, opening range, premarket high/low, volume ratio.
- **Eventy:** earnings date/time, EPS/revenue surprise, guidance, news sentline, sector.
- **Fundamenty:** EPS/revenue growth (8 kwartałów), estymaty 2 lata, market cap, float.
- **Rynek:** QQQ/Nasdaq 10/20/100 SMA, breadth, sektorowe ETF.
- **Egzekucja:** borrow availability/cost, slippage model, spread.

### 14.2 Pipeline doboru

```text
1. universe = US stocks/ETFs
   filter price >= 8
   filter dollar_volume_20 >= 20M          # 80M dla dużego konta
   filter ADR_20 >= 4.5%                    # ideał 6-7%
   filter avg_volume_5 >= 1M                # skan EP
2. regime = market_regime(QQQ)
   green: sma10 > sma20 and slope10 > 0 and slope20 > 0
   black: otherwise
3. candidates = union(
      ep_scan(up >= 50% in 14d, lookback 150d),
      ep_scan(up >= 50% in 22d, lookback 44d),
      premarket_gappers(gap >= 10%, news/earnings),
      breakout_watchlist(base/flag, rs_rank >= 90, sma10 > sma20)
   )
4. score = ep_score(candidate) + setup_score(candidate) + sector_score(candidate)
5. if regime == black: no new longs (or risk * 0.3)
```

### 14.3 Score EP (przykład do kalibracji)

```text
score = 0
if gap_pct >= 10:                 score += 2
if gap_pct >= 50:                 score += 1
if volume_ratio >= 4 or record:   score += 2
if earnings_or_guidance:          score += 2
if base_months >= 6 and higher_lows: score += 2
if rs_rank >= 90:                 score += 1
if hot_sector:                    score += 1
if price < 3 or adr < 4:          score -= 3
if in_downtrend:                  score -= 3
```

### 14.4 Wejście EP

```text
on each new 5-min bar after open:
    orh = high(first 5-min bar)
    orl = low(first 5-min bar)
    if price > orh and volume_confirmed:
        entry = price
        stop = low_of_day
        risk_per_share = entry - stop
        if risk_per_share > 1.0 * ATR:
            skip_or_wait_pullback()
        else:
            size = min(account * 0.005 / risk_per_share,
                       0.01 * ADV20,
                       0.25 * account / entry)
            buy(size)
```

### 14.5 Zarządzanie pozycją (state machine)

```text
day = 0
while position_open:
    if close < trail_ma:                 # 10-day small, 20-day large
        exit_all()
    if day in [3,4,5] and not trimmed:
        sell(1/3 to 1/2)
        stop = max(stop, entry)          # break-even
        trimmed = True
    if price >= entry + 10*initial_risk:
        sell_into_strength(1/3)
    if price > sma10 * 1.30 or price > sma20 * 1.45:
        sell_into_strength(1/3)
    if relative_weakness_today or failed_breakout:
        exit_all()
    day += 1
```

### 14.6 Wejście ORB

```text
orh = high(first N minutes)
orl = low(first N minutes)
if long and price > orh and price > vwap and volume_ratio > 1.5:
    buy; stop = orl
if short and price < orl and price < vwap and volume_ratio > 1.5:
    short; stop = orh
partial at 1.5R; trail 10/20 EMA 60-min; exit by 15:30
```

### 14.7 Parametry startowe

| Parametr | Wartość startowa | Pewność |
|---|---|---|
| EP gap min | 8–10% | A/B |
| EP volume ratio | ≥4× average lub record | B |
| EP base | ≥6 miesięcy, higher lows | B |
| EP entry | ORH pierwszych 5 min | A |
| Stop | LOD / HOD | A |
| Risk per trade | 0.5% (max 1%) | A |
| Max position | 20–25% konta | A |
| Max ADV | 1% | A |
| Partial | 1/3–1/2 po 3–5 dniach | A |
| Trail small | 10-day SMA / 10 EMA | A |
| Trail large | 20-day SMA | A |
| Trail micro 2023 | 10/20 EMA 60-min | B |
| Market filter | QQQ 10/20 + 100-day slope | A |
| ADR min | 4–5% (ideał 6–7%) | A |
| Dollar volume | 20M (small), 80M (large) | A/B |
| ORB window | 5 min (primary), 1/30/60 min | A |
| Daytrade risk | 0.3–0.5% | A |
| Daytrade target | 1.5R partial, trail | B |

---

## 15. Rozbieżności, które trzeba rozstrzygnąć przed backtestem

1. **Trailing 10 vs 20 vs 50.**
   - 10-day: domyślny dla małych/spółek momentum; 20-day: większe spółki; 50-day: wolne.
   - W 2023 mówi „I'm mostly using the 20 day for myself” (2023-06-08), a dla mikrocaps
     10/20 EMA 60-min (2023-12-01). **Rozwiązanie:** parametr zależny od market cap/ADR;
     testować 10 i 20 osobno.
2. **„3-day rule” nie istnieje dosłownie.** Powtarzalna reguła to **3–5 dni** i partial
   1/3–1/2; nie ma dowodu na sztywne wyjście po 3 dniach.
3. **Risk per trade 0,3–1,2%.** Nie ma jednej liczby. **Rozwiązanie:** 0,5% default, cap 1%.
4. **EP gap 7–10%.** Minimum 7–8% w jednym odcinku, „most” 10%+ w innym. **Rozwiązanie:**
   8% + news/volume + baza; testować 7/8/10%.
5. **Skan 1 mln — akcje czy dolary?** Transkrypt mówi „volume 1 million”; przy niskich cenach
   to może być 1 mln akcji, nie dolarów. **Rozwiązanie:** używać dollar volume ≥$20M jako
   filtra płynności i 1 mln akcji tylko jako historycznego parametru skanu.
6. **LOD vs 1 ATR.** LOD jest domyślny, ale jeśli stop jest szerszy niż ATR, odpuszcza.
   **Rozwiązanie:** twardy limit ryzyka na akcję = 1 ATR; inaczej brak wejścia.
7. **Shorty.** Zasady są mniej sformalizowane; dużo zależy od borrow i psychologii.
   **Rozwiązanie:** osobny, mniejszy moduł; nie mieszać z longami w jednym backteście.
8. **Pozycja 20–25% vs 10–15%.** Zależy od płynności i przekonania. **Rozwiązanie:** max 20%
   dla małych spółek, 25% tylko dla highly liquid; limit 1% ADV.
9. **Liczba pozycji.** „10–15”, ale „never 30” — w gorącym rynku bywało więcej.
   **Rozwiązanie:** max 15; twardy limit 20.
10. **ASR.** Wszystkie liczby wymagają weryfikacji na danych rynkowych; nie ufać tickerom
    i cenom z transkryptu.

---

## 16. Ryzyka backtestu i wdrożenia

- **Survivorship bias:** watchlisty i przykłady są wybrane po fakcie; trzeba użyć pełnego
  uniwersum, w tym spółek, które nie przetrwały.
- **Look-ahead bias:** earnings/news timestamp, premarket gap, dane fundamentalne publikowane
  po close; nie używać przyszłych danych.
- **Małe spółki:** poślizg, spread, limit 1% ADV, brak borrow; wyniki z large caps będą lepsze
  niż realne.
- **Regime dependence:** 2020–2021 to ekstremalny bull; testować osobno 2017, 2020, 2022, 2023.
- **Intraday:** ORB wymaga danych 1/5/60-min i modelu egzekucji; bez tego wyniki są nierealne.
- **Parametry:** EP gap/volume/ADR/MA trail są współzależne; robić walk-forward, nie optymalizować
  na całym okresie.
- **Psychologia:** reguły typu „nie trzymaj przez earnings” są trudne do zakodowania; przyjąć
  jawny filtr kalendarza.
- **Nie ma jednego „systemu”:** to zestaw setupów i zasad zarządzania, a nie sztywny algorytm.
  Backtest powinien mierzyć osobno EP, breakout, ORB i shorty.

---

## 17. Indeks kluczowych odcinków

| Data | Temat | Co zawiera |
|---|---|---|
| 2017-02-13 | Jan 2017 watchlists | budowa watchlist, ORH, gap earnings, stop LOD |
| 2017-02-18 | Jan 2017 watchlists Pt 2 | bazy, flagi, 50/100 MA, 5-star setup |
| 2017-04-02 | Feb 2017 watchlists | earnings gap, pierwsza/druga luka, follow-through |
| 2017-04-10 | Mar 2017 watchlist | pullback do MA, shorty, cierpliwość |
| 2019-03-10 | insanity stocks | shorty low-float, blow-off, ryzyko |
| 2019-10-21 | earnings trades | 10–20% konta na trade, EP |
| 2020-02-28 | risk | <1% ryzyka, rozmiar pozycji |
| 2020-05-27 | net long→short | hedging, redukcja ekspozycji |
| 2020-05-29 | LOD stop | „always low of the day” |
| 2020-06-02 | best swing market | ORB, 1/5/60-min, stop ORL |
| 2020-06-04 | best daytrading setup | ORB short, VWAP, 60-min |
| 2020-06-11 | put in the work | ORB, partiale, 10/20 MA |
| 2020-06-24 | defense | trailing, parabolic, redukcja |
| 2020-07-30 | process | risk 0.3–0.5%, 10R, ORB |
| 2020-07-31 | swing school | breakout, watchlist, ADR |
| 2020-08-04 | swing school | 3–5 dni, 10-day trail, ORH |
| 2020-08-05 | short LVGO | shorty, VWAP, parabolic |
| 2020-08-06 | earnings season | EP, 5-star, ADR, dollar volume, 3–5 dni |
| 2020-08-10 | sector rotation | shorty, rotacja, 60-min EMA |
| 2020-08-17 | random setups | selekcja, scan, back watchlist |
| 2020-08-19 | crypto school | te same zasady na crypto, shorty |
| 2020-09-16 | silver HTF | HTF, ADR, tightness, watchlist |
| 2020-10-02 | leaders leading | RS, filtry, 10/20 MA, leaders |
| 2020-12-18 | selling too early | sell rules, 3–5 dni, trailing |
| 2021-01-20 | extended breakdown | fastest growing, EP, 20-day |
| 2021-02-10 | TLRY | parabolic exits, partiale |
| 2021-02-23 | trade with rules | sell rules, defense, 10/20/50 |
| 2021-03-31 | NASDAQ tightening | EP criteria, ADR, CLF |
| 2021-06-03 | intraday momentum | ORB, first red/green 5-min, VWAP |
| 2021-11-09 | stand on own legs | EP, 50-day, laggards |
| 2021-12-31 | sell rules | 3–5 dni, 10-day, nie trzymaj przegranych |
| 2022-04-19 | EP scan | skan EP, filtry |
| 2023-05-18 | EP galore | definicja EP, skan 50%/14d/150d, 5-min ORH, LOD |
| 2023-05-19 | EP Kenny | 3–5 dni, 10/20 trail, 20-day dla larger caps |
| 2023-05-23 | EP follow through | volume trumps numbers, 30 pozycji |
| 2023-06-08 | EP AI/quantum | skan 50%/22d, 10/20, market filter |
| 2023-06-09 | market mechanics | ORH, LOD, 5-min volume |
| 2023-12-01 | EP party | 5-star EP, 100-day filter, 60-min EMA dla mikrocaps |

---

## 18. Checklist wdrożeniowy

- [ ] Dane dzienne + intraday + eventy + fundamenty.
- [ ] Filtr reżimu (QQQ 10/20/100) i przełącznik ekspozycji.
- [ ] Uniwersum: price/ADR/dollar volume/ADV.
- [ ] Skan EP (50%/14d/150d, 1M; wariant 22d).
- [ ] Scoring EP (gap, volume, earnings, base, RS, sector).
- [ ] Wejście ORH 5-min + stop LOD + limit 1 ATR.
- [ ] Sizing 0,5% risk, max 20–25% position, max 1% ADV.
- [ ] State machine: partial 3–5 dni, BE, trail 10/20, parabolic exit.
- [ ] Filtr earnings/news i „failed EP”.
- [ ] Osobny moduł ORB (5-min) i osobny moduł shortów.
- [ ] Dziennik transakcji i statystyki per setup/reżim.
- [ ] Walk-forward i testy na 2017/2020/2022/2023.

---

*Dokument wygenerowany na podstawie 443 transkrypcji z lat 2017-02-01–2023-12-15.
Wszystkie reguły należy zweryfikować na danych rynkowych; transkrypcje ASR zawierają
przekłamania. Dokument nie jest poradą inwestycyjną.*
