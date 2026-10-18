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
```

Pliki trafią do `downloads\`. Po zakończeniu zawartość listy jest dopisywana do
pliku `*-DONE.txt`, a oryginalna lista jest usuwana (żeby nie pobierać jej ponownie).

## Jak działa `pobierz.ps1`

- **Format obrazu:** preferencja `720p` → `1080p` → maksimum dostępne
  (`-S +res:720,vcodec:h264,acodec:aac`).
- **Kodek:** H.264 + AAC stereo, kontener MP4 (`--merge-output-format mp4`,
  `--remux-video mp4`). Bez H.265/AV1/VP9, bo stare TV ich nie odtwarzają.
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
├─ pobierz.ps1          # główny skrypt pobierający
├─ yt-dlp.exe           # binarka yt-dlp (ignorowana przez git)
├─ yt-list.txt          # domyślna kolejka URL-i (ignorowana przez git)
├─ yt-list2-DONE.txt    # historia już przetworzonej listy (ignorowana przez git)
├─ TODO.txt, TODO2.txt # notatki/zlecenia lokalne (ignorowane przez git)
├─ opencode.jsonc       # konfiguracja OpenCode (model, serwer MCP YouTube)
├─ AGENTS.md            # wskazówki dla agentów AI pracujących w repo
├─ README.md
└─ downloads/           # pobrane media, ~65 GB (ignorowane przez git)
   ├─ .archives/        # archiwa yt-dlp (lista pobranych pozycji playlist)
   └─ <playlista>/      # katalogi playlist
```

## Format listy URL

```text
# Modern Talking - Brother Louie
https://www.youtube.com/watch?v=K5DALXwOe0s

# playlista
https://www.youtube.com/watch?v=...&list=PL...
```

Puste linie i linie zaczynające się od `#` są pomijane.

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
