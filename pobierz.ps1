#requires -Version 5.1
<#
    pobierz.ps1 [plik-z-lista-URL] [-MaxTotalGB N]

    Pobiera filmy/playlisty z pliku z lista URL za pomoca yt-dlp.exe.
    Domyslny plik listy: yt-list.txt. Mozna podac inny, np.:
        .\pobierz.ps1 yt-list2.txt
        .\pobierz.ps1 yt-list2.txt -MaxTotalGB 10

    -MaxTotalGB N (opcjonalnie) ogranicza przyrost rozmiaru katalogu downloads
    w danym uruchomieniu. Po osiagnieciu limitu skrypt przerywa i zostawia
    nieprzetworzone URL-e w pliku listy (nie przenosi ich do -DONE).

    Zalozenia:
      - Obraz: preferowane 720p -> 1080p -> inne (gdy max < 720p, bierze max dostepny).
      - Kodek obrazu: h264 (bez H.265/AV1/VP9 z preferencji).
      - Dzwiek: AAC (stereo), kontener MP4 - maksymalna zgodnosc ze starymi TV.
      - Kazda playlista w osobnym katalogu, pliki z tytulem i numerem.
      - Duplikaty w obrebie playlisty sa pomijane (download-archive).
      - Po zakonczeniu pobierania zawartosc listy jest przenoszona do pliku
        z sufiksem -DONE.txt (dopisywana na koncu, jesli plik juz istnieje),
        a oryginalny plik listy jest usuwany.

    Dlawienie YouTube:
      - YouTube potrafi drastycznie dlawic strumienie DASH (np. bardzo dlugie filmy).
      - Dlatego dla pojedynczych filmow, jesli pierwsza proba sie nie powiedzie,
        skrypt automatycznie ponawia pobieranie w wariancie HLS (m3u8), ktory
        zwykle omija dlawienie.
      - Dla playlist domyslnie NIE ma drugiego przebiegu (jest kosztowny);
        ustaw $HlsFallbackForPlaylists = $true, aby go wlaczyc.
#>

param(
    [string]$ListFile = 'yt-list.txt',
    [double]$MaxTotalGB = 0
)

$ErrorActionPreference = 'Stop'

$HlsFallbackForPlaylists = $false

$root     = Split-Path -Parent $MyInvocation.MyCommand.Path
$ytdlp    = Join-Path $root 'yt-dlp.exe'
if ([System.IO.Path]::IsPathRooted($ListFile)) {
    $listFile = $ListFile
} else {
    $listFile = Join-Path $root $ListFile
}
$baseOut  = Join-Path $root 'downloads'
$archDir  = Join-Path $baseOut '.archives'

if (-not (Test-Path -LiteralPath $ytdlp))    { throw "Nie znaleziono: $ytdlp" }
if (-not (Test-Path -LiteralPath $listFile)) { throw "Nie znaleziono: $listFile" }

New-Item -ItemType Directory -Force -Path $baseOut | Out-Null
New-Item -ItemType Directory -Force -Path $archDir | Out-Null

$baselineBytes = (Get-ChildItem $baseOut -Recurse -File -ErrorAction SilentlyContinue | Measure-Object Length -Sum).Sum
if (-not $baselineBytes) { $baselineBytes = 0 }
$limitBytes = if ($MaxTotalGB -gt 0) { $baselineBytes + ($MaxTotalGB * 1GB) } else { [double]::MaxValue }
$minFreeBytes = 0
if ($MaxTotalGB -gt 0) { $minFreeBytes = $limitBytes - (300MB) } # margines na jeden plik

$baseArgs = @(
    '--ignore-errors'
    '--no-warnings'
    '--newline'
    '--continue'
    '--windows-filenames'
    '--js-runtimes'
    'node'
    '--socket-timeout'
    '60'
    '--retries'
    '20'
    '--fragment-retries'
    '20'
    '--retry-sleep'
    '5'
)

$sortArgs = @(
    '-S'
    '+res:720,vcodec:h264,acodec:aac'
    '--merge-output-format'
    'mp4'
    '--remux-video'
    'mp4'
)

$fmtDash = 'bv*[vcodec^=avc1]+ba[acodec^=mp4a]/bv*[vcodec^=avc1]+ba[ext=m4a]/bv*[vcodec^=avc1]+ba'
$fmtHls  = 'bv*[protocol*=m3u8][vcodec^=avc1]+ba[acodec^=mp4a]/bv*[protocol*=m3u8][vcodec^=avc1]+ba/bv*[vcodec^=avc1]+ba[acodec^=mp4a]/bv*[vcodec^=avc1]+ba'

$urls = @(Get-Content -LiteralPath $listFile |
    ForEach-Object { $_.Trim() } |
    Where-Object { $_ -ne '' -and -not $_.StartsWith('#') })

if (-not $urls) { throw "Brak adresow w $listFile" }

$ok = 0
$fail = 0
$stoppedByLimit = $false

for ($i = 0; $i -lt $urls.Count; $i++) {
    $url = $urls[$i]

    if ($MaxTotalGB -gt 0) {
        $currentBytes = (Get-ChildItem $baseOut -Recurse -File -ErrorAction SilentlyContinue | Measure-Object Length -Sum).Sum
        if (-not $currentBytes) { $currentBytes = 0 }
        if ($currentBytes -ge $minFreeBytes) {
            $stoppedByLimit = $true
            Write-Host "Osiagnieto limit $MaxTotalGB GB - przerywam pobieranie." -ForegroundColor Yellow
            break
        }
    }

    Write-Host ""
    Write-Host "=== $url ===" -ForegroundColor Cyan

    $isPlaylist = ($url -match '[?&]list=([A-Za-z0-9_-]+)') -or ($url -match '/playlist')

    if ($isPlaylist) {
        $plId = if ($matches.Count -gt 1 -and $matches[1]) { $matches[1] } else { 'playlist' }
        $archive = Join-Path $archDir "$plId.txt"
        $outTpl  = Join-Path $baseOut '%(playlist_title)s\%(playlist_index)03d - %(title)s.%(ext)s'
        $prefix  = @('--download-archive', $archive, '-o', $outTpl)
        Write-Host "Tryb: PLAYLISTA  (archiwum: $archive)"
    }
    else {
        $outTpl = Join-Path $baseOut '%(title)s.%(ext)s'
        $prefix = @('-o', $outTpl)
        Write-Host "Tryb: POJEDYNCZY FILM"
    }

    $argsDash = $prefix + $baseArgs + $sortArgs + @('-f', $fmtDash) + @($url)
    & $ytdlp @argsDash
    $code = $LASTEXITCODE

    $allowHlsFallback = (-not $isPlaylist) -or $HlsFallbackForPlaylists
    if ($code -ne 0 -and $allowHlsFallback) {
        Write-Host "-> pierwsza proba nieudana; ponawiam z HLS (omija dlawienie)..." -ForegroundColor Yellow
        $argsHls = $prefix + $baseArgs + $sortArgs + @('-f', $fmtHls) + @($url)
        & $ytdlp @argsHls
        $code = $LASTEXITCODE
    }

    if ($code -eq 0) { $ok++ } else { $fail++ }
}

Write-Host ""
Write-Host "Sprzatam niepotrzebne pliki .part (gdy finalny MP4 juz istnieje)..."
Get-ChildItem $baseOut -Recurse -Filter *.part -File -ErrorAction SilentlyContinue | ForEach-Object {
    if ($_.Name -match '^(.*)\.f[0-9A-Za-z_-]+\.(mp4|m4a|webm|mp3)\.part$') {
        $final = Join-Path $_.DirectoryName ($matches[1] + '.mp4')
        if (Test-Path -LiteralPath $final) { Remove-Item -LiteralPath $_.FullName -Force -ErrorAction SilentlyContinue }
    }
}

$mp4Count = (Get-ChildItem $baseOut -Recurse -Filter *.mp4 -File -ErrorAction SilentlyContinue).Count
$totalBytes = (Get-ChildItem $baseOut -Recurse -File -ErrorAction SilentlyContinue | Measure-Object Length -Sum).Sum
if (-not $totalBytes) { $totalBytes = 0 }
$sizeGb   = [math]::Round(($totalBytes / 1GB), 2)
$deltaGb  = [math]::Round((($totalBytes - $baselineBytes) / 1GB), 2)

Write-Host ""
Write-Host "Gotowe. URL: sukces=$ok, bledy=$fail | plikow MP4: $mp4Count | rozmiar: $sizeGb GB (w tym zadaniu: $deltaGb GB)" -ForegroundColor Green

# Po zakonczeniu pobierania przenies zawartosc listy do pliku z sufiksem -DONE.txt.
$listDir  = Split-Path -Parent $listFile
$listBase = [System.IO.Path]::GetFileNameWithoutExtension($listFile)
$doneFile = Join-Path $listDir ($listBase + '-DONE.txt')

if ($stoppedByLimit) {
    $remaining = @()
    if ($i -lt $urls.Count) { $remaining = @($urls[$i..($urls.Count - 1)]) }
    Set-Content -LiteralPath $listFile -Value $remaining -Encoding UTF8
    Write-Host "Lista nie zostala przeniesiona do -DONE; w pliku pozostalo $($remaining.Count) URL." -ForegroundColor Yellow
}
elseif ($listBase -match '-DONE$') {
    Write-Host "Lista '$listBase' jest juz plikiem -DONE; pomijam przenoszenie." -ForegroundColor DarkYellow
}
elseif (Test-Path -LiteralPath $listFile) {
    try {
        $listContent = Get-Content -LiteralPath $listFile
        if (Test-Path -LiteralPath $doneFile) {
            Add-Content -LiteralPath $doneFile -Value (@('') + $listContent)
        }
        else {
            Set-Content -LiteralPath $doneFile -Value $listContent -Encoding UTF8
        }
        Remove-Item -LiteralPath $listFile -Force
        Write-Host "Przeniesiono zawartosc listy do: $doneFile" -ForegroundColor Cyan
    }
    catch {
        Write-Host "Nie udalo sie przeniesc listy do '$doneFile': $($_.Exception.Message)" -ForegroundColor Yellow
    }
}
