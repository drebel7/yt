# AGENTS.md

Wskazówki dla agentów AI pracujących w tym repozytorium.

## Czym jest ten projekt

Mały, jednoplikowy projekt PowerShell do pobierania filmów/playlist z YouTube
przez `yt-dlp.exe`. Celem jest zgodność ze starymi telewizorami (720p, H.264,
AAC, MP4), a nie maksymalna jakość. Nie ma tu testów, pakietu ani CI.

## Najważniejsze pliki

- `pobierz.ps1` — jedyny kod wykonywalny pobierania filmów: wybór formatu,
  archiwizacja i przenoszenie listy do `*-DONE.txt`.
- `transkrypcje.ps1` — pobieranie transkrypcji (napisy → TXT) dla filmów,
  playlist i kanałów; czyści VTT, indeksuje istniejące pliki, wznawia pobieranie.
- `README.md` — dokumentacja użytkownika (po polsku).
- `opencode.jsonc` — konfiguracja lokalna OpenCode; zawiera bezwzględne ścieżki
  Windows i nie powinna być „poprawiana” bez powodu.
- `transkrypcje/` — transkrypcje TXT (wersjonowane), m.in. 443 pliki kanału
  Qullamaggie. `transkrypcje/.staging` i `.archives` to pliki robocze.
- `docs/Qullamaggie-strategia.md` — synteza strategii (EP, ORB, selekcja, wyjścia)
  na podstawie transkrypcji; źródło do implementacji algorytmów.
- `yt-list*.txt`, `transkrypcje-list*.txt`, `TODO*.txt`, `downloads/`,
  `yt-dlp.exe`, `Youtube_transcripts/` — dane lokalne, ignorowane przez git.

## Zasady edycji

- **Zgodność z PowerShell 5.1.** Nie używaj składni PS7+ (np. `??`, `&&`,
  operatorów trójargumentowych). Testuj mentalnie pod 5.1.
- **Kod i komunikaty w `pobierz.ps1` są celowo bez polskich znaków diakrytycznych**
  (ASCII). Zachowaj ten styl w nowych stringach i komentarzach skryptu —
  unika problemów z kodowaniem konsoli. Dokumentację (`.md`) pisz normalną polszczyzną.
- **Ścieżki zawsze względem skryptu**, nie względem bieżącego katalogu:
  `Split-Path -Parent $MyInvocation.MyCommand.Path`. Nie zmieniaj tego wzorca.
- **Nie usuwaj ani nie commituj `downloads/`.** To ~65 GB mediów użytkownika.
  Nigdy nie uruchamiaj poleceń kasujących ten katalog.
- **Nie usuwaj plików z `transkrypcje/<kanał>/`.** To dorobek użytkownika
  (443 pliki Qullamaggie). Zmiana nazwy pliku psuje indeks, ale jest odtwarzana
  z nagłówka `URL:`; jeśli musisz zmienić format, zachowaj linię z URL-em.
- **Nie commituj `Youtube_transcripts/`** — to kopia starego projektu z `.venv`
  (~260 MB). Jest ignorowana; źródłem funkcji transkrypcji jest `transkrypcje.ps1`.
- **`transkrypcje.ps1` nie może zależeć od Pythona.** Ma używać wyłącznie
  `yt-dlp.exe` (i opcjonalnie node/ffmpeg, jeśli yt-dlp tego wymaga).
- **Nie commituj `yt-dlp.exe`** ani innych binarek — `.gitignore` już je wyklucza.
- Zachowaj istniejące argumenty yt-dlp dotyczące kompatybilności
  (`-S +res:720,vcodec:h264,acodec:aac`, `--merge-output-format mp4`,
  `--remux-video mp4`, `--windows-filenames`). Zmiana ich zmienia format wyjściowy.
- Nazewnictwo wyjścia jest częścią umowy: playlisty → osobny katalog +
  `%(playlist_index)03d - %(title)s.%(ext)s`; pojedyncze filmy → `%(title)s.%(ext)s`.
- Archiwa playlist trzymaj w `downloads\.archives\<playlist_id>.txt`.
- **Transkrypcje:** wynik to `transkrypcje\<kanał>\RRRR-MM-DD - <tytuł>.txt`
  z nagłówkiem `Title:` / `URL:` / `Published:` i separatorem 60 myślników.
  Indeks `transkrypcje\.archives\subtitles.txt` jest odtwarzany z nagłówków
  `URL:` przy każdym uruchomieniu — nie usuwaj tej linii z plików.
  Pliki VTT/JSON w `.staging` są tymczasowe i zawsze sprzątane po konwersji.

## Testowanie zmian

- Nie ma testów automatycznych. Weryfikacja = uruchomienie skryptu na krótkiej,
  tymczasowej liście (1–2 krótkie filmy) i sprawdzenie:
  - czy powstał plik MP4 w `downloads/`,
  - czy kodek to h264/aac (`ffprobe`),
  - czy lista została przeniesiona do `*-DONE.txt`.
- Pełne pobieranie playlist jest kosztowne (godziny, dziesiątki GB) — nie uruchamiaj
  go bez wyraźnej zgody użytkownika.
- Nie modyfikuj plików `yt-list*.txt` użytkownika (poza celowym dodaniem testowego
  URL-a na kopii).
- **Transkrypcje testuj na kopii:** `.\transkrypcje.ps1 test.txt -OutDir _test-tx -Limit 1`
  (krótki film z napisami), sprawdź plik TXT, nagłówek i brak plików w `.staging`.
  Następnie usuń `_test-tx`. Nie uruchamiaj pełnego kanału bez potrzeby —
  588 filmów z domyślnym `-Sleep 3` trwa długo.
- Pusty przebieg na istniejącym kanale powinien wypisać `do pobrania: 0`
  (dowód, że indeks działa).

## Typowe zadania

- **Nowa lista do pobrania:** użytkownik tworzy `yt-listN.txt`; uruchomienie to
  `.\pobierz.ps1 yt-listN.txt`. Nie trzeba zmieniać kodu.
- **Nowe transkrypcje:** dopisz URL-e do `transkrypcje-list.txt` i uruchom
  `.\transkrypcje.ps1`; dla innej listy podaj ścieżkę jako pierwszy argument.
- **Zmiana języka napisów:** `-Lang pl` (lub `pl,en`).
- **Zmiana preferencji jakości:** edytuj `$sortArgs` w `pobierz.ps1` i zaktualizuj
  README.
- **Włączenie fallbacku HLS dla playlist:** `$HlsFallbackForPlaylists = $true`.
- **Problemy z pobieraniem:** najpierw zaktualizuj `yt-dlp.exe`; sprawdź, czy
  `ffmpeg` i `node` są w `PATH`.

## Konwencje git

- Commituj tylko źródła i dokumentację (`pobierz.ps1`, `*.md`, `opencode.jsonc`).
- Wiadomości commitów po angielsku lub polsku, krótko, w trybie rozkazującym.
- Przed commitem sprawdź `git status` — upewnij się, że nie ma w nim mediów ani
  plików tymczasowych.
