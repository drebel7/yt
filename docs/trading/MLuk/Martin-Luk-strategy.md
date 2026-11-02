# Martin Luk — strategia odtworzona z transkrypcji i artykułów (2020–2026)

Dokument opisuje metody **Martina Luka** — zwycięzcy US Investing Championship 2025
(+969,8%), uczestnika USIC 2024 (+283,1%) i 2026. Powstał na podstawie 94 transmisji
z jego własnego kanału `@martinlukkt`, 16 transkrypcji innych kanałów oraz 3 artykułów
zapisanych w `docs/trading/MLuk/`. Ma służyć jako podstawa do implementacji algorytmów
i backtestów, dlatego obok opisu strategii zawiera parametry, pseudokod i listę niejasności.

---

## 0. Zakres i metoda

| Element | Wartość |
|---|---|
| Główne źródło | `transkrypcje/martinlukkt/` |
| Liczba transmisji | **94 pliki TXT** |
| Zakres dat | **2025-11-26 → 2026-10-23** |
| Objętość | ~1,97 mln znaków |
| Źródła zewnętrzne | 16 transkrypcji (TraderLion, Financial Wisdom, Zero to Alpha, Making Millions) |
| Artykuły | `docs/trading/MLuk/` — Forex Club, Trading Resource Hub (Substack), Financial Wisdom TV |
| Okres opisanej kariery | X 2020 → X 2026 |

**Ograniczenia korpusu:**

- Własny kanał obejmuje tylko okres **od listopada 2025** — wcześniejsze lata (2020–2024)
  znamy wyłącznie z wywiadów i artykułów, czyli relacji z drugiej ręki.
- Transkrypcje są automatyczne. Imiona i nazwiska są zniekształcane („Martin Luke",
  „Christian Kamagi", „Mark Manovven", „ankle VWAP" = anchored VWAP). Liczby bywają
  błędne — każdą kluczową wartość sprawdzono w co najmniej dwóch źródłach.
- Część transmisji to zapis na żywo: zawierają dygresje, pytania widzów i decyzje
  podejmowane ad hoc. Nie każda decyzja z transmisji jest elementem systemu.

**Oznaczenia pewności:**

- **[A] potwierdzone** — powtórzone w kilku niezależnych źródłach lub przez samego Luka.
- **[B] prawdopodobne** — jedno źródło, spójne z resztą systemu.
- **[C] niepewne** — pojedyncza wzmianka, możliwy błąd transkrypcji.

**Metoda:** przeskanowano cały korpus po słowach kluczowych (`stop`, `entry`, `pullback`,
`AVWAP`, `scanner`, `watchlist`, `position size`, `sell`, `ADR`, `theme`, `drawdown`),
a następnie przeczytano w całości najbogatsze metodycznie transmisje (m.in. „Kristjan
influence", „Watchlist rules, AVWAP…", „Premarket routine", „Selling into strength",
„Weekend scan", „26% Dec drawdown", „Sit-out power") oraz trzy artykuły.

---

## 1. Streszczenie w dziesięciu punktach

1. **Rdzeń systemu to asymetria, nie skuteczność.** Luk wygrywa ok. **22–25%** transakcji,
   ale średni zysk jest **5–7× większy** od średniej straty. W 2025 r. miał 209 wygranych
   i 731 przegranych transakcji, a mimo to +969,8%.
2. **Nie przewiduje stopy zwrotu — ogranicza ryzyko.** „Nie mogę przewidzieć, ile zarobię,
   ale mogę ograniczyć ryzyko" to jego podstawowa zasada.
3. **Stop jest najważniejszą decyzją.** Zawężenie stopu z 3% do 1,5% podwaja mnożnik R
   (25% zysk → 8,3R vs 16,7R). Zależność jest hiperboliczna: `R = zwrot / szerokość stopu`.
4. **Ryzyko na transakcję: 0,5% konta** (zakres 0,25–1%; w 2026 r. obniżane do ~0,3–0,4%
   z powodu nadaktywności). Dzienny limit strat ~2%.
5. **Stop: low of day (LoD)**, a jeśli dzień jest zbyt szeroki — low świecy wejściowej
   na 5 min. Zwykle **1–3%**, nigdy więcej niż **50% ADR** i praktycznie nigdy >5%.
6. **Trzy skanery:** pre-market (gap up), potent (wczorajsze najmocniejsze spółki),
   leader (weekend, największe ruchy 30 dni). Liczba nazw w skanach = wskaźnik zdrowia rynku.
7. **Trzy watchlisty:** Lead / Mediocre / Lag według położenia ceny względem EMA 50 i 150
   (wcześniej: uporządkowanie 9 > 21 > 50). Zmiana kategorii = sygnał rotacji tematycznej.
8. **Motyw (theme) przed wykresem.** Jeśli z jednej branży pojawia się wiele spółek,
   to ważniejszy sygnał niż pojedynczy lepszy wykres. Preferuje akcje z ADR > 5%
   i wysoką płynnością (100–200 mln USD obrotu dziennie).
9. **Setup numer jeden w 2025 r. to pullback**, nie breakout: silna spółka w konsolidacji,
   konfluencja AVWAP + EMA 9/21/50 + poziom horyzontalny + niezamknięta luka, wejście
   na intraday flush i odzyskanie wsparcia. Breakouty i EP pozostały w arsenale.
10. **Wyjścia są elastyczne, wejścia mechaniczne.** Sprzedaje 10–15% pozycji przy 3–5R
    lub gdy cena jest mocno rozciągnięta, resztę prowadzi po zamknięciu poniżej EMA 9
    (w silnych trendach 21/50). W drawdownie sprzedaje w siłę, w dobrym rynku trzyma dłużej.

---

## 2. Kim jest Martin Luk — wyniki i kontekst

| Rok | Wynik | Kontekst |
|---|---|---|
| 2020 | potrojenie konta w ~3–4 miesiące | start w X 2020 z HK$10 000 (~1 300 USD); small caps i SPAC-y |
| 2021 | +50%, następnie **−50%** drawdown | brak adaptacji do rotacji rynku, revenge trading, ignorowanie stopów |
| 2022 | oddanie zysków | rynek niedźwiedzia, powrót do złych nawyków |
| 2023 | **+91%** (win rate 23%) | przełom: transakcja CVNA +80%, zmiana myślenia na proces |
| 2024 | **+283,1%** — 6. miejsce USIC | 104 wygrane / 319 przegranych (win rate ~23–25%) [A] |
| 2025 | **+969,8%** — 1. miejsce USIC (rekord) | 209 wygranych / 731 przegranych (~940 transakcji) [A] |
| XII 2025 | **−26%** drawdown | 70–80 transakcji, 46% „zbędnych"; overtrading w chopie [A] |
| 2026 | ~+40% YTD w marcu; później +868,6% (lipiec, wg Forex Club) | 3. rok w USIC [B] |

**Ciekawostki biograficzne [B]:** pochodzi z Hongkongu; studiował Global Economics and
Finance na University of Hong Kong (2020–2024); zaczynał od rządowego dodatku
HK$10 000; nie pracował w banku inwestycyjnym ani funduszu; 80% podstawy tradingowej
przypisuje Qullamaggie, a fundament zarządzania ryzykiem — książkom Minerviniego.

**Uwaga o rozbieżności wyników:** jedno z opracowań Financial Wisdom podaje „1 358%"
za 2025 r. i „283%" za 2024 r. Wersja powtarzana przez samego Luka i TraderLion to
**969,8%** (2025) i **283,1%** (2024). Wersja 1 358% nie została potwierdzona —
najprawdopodobniej obejmuje inny okres lub zawiera błąd. Do backtestów należy przyjąć
969,8%.

---

## 3. Filozofia i źródło przewagi

### 3.1 Zdanie-klucz

> „Nie mogę przewidzieć zwrotu z transakcji, ale mogę ograniczyć ryzyko."

Cały system jest konsekwencją tego zdania. Luk nie szuka wysokiej skuteczności.
Szuka sytuacji, w których **stratę można zamknąć bardzo blisko**, a zysk może być wielokrotnością
ryzyka. Dlatego koncentruje się na jakości wejścia, a nie na trafności kierunku.

### 3.2 Matematyka R

```
R = zwrot_z_transakcji / szerokość_stopu
```

Przykład z jego prezentacji:

| Stop | Zwrot 25% | Zwrot 50% | Zwrot 75% |
|---|---|---|---|
| 3,0% | 8,3R | 16,7R | 25R |
| 1,5% | 16,7R | 33,3R | 50R |
| 1,0% | 25R | 50R | 75R |

Zawężenie stopu o połowę **podwaja R** przy tym samym ruchu ceny. Ponieważ stop jest
w mianowniku, poniżej ~2% zależność przyspiesza. To dlatego Luk potrafi mieć 22% win rate
i dodatnią expectancy.

### 3.3 Expectancy

Dane z 2024 r. [A]: 104 wygrane, 319 przegranych, średni zysk ~15%, średnia strata ~3%.

```
EV = 0,23 × 15% − 0,77 × 3% = 3,45% − 2,31% = +1,14% na transakcję
```

Dane z 2025 r. (209/731, średni zysk ~15%, średnia strata ~2,5%) dają ok. **+1,35%**
na transakcję. Przy ~940 transakcjach rocznie efekt składany jest ogromny.

### 3.4 Trzy filary

1. **Selekcja** — tylko szybkie, płynne spółki w gorących tematach.
2. **Wejście** — precyzyjne, przy wsparciu, z minimalnym stopem.
3. **Przetrwanie** — stały, mały risk per trade; brak pojedynczych katastrof.

---

## 4. Reżim rynkowy — filtr nadrzędny

Luk nie podejmuje decyzji „na wykresie spółki" w oderwaniu od rynku. Kolejność jest stała:
**rynek → sektor → spółka → wejście intraday**.

### 4.1 Sygnały reżimu

| Sygnał | Interpretacja bycza | Interpretacja niedźwiedzia |
|---|---|---|
| Szerokość rynku (breadth) | wiele spółek w Lead, mało w Lag | Lead się kurczy, Lag rośnie |
| IWM vs QQQ | IWM outperformance, higher highs | QQQ ciągnie, IWM słabszy |
| Skanery | dużo nazw w potencie/pre-market | mało nazw, skany krótkie |
| EMA indeksów | powyżej rosnących EMA 9/21/50 | poniżej, EMA opadają |
| Follow-through | przebicia się utrzymują | breakouty wracają, „pop and drop" |
| Laggards | dołączają (zdrowy rynek) | tylko mega-capy rosną |

### 4.2 Zasady praktyczne

- **Gap down indeksów do wsparcia** (np. EMA 150) zwiększa skuteczność ORB long —
  bo rynek ma wyższe prawdopodobieństwo odbicia, a pojedyncze spółki są silniejsze od indeksu.
- **Gap up indeksów** przy wykupieniu — Luk woli go unikać; woli wejścia na cofnięciu.
- **Po korekcie** to najlepszy czas na position trading, bo trends trwają dłużej.
- **W chopie** system ciasnych stopów generuje „death by a thousand cuts" — dlatego
  w grudniu 2025 r. 70–80 transakcji dało −26%, mimo że pojedyncze straty były małe.

### 4.3 Equity-curve feedback [A]

> Jeśli twoje transakcje działają, gdy indeksy są słabe — kontynuuj ostrożnie.
> Jeśli indeksy są silne, a twoje transakcje nie działają — szybko zweryfikuj siebie.

To jego sposób na odróżnienie „rynek mi nie pasuje" od „ja popełniam błędy".

---

## 5. Uniwersum i selekcja

### 5.1 Trzy skanery

| Skaner | Kiedy | Co pokazuje | Zastosowanie |
|---|---|---|---|
| **Pre-market** | przed otwarciem | spółki z gap up na dużym obrocie | EP, opening range breakout |
| **Potent** | codziennie po zamknięciu | wczorajsze najsilniejsze spółki | rotacja sektorowa, świeże tematy |
| **Leader** | weekend | największe ruchy z 30 dni | względna siła, trend wielotygodniowy |

Skanuje w godzinach porannych czasu Hongkongu, czyli **po zamknięciu sesji US** —
wtedy rynek „nie rusza się", więc decyzje są bardziej racjonalne. Rutynowo zajmuje mu to
**30–45 min** (w korekcie 15–20 min).

### 5.2 Filtry uniwersum

| Filtr | Wartość | Pewność |
|---|---|---|
| ADR (average daily range) | **> 5%** preferowane | A |
| Płynność (average dollar volume) | **> 100 mln USD**, od 2026 r. **> 200 mln USD** | A |
| Cena akcji | unika tanich (< 5 USD) — spread i poślizg | A |
| Market cap | nie jest filtrem samym w sobie; płynność ważniejsza | A |
| Liczba spółek na watchliście | celowo ograniczana; nowe tylko wyjątkowo dobre | B |

### 5.3 Watchlisty

Obecna, uproszczona wersja [A]:

| Lista | Reguła | Przeznaczenie |
|---|---|---|
| **Lead** | cena > EMA 50 **i** EMA 50 > EMA 150 | long candidates |
| **Mediocre** | pomiędzy | obserwacja, bez akcji |
| **Lag** | cena < EMA 50 **i** EMA 50 < EMA 150 | short candidates |

Wcześniejsza wersja używała porządku EMA 9/21/50 (jak w Qullamaggie). Luk sam przyznaje,
że reguły zmieniał wielokrotnie i stara się je upraszczać, bo przegląda wykresy ręcznie.

**Rotacja list = sygnał.** Gdy kilka spółek awansuje z Mediocre do Lead, oznacza to,
że w danym sektorze pojawia się siła. Gdy Lead się kurczy, a Lag rośnie — rynek słabnie.

### 5.4 Temat (theme) — najważniejszy filtr

> „Jeśli dwa identyczne wykresy, jeden w gorącym sektorze, drugi nie — wybieram gorący.
> Czasem wolę nawet gorszy wykres, ale lepszy sektor."

Zasady:

1. Jedna spółka z branży to przypadek. **Kilka spółek z tej samej branży w tym samym dniu
   to temat.**
2. Nowy temat (nie będący jeszcze liderem) jest ważniejszy niż wzmocnienie istniejącego.
3. W ramach tematu wybiera **najmocniejszą** spółkę (np. z quantum: QBTS, IONQ, RGTI),
   najlepiej najbardziej płynną.
4. Temat może się wypalić — wtedy nawet dobre wykresy przestają działać.

---

## 6. Setup 1: Pullback do wsparcia (rdzeń 2025)

To setup, który odpowiada za większość wyniku w 2025 r. Luk zaczął go rozwijać, gdy
breakouty przestały działać: „coraz więcej spółek cofało się do wsparć i odbijało".

### 6.1 Warunki wstępne (kontekst)

| Warunek | Opis |
|---|---|
| Silny trend | spółka w uptrendzie, nie w downtrendzie; „buy weakness in strength, not weakness in weakness" |
| Względna siła | wzrost **> 30%** w okresie 1, 3 lub 6 miesięcy |
| Konsolidacja | najlepiej **≥ 8 tygodni**, z wyższymi dołkami |
| EMA | 9/21/50 rosnące; cena „surfuje" po EMA |
| Range | zawężający się (volatility contraction) |
| Temat | gorący sektor, wysoki ADR |

### 6.2 Strefa wsparcia — konfluencja

Wejście ma sens tylko wtedy, gdy w jednym miejscu spotyka się **kilka niezależnych poziomów**:

- **AVWAP** zakotwiczony na istotnym swing high (opór → wsparcie) lub swing low,
- **EMA 9 / 21 / 50** (na dziennym lub 60-min),
- **poziomy horyzontalne** (poprzednie szczyty/dołki),
- **niezamknięta luka** (gap fill),
- liczby okrągłe (np. 100 USD).

Im więcej poziomów w jednej strefie, tym wyższe prawdopodobieństwo, że kupujący tam wrócą.
Luk nazywa to **multiple-edge entry** — różni traderzy patrzą na różne wskaźniki, ale widzą
to samo wsparcie.

### 6.3 Wyzwalacz wejścia

Sekwencja:

1. Cena cofa się w strefę wsparcia (dzienny setup).
2. Zejście na **60 min / 15 min / 5 min / 1 min**.
3. Czeka na **flush** — szybkie, paniczne zejście w support.
4. Wejście, gdy cena **odzyskuje poziom**:
   - wraca powyżej AVWAP / EMA,
   - wychodzi na plus dnia,
   - przebija high poprzedniej świecy 5-min,
   - zamyka się powyżej wsparcia.
5. Stop: **low of day** albo **low świecy wejściowej**, jeśli LoD jest zbyt daleko.

### 6.4 Przykłady (z artykułów; dane przybliżone)

| Spółka | Kontekst | Ryzyko | Wynik | R |
|---|---|---|---|---|
| IONQ | konsolidacja, AVWAP z szczytu, EMA 9/21 | 4–7% | +125%, wyjście po 9 EMA +76% | ~20R |
| TSLA | 5-mies. baza, flush do gapu i EMA 9 | < 1% | +24% | ~24R |
| AMPX | baza 2 mies., AVWAP + EMA 9 | 1,2–2,2% | +40–55% | ~30R |
| SNDK | baza 2 mies., flush do AVWAP | ~4% | +126% | ~31R |
| RMLD | baza 5 mies., AVWAP + EMA 9 | ~1,5% | +45–84% | ~30R |
| SYRE | AVWAP + EMA 21 | ~3% | +62–80% | ~20R |

**Uwaga:** to przykłady z artykułów (źródło wtórne), nie z samych transmisji. Traktować
jako ilustrację, nie jako dowód statystyczny.

### 6.5 Dlaczego to działa

- Wejście jest **bliżej wsparcia** niż breakout, więc stop jest mniejszy.
- Ten sam ruch daje większe R.
- Mniejszy stop pozwala na **większą pozycję** przy tym samym ryzyku dolarowym.
- Wiele takich transakcji jest przegranych — ale kilka dużych wygrywa cały rok.

---

## 7. Setup 2: Breakout / prior day high / inside day

### 7.1 Warianty

| Wariant | Warunki | Stop |
|---|---|---|
| **Prior day high** | konsolidacja, cena przebija szczyt poprzedniego dnia | LoD lub low świecy |
| **Inside day + gap** | jedna/dwie świece inside, gap up w górnej części zakresu, przebicie szczytu | low inside day |
| **Opening range breakout (ORB)** | po otwarciu, przebicie high pierwszych 1–5 min | low opening range |
| **Re-entry** | pierwszy breakout fails, ale struktura bycza; drugi breakout z konsolidacji 5-min nad EMA 9 | low konsolidacji |

### 7.2 Zasady

- Breakout **musi** mieć kontekst: rynek, sektor, EMA, względna siła.
- Luk nie kupuje breakoutu „w próżni" — jeśli rynek jest słaby, breakout ma niższą skuteczność.
- Inside day + gap daje najciaśniejszy stop (często **1,5–2,5%**).
- ORB stosuje głównie do EP i spółek z gapem.
- Nie używa wolumenu jako warunku wejścia na breakout — uważa, że niski wolumen
  w uptrendzie nie musi oznaczać słabości.

### 7.3 Przykład: GME 2024 [A]

- Wejście: ORB na 1-min, cena 26,30 USD, stop 25,47 USD.
- Stop postawiony na low poprzedniej świecy 1-min, nie na LoD (LoD dawałoby > 6% ryzyka).
- Wyjście: połowa przy 12R (~37 USD, +37%), reszta przy ~56 USD.
- Wynik: ~40R. To był EP, nie klasyczny breakout.

---

## 8. Setup 3: Episodic Pivot (EP)

EP to nagły, newsowy ruch — najczęściej gap up po wynikach, kontrakcie, decyzji regulatora.
Luk nauczył się go od Qullamaggie i stosuje do dziś.

### 8.1 Warunki

| Element | Wartość |
|---|---|
| Przyczyna | wyniki, kontrakt, zmiana regulacyjna, przejęcie |
| Gap | wysoki, na dużym obrocie |
| ADR | wysoki (> 5%) |
| Temat | spółka w gorącym sektorze lub nowy temat |
| Pozycja w bazie | najlepiej blisko szczytu bazy lub po długiej konsolidacji |
| Wejście | ORB 1-min/5-min albo pierwszy pullback do EMA 9 na 5-min |

### 8.2 Stop

- Low of day, jeśli odległość jest akceptowalna (< 5%).
- Jeśli nie — low świecy wejściowej lub low ORB.
- W praktyce EP daje często najciaśniejsze stopy (1–3%).

### 8.3 Zarządzanie

- EP często startuje szybko; Luk sprzedaje część w siłę, gdy ruch jest gwałtowny.
- Jeżeli po gapie cena się cofa i nie odzyskuje poziomów — wychodzi.
- Przykłady: AMD (X 2025, +35–40%), COIN (2024), GME (2024), quantum names (2025).

---

## 9. Setup 4: Parabolic long / short i mean reversion

### 9.1 Parabolic long (panic bottom)

Warunki:

- rynek po **2–3 gap downach**, panika, wykupienie po stronie sprzedających,
- cena **20% poniżej EMA 1h** (przykład: kwiecień 2025),
- wejście na **intraday strength**: ORB 1-min, breakout 5-min, powrót nad EMA,
- stop ciasny, poniżej low świecy,
- wyjście szybkie, w siłę — to trade o wysokiej zmienności, nie position trade.

Przykład: TQQQ w kwietniu 2025 — 13R w pół godziny.

### 9.2 Parabolic short (top formacje)

Warunki:

- parabola z **rekordowym wolumenem** tygodniowym,
- pierwsze załamanie, potem retest i **lower high**,
- wejście na cofnięciu do opadającej EMA 9/21,
- wyjście na zamknięciu powyżej EMA 9.

Przykłady: złoto i srebro (I 2026), MSTR, ARKK.

### 9.3 Short pullback

- Tylko w słabych spółkach i słabych sektorach.
- Cena cofa się do **opadającej EMA 9/21/50**.
- Nie shortować silnego tygodniowego uptrendu ani najsilniejszego sektora.
- Wyjście: zamknięcie powyżej EMA 9 (np. złoto/srebro w marcu 2026).

---

## 10. Wejścia intraday — warsztat

### 10.1 Wielotimeframe

| TF | Rola |
|---|---|
| **Weekly** | struktura, baza, EMA 9/21/50, VCP, inside week |
| **Daily** | setup, konsolidacja, konfluencja wsparć |
| **60 min** | trend i wsparcie średnioterminowe, EMA 9/21/50 |
| **15 min** | konsolidacja, breakout |
| **5 min** | główny trigger (prior bar high, EMA 9/21) |
| **1 min** | precyzja EP/ORB, minimalizacja stopu |

Typowa sekwencja: weekly → daily → 60 min → 5 min → 1 min.

### 10.2 Reguły triggera

- **Prior bar high** na 5-min — najczęstszy trigger.
- **Opening range high** — dla EP i gapów.
- **Reclaim** poziomu (AVWAP/EMA/gap) — dla pullbacków.
- **Flush + reclaim** — dla paniki.
- Stop zawsze **przed** wejściem, nie po.

### 10.3 Czego nie robi

- Nie kupuje „w ciemno" spadającej ceny — czeka na potwierdzenie (odzyskanie poziomu).
- Nie kupuje późno rozciągniętych nazw („nie kupuję na czwartym zielonym dniu").
- Nie handluje newsów bez kontekstu technicznego.
- Nie używa fundamentalnych wskaźników poza tematem.

---

## 11. Ryzyko i rozmiar pozycji

### 11.1 Parametry

| Parametr | Wartość | Pewność |
|---|---|---|
| Ryzyko na transakcję | **0,5%** konta (0,25–1%) | A |
| Dzienny limit strat | **~2%** (4 kolejne straty przy 0,5%) | B |
| Maks. pozycja | **25–30%** portfela; max **35%** dla płynnych large capów | A |
| Małe/mikro spółki | **25–30%**, ze względu na gap risk | A |
| Ekspozycja całkowita | do **250%** (margines) w bardzo dobrym rynku | A |
| Stop | **< 3%** typowo; **< 50% ADR**; max 5% | A |
| Dźwignia | używa marginesu, ale ogranicza ryzyko na transakcję | A |

### 11.2 Wzór na pozycję

```
risk_dollar = equity × risk_pct
shares = risk_dollar / (entry − stop)
position_value = shares × entry
```

Przykład: konto 150 000 USD, risk 0,5% = 750 USD; wejście 44,20, stop 43,40
(różnica 0,80) → 937 akcji ≈ 41 000 USD ≈ 28% portfela.

### 11.3 Sizing a jakość setupu

- Bazowo ta sama wartość ryzyka.
- Przy lepszym setupie (A+) może zwiększyć risk (np. do 1%), przy słabszym (B) zmniejszyć.
- W drawdownie **zmniejsza** rozmiar, nie zwiększa.
- Po serii strat wraca do mniejszego rozmiaru, żeby odbudować „mental capital".

### 11.4 Gap risk

- Mikro i małe spółki mogą stracić 30–35% jednego dnia (przykład: SERV).
- Dlatego rozmiar jest mniejszy, a stop nie chroni przed gapem.
- Luk akceptuje ten risk, ale ogranicza ekspozycję.

### 11.5 Equity do sizingu

- Domyślnie **real-time equity**.
- Przy dużych niezrealizowanych zyskach stosuje **dyskonto ~10%**, żeby nie przesadzić z rozmiarem.
- W 2026 r. skłania się ku liczeniu od **zrealizowanego** kapitału, bez niezrealizowanych zysków.

---

## 12. Prowadzenie pozycji i wyjścia

### 12.1 Filozofia

> „Nie mam bardzo sztywnych zasad sprzedaży. Sprzedaję w siłę, gdy pozycja jest rozciągnięta."

Wejścia są mechaniczne i precyzyjne; wyjścia są **dyskrecjonalne**. To świadoma asymetria:
ciasne wejście chroni kapitał, elastyczne wyjście maksymalizuje zysk.

### 12.2 Zasady

| Sytuacja | Działanie |
|---|---|
| Zysk **3R / 5R** | sprzedaż **10–15%** pozycji |
| Cena **10–15% powyżej EMA 9** | rozważ sprzedaż części |
| Pozycja urosła > 35% portfela | przycina |
| Euforia / parabolica | sprzedaje w siłę |
| Trend silny, wczesne wejście | trailing po **EMA 21**, czasem **50** |
| Standard | zamknięcie dnia poniżej **EMA 9** |
| Drawdown | sprzedaje w siłę, nie czeka na stop |
| Silny rynek + poduszka zysku | trzyma dłużej, mniej częściowych wyjść |

### 12.3 Horyzont

- Swing: dni do tygodni.
- Docelowo chce trzymać zwycięzców **≥ 5 tygodni**, ale przyznaje, że sprzedaje zbyt wcześnie.
- Przykład SMCI 2024: sprzedał całość za wcześnie i stracił kolejne +100% w 3–4 tygodnie.

### 12.4 Re-entry

- Po stopie może wrócić, jeśli struktura i rynek nadal sprzyjają.
- Nie stawia sztywnego limitu „nie wchodzę ponownie".
- Ważne: re-entry nie może być revenge tradingiem.

---

## 13. Psychologia i proces

### 13.1 Filtr mentalny

> „Zapytaj siebie: co zrobiłby wielki trader? To eliminuje ponad 90% losowych i revenge'owych transakcji."

### 13.2 Największe błędy (sam je wymienia)

1. **Revenge trading** — szczególnie po stratach i w drawdownie.
2. **Zwiększanie ryzyka w serii strat** — odwrotność tego, co powinien robić.
3. **Niestosowanie stopów** — pojedyncze duże straty.
4. **Overtrading w chopie** — grudzień 2025: 70–80 transakcji, 46% zbędnych, −26%.
5. **Koncentracja na small/micro caps** przy ocenie rynku — zniekształca obraz.
6. **Zbyt wczesne sprzedawanie zwycięzców** — największy koszt alternatywny.

### 13.3 Rozwiązania

| Problem | Rozwiązanie |
|---|---|
| Overtrading | reduce number of trades; cel < 800/rok, docelowo 500 |
| Revenge trading | filtr „co zrobiłby wielki trader"; przerwa |
| Brak dyscypliny | twarde stopy w systemie brokera; nie przesuwa stopów |
| Przeciążenie psychiczne | „sit-out power" — czasem najlepszy trade to brak trade'u |
| Drawdown | zmniejszenie rozmiaru, odbudowa „mental capital" |
| Zbyt wczesna sprzedaż | próba trzymania ≥ 5 tygodni, częściowe wyjścia |

### 13.4 Dziennik

- Wczesny etap: codzienny journal.
- Obecnie: Excel z transakcjami + okazjonalne notatki z wnioskami.
- Regularnie analizuje transakcje i wyciąga wnioski.

### 13.5 Procenty, nie dolary

Od Qullamaggie: myśl w **procentach konta i R**, nie w dolarach. To umożliwia skalowanie
konta i eliminuje emocje związane z kwotami.

---

## 14. Ewolucja strategii 2020–2026

| Okres | Styl | Kluczowe zdarzenie |
|---|---|---|
| 2020 | small caps, SPAC, momentum | start, potrojenie konta |
| 2021 | breakouts, EP, słaba dyscyplina | −50% drawdown, lekcja |
| 2022 | bear market, overtrading | oddanie zysków |
| 2023 | breakouts + EP, większa dyscyplina | +91%, przełom CVNA |
| 2024 | breakouts, EP, tight stops | +283%, 6. miejsce USIC |
| 2025 | **przejście na pullbacki** | +969,8%, rekord USIC |
| 2026 | pullbacki + shorty + większa płynność | +868,6% (lipiec), ograniczanie liczby transakcji |

**Wniosek:** system nie jest stały. Luk zmienia setupy wraz z warunkami rynku
(breakouty → pullbacki), ale **stałe pozostają**: risk-first, ciasny stop, selekcja
tematyczna, płynność i asymetria.

---

## 15. Tabela porównawcza setupów

| Setup | Kontekst | Trigger | Stop | Typowy R | Częstość |
|---|---|---|---|---|---|
| Pullback do wsparcia | uptrend + konsolidacja | reclaim AVWAP/EMA/gap | LoD / low świecy | 10–30R | wysoka (2025) |
| Prior day high | baza / konsolidacja | przebicie szczytu dnia | LoD | 5–15R | średnia |
| Inside day + gap | tight range | gap + przebicie | low inside day | 10–20R | średnia |
| ORB | EP / gap | high pierwszych min | low ORB | 5–15R | wysoka (EP) |
| EP | news / wyniki | ORB lub pullback | LoD / low świecy | 5–20R | średnia |
| Parabolic long | panika, 2–3 gap downy | intraday strength | low świecy | 5–15R | niska |
| Parabolic short | top formacji | lower high / EMA | high świecy | 5–15R | niska |
| Short pullback | słaby sektor | cofnięcie do EMA | high świecy | 3–10R | niska |

---

## 16. Model algorytmiczny

Poniższy pseudokod jest szkicem implementacji, nie kompletnym systemem.

### 16.1 Reżim rynkowy

```python
def market_regime(breadth, iwm_qqq, scan_counts, index_emas):
    score = 0
    if breadth.lead_count > breadth.lag_count: score += 1
    if iwm_qqq.relative_strength > 0: score += 1
    if scan_counts.potent > median(scan_counts.potent, 20): score += 1
    if index_emas.close > index_emas.ema50 and index_emas.ema50_rising: score += 1
    if score >= 3: return "GREEN"
    if score == 2: return "YELLOW"
    return "RED"
```

### 16.2 Selekcja

```python
def build_universe():
    premarket = scan_gap_up(min_gap=0.03, min_dollar_volume=200e6)
    potent = scan_top_gainers(period="1d", min_dollar_volume=200e6)
    leader = scan_top_gainers(period="30d", min_dollar_volume=200e6)

    theme_counts = count_by_industry(premarket + potent + leader)
    hot_themes = [t for t, n in theme_counts.items() if n >= 3]

    universe = []
    for s in premarket + potent + leader:
        if s.adr < 0.05: continue
        if s.dollar_volume < 200e6: continue
        if s.price < 5: continue
        if s.industry not in hot_themes: continue
        universe.append(s)
    return universe
```

### 16.3 Watchlisty

```python
def classify(stock):
    if stock.close > stock.ema50 and stock.ema50 > stock.ema150:
        return "LEAD"
    if stock.close < stock.ema50 and stock.ema50 < stock.ema150:
        return "LAG"
    return "MEDIOCRE"
```

### 16.4 Pullback

```python
def pullback_setup(stock):
    if stock.trend != "UP": return None
    if stock.return_3m < 0.30: return None
    if stock.consolidation_weeks < 8: return None
    if not higher_lows(stock): return None

    supports = []
    if near(stock.close, stock.avwap): supports.append("AVWAP")
    if near(stock.close, stock.ema9): supports.append("EMA9")
    if near(stock.close, stock.ema21): supports.append("EMA21")
    if near(stock.close, stock.horizontal_support): supports.append("HORIZ")
    if near(stock.close, stock.unfilled_gap): supports.append("GAP")

    if len(supports) < 2: return None

    # trigger intraday
    if not reclaim_after_flush(stock): return None

    stop = min(stock.low_of_day, stock.entry_candle_low)
    risk = (stock.entry - stop) / stock.entry
    if risk > 0.05: return None
    if risk > 0.5 * stock.adr: return None

    return Trade(stock, entry=stock.entry, stop=stop, risk_pct=0.005)
```

### 16.5 Sizing

```python
def size(equity, entry, stop, risk_pct=0.005, max_position=0.35):
    risk_dollar = equity * risk_pct
    per_share = entry - stop
    if per_share <= 0: return 0
    shares = risk_dollar / per_share
    max_shares = (equity * max_position) / entry
    return min(shares, max_shares)
```

### 16.6 Wyjścia

```python
def manage(position, bar):
    r = (bar.close - position.entry) / (position.entry - position.stop)

    if r >= 3 and not position.trimmed_3r:
        sell(position, 0.15); position.trimmed_3r = True
    if r >= 5 and not position.trimmed_5r:
        sell(position, 0.15); position.trimmed_5r = True

    if bar.close < ema(bar, 9):
        sell(position, "all")

    if position.regime == "RED" and r > 1:
        sell(position, 0.5)
```

---

## 17. Rozbieżności i decyzje przed backtestem

| # | Rozbieżność | Wartości | Rekomendacja |
|---|---|---|---|
| 1 | Wynik 2025 | 969,8% vs 1 358% | przyjąć 969,8% (źródła pierwotne) |
| 2 | Wynik 2024 | 283,1% (USIC) vs 340% (pełny rok) | rozdzielić: USIC vs własny P&L |
| 3 | Win rate | 22% / 23% / 25% | parametr do testu w zakresie 20–25% |
| 4 | Średni zysk | 15% | parametr |
| 5 | Średnia strata | 2,5% / 3% | parametr |
| 6 | Liczba transakcji | 423 (2024) / ~940–1 100 (2025) | zależy od okresu i aktywności |
| 7 | Stop | < 3% vs < 50% ADR vs max 5% | reguła: min(3%, 50% ADR), twardy limit 5% |
| 8 | Max pozycja | 25–30% vs 35% | 30% domyślnie, 35% tylko large cap |
| 9 | Watchlisty | EMA 9/21/50 vs 50/150 | wersja 50/150 jest nowsza; testować obie |
| 10 | Płynność | 100 mln vs 200 mln USD | 200 mln dla wersji 2026 |
| 11 | Horyzont | dni vs tygodnie | parametr: min. 5 dni, cel 5 tygodni |
| 12 | Margines | do 250% ekspozycji | modelować jako dźwignię 2,5× tylko w GREEN |

---

## 18. Ryzyka backtestu i wdrożenia

1. **Survivorship bias** — analizowane przykłady to zwycięzcy; trzeba testować także
   przegrane pullbacki.
2. **Look-ahead bias** — AVWAP i EMA muszą być liczone tylko z danych dostępnych
   w momencie decyzji.
3. **Poślizg i płynność** — ciasne stopy na małych spółkach są wrażliwe na spread.
   Luk sam ogranicza mikro capy.
4. **Gap risk** — stop nie chroni przed gapem; modelować scenariusze gap down.
5. **Zmienność reżimu** — system działa w trendzie, zawodzi w chopie (grudzień 2025).
6. **Overfitting** — nie kalibrować parametrów pod jeden rok (2025 był wyjątkowy).
7. **Dane intradays** — 1-min/5-min są potrzebne do wiernego odtworzenia wejść;
   bez nich trzeba uprościć model do dziennego.
8. **Transkrypcje automatyczne** — liczne błędy nazw i liczb; każdą regułę potwierdzać
   w co najmniej dwóch źródłach.

---

## 19. Checklist wdrożeniowy

- [ ] Zdefiniować uniwersum: ADR > 5%, ADV > 200 mln USD, cena > 5 USD.
- [ ] Zaimplementować trzy skanery i licznik tematów (≥ 3 spółki z branży).
- [ ] Zbudować watchlisty Lead/Mediocre/Lag (EMA 50/150).
- [ ] Zaimplementować detekcję konsolidacji ≥ 8 tygodni i wyższych dołków.
- [ ] Zaimplementować AVWAP (kotwice: swing high/low, gap, IPO).
- [ ] Zaimplementować konfluencję ≥ 2 wsparć.
- [ ] Zaimplementować trigger intraday (flush + reclaim / prior bar high / ORB).
- [ ] Zaimplementować stop: LoD lub low świecy; limit 5% i 50% ADR.
- [ ] Zaimplementować sizing 0,5% risk, max 30–35% pozycji.
- [ ] Zaimplementować wyjścia: 15% przy 3R, 15% przy 5R, trailing EMA 9/21/50.
- [ ] Dodać filtr reżimu (GREEN/YELLOW/RED) i ograniczać ekspozycję w RED.
- [ ] Dodać dziennik transakcji i metryki: win rate, avg win/loss, R, drawdown.
- [ ] Testować na danych 2021–2023 (bear/chop) i 2024–2025 (bull), osobno.
- [ ] Porównać wersję pullback vs breakout vs EP.

---

## 20. Mapa źródeł

### 20.1 Własny kanał `@martinlukkt` (94 transmisje)

Najważniejsze metodycznie:

| Data | Tytuł | Tematy |
|---|---|---|
| 2026-05-21 | Kristjan influence | wpływ Qullamaggie, stopy, selekcja, procenty |
| 2026-03-12 | Watchlist rules, AVWAP… | watchlisty, AVWAP, shorty, reżim |
| 2026-04-09 | Premarket routine | rutyna, skanery, wykonanie |
| 2026-04-14 | Selling into strength | wyjścia, częściowe sprzedaże |
| 2026-06-22 | Weekend scan | skan weekendowy, selekcja |
| 2026-01-08 | 26% Dec drawdown | overtrading, błędy, risk per trade |
| 2026-04-15 | Sit-out power | powstrzymywanie się od transakcji |
| 2026-07-22 | Study the charts | analiza wykresów |
| 2026-10-23 | A stream full of wisdoms | podsumowanie zasad |

### 20.2 Transkrypcje z innych kanałów (16)

| Kanał | Plik | Wkład |
|---|---|---|
| TraderLion | 2026-01-31 — 969% Return… Pullback Strategy | pełny wywiad o pullbackach |
| TraderLion | 2025-04-06 — 283% Gain… 22-Year-Old | wczesny wywiad, filozofia |
| TraderLion | 2026-02-04 — Give Me One More Gap Down | najlepszy trade 2025 (TQQQ) |
| TraderLion | 2026-02-07 — Mental Filter | psychologia |
| TraderLion | 2026-02-07 — Lessons That Actually Stick | lekcje |
| TraderLion | 2026-02-08 — Anchored VWAP Strategy | AVWAP |
| TraderLion | 2026-09-23 — $1,300 into a Trading Career | początek kariery |
| Financial Wisdom | 2026-02-12 — Winning Trading Strategy | pełny system, liczby |
| Financial Wisdom | 2026-05-29 — Pullback Strategy | pullbacki, przykłady |
| Zero to Alpha | 2026-05-16 — Full System Reveal | matematyka R, sizing |
| Making Millions | 2026-02-10 — Interview | pytania i odpowiedzi |
| Pozostałe | 5 plików (m.in. Shake Pryzby, 1 Minute Trader) | wzmianki kontekstowe |

### 20.3 Artykuły `docs/trading/MLuk/`

| Plik | Źródło |
|---|---|
| `forexclub-martin-luk-969-w-rok.md` | Forex Club |
| `substack-martin-luk-283-usic-2024.md` | Trading Resource Hub |
| `financialwisdom-martin-luk-pullback-strategy.md` | Financial Wisdom TV |

---

## Appendix A — słownik pojęć

| Pojęcie | Znaczenie |
|---|---|
| **ADR** | Average Daily Range — średni dzienny zakres |
| **AVWAP** | Anchored VWAP — VWAP kotwiczony na wybranym zdarzeniu |
| **EP** | Episodic Pivot — nagły ruch newsowy |
| **ORB** | Opening Range Breakout |
| **R** | mnożnik ryzyka; zysk / szerokość stopu |
| **LoD** | Low of Day — dołek dnia |
| **Potent scan** | skan wczorajszych najsilniejszych spółek |
| **Leader scan** | skan największych ruchów 30 dni |
| **Sit-out power** | umiejętność powstrzymania się od transakcji |
| **Mental capital** | kapitał psychiczny, odporność na straty |

---

*Dokument wygenerowany z korpusu `transkrypcje/martinlukkt/` oraz źródeł zewnętrznych
1 XI 2026. Wszystkie reguły wymagają weryfikacji na danych point-in-time. Materiał
edukacyjny, nie jest poradą inwestycyjną.*
