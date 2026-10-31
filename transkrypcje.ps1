#requires -Version 5.1
<#
    transkrypcje.ps1 [plik-z-lista-URL] [opcje]

    Pobiera transkrypcje (napisy) z YouTube za pomoca yt-dlp.exe.

    Obsluguje pojedyncze filmy, playlisty i kanaly (URL kanalu -> wszystkie
    filmy z listy uploads). Dla kazdego filmu:

      1. yt-dlp pobiera napisy (recznie lub automatyczne) w formacie VTT
         oraz metadane (info.json) do katalogu tymczasowego,
      2. skrypt czysci VTT (usuwa znaczniki czasu, tagi, duplikaty),
      3. zapisuje transkrypcje jako TXT w katalogu kanalu:
             <OutDir>\<kanal>\RRRR-MM-DD - <tytul>.txt
         z naglowkiem Title/URL/Published/Language;
      4. pliki tymczasowe sa usuwane.

    Nazwy katalogow i plikow sa normalizowane do czystego ASCII (nazwy.ps1):
    polskie znaki transliterowane, emoji usuniete. Dzieki temu transkrypcje
    otwieraja sie poprawnie takze na starych odtwarzaczach i telewizorach.

    Domyslna lista URL: transkrypcje-list.txt (ten sam format co yt-list.txt -
    jeden URL na linie, '#' rozpoczyna komentarz).

    Wznowienie: skrypt prowadzi wlasne archiwum ID w
    <OutDir>\.archives\subtitles.txt (odtwarzane z naglowkow istniejacych TXT),
    a istniejace pliki nie sa nadpisywane. Dzieki temu kolejne uruchomienia
    pomijaja juz pobrane filmy, takze te przeniesione z innego projektu.

    Przyklady:
        .\transkrypcje.ps1
        .\transkrypcje.ps1 transkrypcje-list2.txt
        .\transkrypcje.ps1 lista.txt -Lang pl -OutDir transkrypcje
        .\transkrypcje.ps1 lista.txt -Limit 10 -Sleep 5

    Uwaga: YouTube potrafi ograniczac liczbe zapytan (429). Skrypt domyslnie
    usypia 3 s miedzy zapytaniami (-Sleep).
#>

param(
    [string]$ListFile = 'transkrypcje-list.txt',
    [string]$Lang = 'en',
    [string]$OutDir = 'transkrypcje',
    [int]$Limit = 0,
    [double]$Sleep = 3
)

$ErrorActionPreference = 'Stop'

$root  = Split-Path -Parent $MyInvocation.MyCommand.Path
$nazwyFn = Join-Path $root 'nazwy.ps1'
if (-not (Test-Path -LiteralPath $nazwyFn)) { throw "Nie znaleziono: $nazwyFn" }
. $nazwyFn

# Cross-platform: Windows -> yt-dlp.exe, Linux/macOS -> yt-dlp
if ($IsWindows) {
    $ytdlpLocal = Join-Path $root 'yt-dlp.exe'
} else {
    $ytdlpLocal = Join-Path $root 'yt-dlp'
}

if ([System.IO.Path]::IsPathRooted($ListFile)) {
    $listFile = $ListFile
} else {
    $listFile = Join-Path $root $ListFile
}
if ([System.IO.Path]::IsPathRooted($OutDir)) {
    $outRoot = $OutDir
} else {
    $outRoot = Join-Path $root $OutDir
}

$stage   = Join-Path $outRoot '.staging'
$archDir = Join-Path $outRoot '.archives'
$archive = Join-Path $archDir 'subtitles.txt'
$utf8    = New-Object System.Text.UTF8Encoding($false)

if (-not (Test-Path -LiteralPath $ytdlpLocal)) {
    $ytdlpCmd = Get-Command 'yt-dlp' -CommandType Application -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($ytdlpCmd) { $ytdlp = $ytdlpCmd.Source }
    else { throw "Nie znaleziono yt-dlp (lokalnie ani w PATH)" }
} else {
    $ytdlp = $ytdlpLocal
}
if (-not (Test-Path -LiteralPath $listFile)) { throw "Nie znaleziono: $listFile" }

New-Item -ItemType Directory -Force -Path $stage, $archDir | Out-Null

$script:ok = 0
$script:nosubs = 0
$script:existing = 0

$script:archived = New-Object 'System.Collections.Generic.HashSet[string]'

function Add-ArchiveId {
    param([string]$Id)
    if (-not $Id) { return }
    if (-not $script:archived.Contains($Id)) {
        Add-Content -LiteralPath $archive -Value $Id -Encoding ASCII
        [void]$script:archived.Add($Id)
    }
}

# yt-dlp nie sprawdza archiwum przy --skip-download, wiec prowadzimy je sami.
# Archiwum jest odtwarzane od zera na podstawie naglowkow istniejacych plikow TXT
# (dzieki temu przeniesione transkrypcje nie sa pobierane ponownie, a usuniety
# plik zostanie pobrany przy kolejnym uruchomieniu).
function Import-ExistingTranscripts {
    $script:archived.Clear()
    Set-Content -LiteralPath $archive -Value $null -Encoding ASCII

    $files = Get-ChildItem -LiteralPath $outRoot -Recurse -Filter '*.txt' -File -ErrorAction SilentlyContinue |
        Where-Object { $_.FullName -notlike '*\.staging\*' -and $_.FullName -notlike '*\.archives\*' }
    foreach ($file in $files) {
        $head = Get-Content -LiteralPath $file.FullName -TotalCount 4 -Encoding UTF8
        foreach ($line in $head) {
            if ($line -match 'v=([A-Za-z0-9_-]{11})') {
                Add-ArchiveId $matches[1]
                break
            }
        }
    }
    Write-Host "  zaindeksowano $($script:archived.Count) transkrypcji" -ForegroundColor DarkGray
}

function ConvertFrom-Vtt {
    param([string]$Path)
    $lines = Get-Content -LiteralPath $Path -Encoding UTF8
    $out = New-Object System.Collections.Generic.List[string]

    foreach ($raw in $lines) {
        $line = $raw.Trim()
        if (-not $line) { continue }
        if ($line.StartsWith('WEBVTT') -or $line.StartsWith('Kind:') -or
            $line.StartsWith('Language:') -or $line.StartsWith('NOTE') -or
            $line.StartsWith('STYLE') -or $line.StartsWith('REGION')) { continue }
        if ($line.Contains('-->')) { continue }
        if ($line -match '^\d{2}:\d{2}:\d{2}\.\d{3}\s*-->') { continue }
        if ($line -match '^\d+$') { continue }

        $line = [regex]::Replace($line, '<[^>]+>', '')
        $line = $line.Replace('&nbsp;', ' ').Replace('&amp;', '&')
        $line = $line.Replace('&lt;', '<').Replace('&gt;', '>').Trim()

        if (-not $line) { continue }
        if ($out.Count -gt 0 -and $out[$out.Count - 1] -eq $line) { continue }
        $out.Add($line)
    }

    return ([regex]::Replace(($out -join ' '), '\s+', ' ')).Trim()
}

function Convert-Staged {
    $infos = @(Get-ChildItem -LiteralPath $stage -Filter '*.info.json' -File -ErrorAction SilentlyContinue)
    foreach ($infoFile in $infos) {
        try {
            $info = Get-Content -LiteralPath $infoFile.FullName -Raw -Encoding UTF8 | ConvertFrom-Json
        }
        catch {
            Remove-Item -LiteralPath $infoFile.FullName -Force -ErrorAction SilentlyContinue
            continue
        }

        $id = [string]$info.id
        if (-not $id) {
            Remove-Item -LiteralPath $infoFile.FullName -Force -ErrorAction SilentlyContinue
            continue
        }

        $vtts = @(Get-ChildItem -LiteralPath $stage -Filter "$id.*.vtt" -File -ErrorAction SilentlyContinue)
        if (-not $vtts) {
            $script:nosubs++
            Write-Host "  NOSUBS $id" -ForegroundColor DarkYellow
            Get-ChildItem -LiteralPath $stage -Filter "$id.*" -File -ErrorAction SilentlyContinue |
                Remove-Item -Force -ErrorAction SilentlyContinue
            continue
        }

        $text = ConvertFrom-Vtt $vtts[0].FullName
        if (-not $text) {
            $script:nosubs++
            Write-Host "  NOSUBS $id (puste napisy)" -ForegroundColor DarkYellow
            Get-ChildItem -LiteralPath $stage -Filter "$id.*" -File -ErrorAction SilentlyContinue |
                Remove-Item -Force -ErrorAction SilentlyContinue
            continue
        }

        # Jezyk wybieramy z faktycznie pobranego pliku VTT (moze byc inny niz
        # lista -Lang, np. przy wielu wariantach jezykowych).
        $language = $Lang
        if ($vtts[0].Name -match ('^' + [regex]::Escape($id) + '\.(.+)\.vtt$')) {
            $language = $matches[1]
        }
        if (-not $language) { $language = $Lang }

        $title = [string]$info.title
        if (-not $title) { $title = $id }

        $channel = [string]$info.channel
        if (-not $channel) { $channel = [string]$info.uploader }
        if (-not $channel) { $channel = 'unknown' }

        $date = [string]$info.upload_date
        if ($date -match '^(\d{4})(\d{2})(\d{2})$') {
            $date = '{0}-{1}-{2}' -f $matches[1], $matches[2], $matches[3]
        }
        elseif ($date.Length -ge 10) {
            $date = $date.Substring(0, 10)
        }
        else {
            $date = '0000-00-00'
        }

        $url = [string]$info.webpage_url
        if (-not $url) { $url = "https://www.youtube.com/watch?v=$id" }

        $channelDir = Join-Path $outRoot (ConvertTo-SafeFileName -Name $channel -MaxLength 60)
        New-Item -ItemType Directory -Force -Path $channelDir | Out-Null

        $base   = "$date - $(ConvertTo-SafeFileName -Name $title -MaxLength 110)"
        $target = Join-Path $channelDir "$base.txt"

        if (Test-Path -LiteralPath $target) {
            $head = Get-Content -LiteralPath $target -TotalCount 4 -Encoding UTF8
            $headText = $head -join "`n"
            if ($headText -match [regex]::Escape("v=$id")) {
                $script:existing++
                Add-ArchiveId $id
                Get-ChildItem -LiteralPath $stage -Filter "$id.*" -File -ErrorAction SilentlyContinue |
                    Remove-Item -Force -ErrorAction SilentlyContinue
                continue
            }

            if ($headText -notmatch 'youtube\.com|youtu\.be') {
                # Stary plik z vtt_to_txt.py (naglowek "Source:", bez URL).
                # Ten sam dzien i tytul => ta sama transkrypcja; normalizujemy naglowek.
                $raw = [System.IO.File]::ReadAllText($target)
                $sep = [regex]::Match($raw, '(?m)^-{60}\s*$')
                if ($sep.Success) {
                    $body = $raw.Substring($sep.Index + $sep.Length) -replace '^[\r\n]+', ''
                }
                else {
                    $body = $raw
                }
                $content = "Title: $title`nURL: $url`nPublished: $date`nLanguage: $language`n" + ('-' * 60) + "`n`n" + $body
                [System.IO.File]::WriteAllText($target, $content, $utf8)
                $script:existing++
                Add-ArchiveId $id
                Write-Host "  UPD $id  $base (uzupelniono naglowek)" -ForegroundColor DarkCyan
                Get-ChildItem -LiteralPath $stage -Filter "$id.*" -File -ErrorAction SilentlyContinue |
                    Remove-Item -Force -ErrorAction SilentlyContinue
                continue
            }

            $target = Join-Path $channelDir "$base [$id].txt"
        }

        $content = "Title: $title`nURL: $url`nPublished: $date`nLanguage: $language`n" + ('-' * 60) + "`n`n" + $text
        [System.IO.File]::WriteAllText($target, $content, $utf8)
        Add-ArchiveId $id
        $script:ok++
        Write-Host "  OK $id  $base" -ForegroundColor Green

        Get-ChildItem -LiteralPath $stage -Filter "$id.*" -File -ErrorAction SilentlyContinue |
            Remove-Item -Force -ErrorAction SilentlyContinue
    }
}

$urls = Get-Content -LiteralPath $listFile |
    ForEach-Object { $_.Trim() } |
    Where-Object { $_ -ne '' -and -not $_.StartsWith('#') }

if (-not $urls) { throw "Brak adresow w $listFile" }

Write-Host "Indeksowanie istniejacych transkrypcji..." -ForegroundColor DarkGray
Import-ExistingTranscripts
Write-Host "Konwersja plikow pozostawionych w staging..." -ForegroundColor DarkGray
Convert-Staged

foreach ($url in $urls) {
    Write-Host ""
    Write-Host "=== $url ===" -ForegroundColor Cyan

    # Najpierw sama lista ID (szybko, bez pobierania metadanych kazdego filmu).
    $flatArgs = @(
        '--no-warnings'
        '--ignore-errors'
        '--flat-playlist'
        '--print', '%(id)s'
        $url
    )
    $ids = @(& $ytdlp @flatArgs 2>$null |
        ForEach-Object { $_.Trim() } |
        Where-Object { $_ -match '^[A-Za-z0-9_-]{11}$' } |
        Select-Object -Unique)

    if ($ids.Count -eq 0) {
        Write-Host "Nie udalo sie odczytac listy filmow z tego adresu." -ForegroundColor Yellow
        continue
    }

    $todo = @($ids | Where-Object { -not $script:archived.Contains($_) })
    if ($Limit -gt 0 -and $todo.Count -gt $Limit) {
        $todo = @($todo[0..($Limit - 1)])
    }

    Write-Host ("Filmow: {0}, do pobrania: {1}" -f $ids.Count, $todo.Count) -ForegroundColor DarkGray
    if ($todo.Count -eq 0) { continue }

    # yt-dlp dostaje pojedyncze URL-e partiami (limit dlugosci linii polecen).
    for ($i = 0; $i -lt $todo.Count; $i += 50) {
        $end = [math]::Min($i + 49, $todo.Count - 1)
        $batchUrls = @($todo[$i..$end] | ForEach-Object { "https://www.youtube.com/watch?v=$_" })

        $ytArgs = @(
            '--no-warnings'
            '--ignore-errors'
            '--newline'
            '--skip-download'
            '--write-subs'
            '--write-auto-subs'
            '--sub-langs', $Lang
            '--sub-format', 'vtt/best'
            '--write-info-json'
            '--sleep-requests', [string]$Sleep
            '--retries', '10'
            '--fragment-retries', '10'
            '-o', (Join-Path $stage '%(id)s.%(ext)s')
        ) + $batchUrls

        & $ytdlp @ytArgs
        $code = $LASTEXITCODE
        if ($code -ne 0) {
            Write-Host "yt-dlp zwrocil kod $code (niektore pozycje moga byc niedostepne)" -ForegroundColor Yellow
        }

        Convert-Staged
    }
}

# Sprzatanie pustych katalogow pozostawionych po nieudanych probach.
Get-ChildItem -LiteralPath $stage -Force -ErrorAction SilentlyContinue |
    Where-Object { $_.PSIsContainer } |
    Remove-Item -Recurse -Force -ErrorAction SilentlyContinue

Write-Host ""
Write-Host "Gotowe. nowe=$($script:ok), istniejace=$($script:existing), bez napisow=$($script:nosubs) | katalog: $outRoot" -ForegroundColor Green
