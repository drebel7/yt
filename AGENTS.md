# AGENTS.md

Wskazówki dla agentów AI pracujących w tym repozytorium.

## Czym jest ten projekt

Mały, jednoplikowy projekt PowerShell do pobierania filmów/playlist z YouTube
przez `yt-dlp.exe`. Celem jest zgodność ze starymi telewizorami (720p, H.264,
AAC, MP4), a nie maksymalna jakość. Nie ma tu testów, pakietu ani CI.

## Najważniejsze pliki

- `pobierz.ps1` — jedyny kod wykonywalny. Cała logika pobierania, wyboru formatu,
  archiwizacji i przenoszenia listy do `*-DONE.txt`.
- `README.md` — dokumentacja użytkownika (po polsku).
- `opencode.jsonc` — konfiguracja lokalna OpenCode; zawiera bezwzględne ścieżki
  Windows i nie powinna być „poprawiana” bez powodu.
- `yt-list*.txt`, `TODO*.txt`, `downloads/`, `yt-dlp.exe` — dane lokalne,
  ignorowane przez git.

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
- **Nie commituj `yt-dlp.exe`** ani innych binarek — `.gitignore` już je wyklucza.
- Zachowaj istniejące argumenty yt-dlp dotyczące kompatybilności
  (`-S +res:720,vcodec:h264,acodec:aac`, `--merge-output-format mp4`,
  `--remux-video mp4`, `--windows-filenames`). Zmiana ich zmienia format wyjściowy.
- Nazewnictwo wyjścia jest częścią umowy: playlisty → osobny katalog +
  `%(playlist_index)03d - %(title)s.%(ext)s`; pojedyncze filmy → `%(title)s.%(ext)s`.
- Archiwa playlist trzymaj w `downloads\.archives\<playlist_id>.txt`.

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

## Typowe zadania

- **Nowa lista do pobrania:** użytkownik tworzy `yt-listN.txt`; uruchomienie to
  `.\pobierz.ps1 yt-listN.txt`. Nie trzeba zmieniać kodu.
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
