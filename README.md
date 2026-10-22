# yt

Zestaw narzędzi do pobierania filmów i playlist z YouTube na dysk lokalny.
Głównym celem jest **maksymalna zgodność odtwarzania** ze starszymi telewizorami
(720p, H.264 + AAC w kontenerze MP4), a nie najwyższa możliwa jakość.

Repozytorium powstało jako ręczna kopia z innego projektu, dlatego zawiera tylko
skrypt, konfigurację i listy adresów — cała pobrana zawartość (`downloads/`)
pozostaje lokalna i jest ignorowana przez git.

## Wymagania

| Element | Wersja / uwagi |
| --- | --- |
| Windows | PowerShell 5.1 (`#requires -Version 5.1`) lub nowszy |
| [yt-dlp](https://github.com/yt-dlp/yt-dlp) | `yt-dlp.exe` w katalogu głównym repo |
| [ffmpeg](https://ffmpeg.org/) | wymagany do scalania strumieni video+audio; musi być w `PATH` |
| Node.js | wymagany przez yt-dlp do rozwiązywania wyzwań JS (`--js-runtimes node`) |

## Szybki start

1. Wrzuć `yt-dlp.exe` do katalogu głównego projektu.
2. Uzupełnij `yt-list.txt` adresami (jeden URL na linię, `#` rozpoczyna komentarz).
3. Uruchom:

```powershell
.\pobierz.ps1
# lub z własną listą:
.\pobierz.ps1 yt-list2.txt
# z limitem 10 GB przyrostu:
.\pobierz.ps1 yt-list2.txt -MaxTotalGB 10
```

Pliki trafią do `downloads\`. Po zakończeniu zawartość listy jest dopisywana do
pliku `*-DONE.txt`, a oryginalna lista jest usuwana (żeby nie pobierać jej ponownie).

## Jak działa `pobierz.ps1`

- **Format obrazu:** preferencja `720p` → maksimum dostępne w H.264
  (`-S +res:720,vcodec:h264,acodec:aac`).
- **Kodek:** H.264 + AAC stereo, kontener MP4 (`--merge-output-format mp4`,
  `--remux-video mp4`). Format jest **wymuszany filtrem** `vcodec^=avc1` /
  `acodec^=mp4a`, więc nie trafi się VP9/AV1 ani Opus — nawet jeśli YouTube
  oferuje wyższą rozdzielczość tylko w nowszym kodeku. Dla starych TV ważniejsza
  jest zgodność niż rozdzielczość.
- **Limit rozmiaru:** opcjonalny `-MaxTotalGB N` mierzy przyrost względem stanu
  sprzed uruchomienia i przerywa przed kolejnym plikiem po osiągnięciu limitu.
  Nieprzetworzone URL-e zostają w pliku listy (nie trafiają do `-DONE`).
- **Playlisty:** każda playlista ląduje w osobnym katalogu, pliki mają numer
  trzycyfrowy z przodu: `downloads\<tytuł playlisty>\001 - <tytuł>.mp4`.
- **Pojedyncze filmy:** `downloads\<tytuł>.mp4`.
- **Duplikaty:** playlista korzysta z `--download-archive` w
  `downloads\.archives\<ID_playlisty>.txt`, więc ponowne uruchomienie pomija
  już pobrane pozycje.
- **Dławienie przez YouTube:** gdy pierwsza próba dla pojedynczego filmu
  się nie uda, skrypt ponawia pobieranie w wariancie HLS (m3u8), który zwykle
  omija throttling. Dla playlist drugi przebieg jest wyłączony
  (zmienna `$HlsFallbackForPlaylists` na górze skryptu).
- **Odporność:** `--continue`, 20 prób, 20 prób fragmentów, timeout gniazda 60 s.
- **Porządki:** usuwa osierocone pliki `.part`, gdy finalny `.mp4` już istnieje,
  i wypisuje podsumowanie (sukces/błędy, liczba MP4, rozmiar w GB).

## Struktura projektu

```
yt/
├─ pobierz.ps1          # główny skrypt pobierający filmy
├─ transkrypcje.ps1     # pobieranie transkrypcji (napisy -> TXT)
├─ yt-dlp.exe           # binarka yt-dlp (ignorowana przez git)
├─ yt-list.txt          # domyślna kolejka URL-i filmów (ignorowana przez git)
├─ transkrypcje-list.txt # kolejka URL-i do transkrypcji (ignorowana przez git)
├─ yt-list2-DONE.txt    # historia już przetworzonej listy (ignorowana przez git)
├─ TODO.txt, TODO2.txt # notatki/zlecenia lokalne (ignorowane przez git)
├─ opencode.jsonc       # konfiguracja OpenCode (model, serwer MCP YouTube)
├─ AGENTS.md            # wskazówki dla agentów AI pracujących w repo
├─ README.md
├─ docs/
│  └─ Qullamaggie-strategia.md  # synteza strategii z transkrypcji
├─ downloads/           # pobrane media, ~65 GB (ignorowane przez git)
│  ├─ .archives/        # archiwa yt-dlp (lista pobranych pozycji playlist)
│  └─ <playlista>/      # katalogi playlist
└─ transkrypcje/        # transkrypcje TXT (lokalne, ignorowane przez git)
   ├─ .archives/        # indeks ID pobranych transkrypcji (ignorowany)
   ├─ .staging/         # pliki tymczasowe VTT/JSON (ignorowany)
   └─ Qullamaggie/      # 443 transkrypcje kanału (~12 MB)
```

## Format listy URL

```text
# Modern Talking - Brother Louie
https://www.youtube.com/watch?v=K5DALXwOe0s

# playlista
https://www.youtube.com/watch?v=...&list=PL...
```

Puste linie i linie zaczynające się od `#` są pomijane.

## Transkrypcje

Drugi skrypt, `transkrypcje.ps1`, pobiera napisy (ręczne lub automatyczne)
i zapisuje je jako czysty tekst. Nie wymaga Pythona ani klucza API — korzysta
z tego samego `yt-dlp.exe`.

Syntetyczne opracowanie strategii Qullamaggie na podstawie wszystkich 443
transkrypcji (2017–2023) znajduje się w
[`docs/Qullamaggie-strategia.md`](docs/Qullamaggie-strategia.md).

```powershell
.\transkrypcje.ps1                                   # domyślnie transkrypcje-list.txt
.\transkrypcje.ps1 transkrypcje-list2.txt
.\transkrypcje.ps1 lista.txt -Lang pl -OutDir transkrypcje
.\transkrypcje.ps1 lista.txt -Limit 10 -Sleep 5      # test / ograniczenie
```

Lista URL ma ten sam format co `yt-list.txt` (jedna linia = jeden URL,
`#` to komentarz). Obsługiwane są pojedyncze filmy, playlisty i kanały
(URL kanału pobiera wszystkie filmy z zakładki uploads).

### Jak to działa

1. `yt-dlp --flat-playlist --print` zbiera same ID filmów (tanio, bez metadanych).
2. ID już obecne w indeksie są pomijane.
3. Dla pozostałych `yt-dlp` pobiera napisy `--sub-langs` (domyślnie `en`)
   oraz `info.json` do `transkrypcje/.staging/`.
4. Skrypt czyści VTT (znaczniki czasu, tagi, duplikaty linii), skleja tekst
   i zapisuje plik z nagłówkiem `Title` / `URL` / `Published`.
5. Pliki tymczasowe są usuwane.

Wynik:

```text
transkrypcje\<kanał>\RRRR-MM-DD - <tytuł>.txt
```

Zawartość pliku:

```text
Title: Market mechanics, setups and more
URL: https://www.youtube.com/watch?v=...
Published: 2023-06-09
------------------------------------------------------------

<tekst transkrypcji w jednej linii>
```

### Wznawianie i duplikaty

- Indeks `transkrypcje/.archives/subtitles.txt` jest **odtwarzany przy każdym
  uruchomieniu** z nagłówków istniejących plików TXT. Usunięcie pliku powoduje,
  że zostanie pobrany ponownie; przeniesione transkrypcje nie są dublowane.
- Jeśli plik o tej samej dacie i tytule już istnieje, ale nie ma w nagłówku URL
  (stary format `vtt_to_txt.py`), skrypt uzupełnia nagłówek zamiast tworzyć kopię.
- Przy kolizji różnych filmów o tym samym dniu i tytule dodawany jest sufiks
  ` [video_id]`.
- Filmy bez napisów są raportowane jako `NOSUBS` i nie trafiają do indeksu,
  więc można je ponowić później.

### Przeniesione transkrypcje

Katalog `transkrypcje/Qullamaggie/` zawiera 443 transkrypcje (ok. 12 MB)
przeniesione ze starego projektu `Youtube_transcripts` (kanał Qullamaggie,
lata 2017–2023). Pliki są w formacie opisanym wyżej. Cały katalog
`transkrypcje/` jest trzymany wyłącznie lokalnie i ignorowany przez git
(pełne transkrypcje mogą podlegać prawom autorskim).

## Silnik MCP YouTube (opcjonalnie)

W sąsiednim katalogu `Youtube_transcripts/youtube-mcp/` znajduje się serwer
[MCP](https://modelcontextprotocol.io/) (`youtube_server.py`) udostępniający
agentom AI dwa narzędzia:

- `search_youtube_videos` — wyszukiwanie filmów przez YouTube Data API v3
  (wymaga `YOUTUBE_API_KEY`),
- `get_youtube_transcript` — pobranie transkrypcji pojedynczego filmu
  (biblioteka `youtube-transcript-api`).

Konfiguracja w `opencode.jsonc` wskazuje na interpreter z jego środowiska
`.venv`. To narzędzie działa „ad hoc” w rozmowie z agentem; masowe pobieranie
transkrypcji realizuje `transkrypcje.ps1`. Sam katalog `youtube-mcp` nie jest
częścią tego repozytorium i nie jest potrzebny do działania obu skryptów.

Katalog `youtube-mcp` zajmuje ok. 250 MB, bo prawie całą objętość stanowi
`.venv` (zależności: FastMCP, google-api-python-client, youtube-transcript-api
oraz `yt-dlp`). Największy element to `googleapiclient/discovery_cache/documents`
(~90 MB statycznych schematów API Google). To **nie jest** pełna dystrybucja
Pythona: venv zawiera tylko `site-packages` i małe `python.exe`/`pythonw.exe`,
a korzysta z bazowej instalacji Python 3.12 wskazanej w `pyvenv.cfg`
(`C:\Users\daniel\AppData\Local\Programs\Python\Python312`). Przeniesienie
katalogu na inną maszynę wymaga odtworzenia venv lub zainstalowania Pythona
w tej samej lokalizacji.

## Konfiguracja OpenCode

`opencode.jsonc` definiuje lokalny model (LM Studio) oraz serwer MCP `youtube`
(ścieżki bezwzględne wskazują na sąsiednie repozytorium i installation lokalną).
Plik jest specyficzny dla tej maszyny — przy przenoszeniu projektu trzeba
poprawić ścieżki. Klucz API jest brany ze zmiennej środowiskowej `YOUTUBE_API_KEY`.

## Uwagi

- Pobieraj tylko treści, do których masz prawa lub które są legalnie dostępne.
- Katalog `downloads/` potrafi mieć dziesiątki GB — nie trafia do repozytorium.
- `yt-dlp` jest często aktualizowany; przy błędach pobierania najpierw
  zaktualizuj `yt-dlp.exe`.
