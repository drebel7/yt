#requires -Version 5.1
<#
    kodeki.ps1 - kontrola i naprawa kodekow pod stare odtwarzacze.

    Po co: yt-dlp potrafi czasem sciagnac VP9/AV1 (mimo preferencji H.264),
    a stary odtwarzacz DVD/Blu-ray lub telewizor takich plikow nie odtworzy.
    Ten plik sprawdza strumienie (ffprobe) i w razie potrzeby transkoduje
    do H.264 + AAC w MP4 (ffmpeg).

    Funkcje:
      Get-MediaInfo            - odczyt kodekow/rozdzielczosci/czasu (ffprobe).
      Test-MediaCompatible     - czy plik jest zgodny (H.264, yuv420p, AAC, MP4).
      ConvertTo-CompatibleMedia - transkoduje jeden plik, weryfikuje wynik.
      Repair-MediaCodecs       - przechodzi katalog; domyslnie dry-run.

    Uzycie reczne:
        . .\kodeki.ps1
        Repair-MediaCodecs -Path 'downloads' -Recurse              # podglad
        Repair-MediaCodecs -Path 'downloads' -Recurse -Apply       # naprawa

    Uwaga: transkodowanie jest kosztowne (czas CPU), ale bezstratne dla nazw
    plikow. Oryginal mozna zachowac przelacznikiem -KeepOriginal.
#>

$script:MediaExtensions = @('.mp4', '.m4v', '.mkv', '.webm', '.mov', '.avi')

function Test-FfmpegAvailable {
    [CmdletBinding()]
    param()
    foreach ($exe in 'ffmpeg', 'ffprobe') {
        if (-not (Get-Command $exe -ErrorAction SilentlyContinue)) {
            throw "Nie znaleziono '$exe' w PATH. Zainstaluj ffmpeg i dodaj do PATH."
        }
    }
}

function Get-MediaInfo {
    <#
    .SYNOPSIS
        Zwraca informacje o strumieniach pliku multimedialnego (albo $null).
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true, Position = 0)]
        [string]$Path
    )

    if (-not (Test-Path -LiteralPath $Path)) { return $null }

    $raw = & ffprobe -v error -show_entries 'stream=codec_type,codec_name,profile,pix_fmt,width,height,channels,sample_rate' -show_entries 'format=duration,format_name' -of json -- $Path 2>$null
    if ($LASTEXITCODE -ne 0 -or -not $raw) { return $null }

    try { $data = ($raw -join "`n") | ConvertFrom-Json }
    catch { return $null }

    $video = @($data.streams | Where-Object { $_.codec_type -eq 'video' } | Select-Object -First 1)
    $audio = @($data.streams | Where-Object { $_.codec_type -eq 'audio' } | Select-Object -First 1)

    $videoCodec = if ($video.Count -gt 0) { [string]$video[0].codec_name } else { '' }
    $audioCodec = if ($audio.Count -gt 0) { [string]$audio[0].codec_name } else { '' }
    $pixFmt     = if ($video.Count -gt 0) { [string]$video[0].pix_fmt } else { '' }
    $container  = [string]$data.format.format_name

    $reasons = @()
    if ($videoCodec -ne 'h264') { $reasons += "obraz=$videoCodec" }
    if ($pixFmt -and $pixFmt -ne 'yuv420p' -and $pixFmt -ne 'yuvj420p') { $reasons += "pix_fmt=$pixFmt" }
    if ($audioCodec -and $audioCodec -ne 'aac') { $reasons += "dzwiek=$audioCodec" }
    if ($container -notmatch 'mp4') { $reasons += "kontener=$container" }

    [pscustomobject]@{
        Path         = $Path
        Container    = $container
        DurationSec  = [double]$data.format.duration
        VideoCodec   = $videoCodec
        VideoProfile = if ($video.Count -gt 0) { [string]$video[0].profile } else { '' }
        PixFmt       = $pixFmt
        Width        = if ($video.Count -gt 0) { [int]$video[0].width } else { 0 }
        Height       = if ($video.Count -gt 0) { [int]$video[0].height } else { 0 }
        AudioCodec   = $audioCodec
        AudioChannels = if ($audio.Count -gt 0) { [int]$audio[0].channels } else { 0 }
        Compatible   = ($reasons.Count -eq 0)
        Reason       = ($reasons -join ', ')
    }
}

function Test-MediaCompatible {
    <#
    .SYNOPSIS
        $true, gdy plik jest H.264/yuv420p + AAC w kontenerze MP4.
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true, Position = 0)]
        [string]$Path
    )

    $info = Get-MediaInfo -Path $Path
    if (-not $info) { return $false }
    return $info.Compatible
}

function ConvertTo-CompatibleMedia {
    <#
    .SYNOPSIS
        Transkoduje jeden plik do H.264 (Main) + AAC w MP4.
    .DESCRIPTION
        Zapisuje wynik do pliku tymczasowego, weryfikuje go ffprobe i dopiero
        wtedy zastepuje oryginal. Przy bledzie oryginal zostaje nietkniety.
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true, Position = 0)]
        [string]$Path,

        [int]$Crf = 20,
        [string]$Preset = 'fast',
        [switch]$KeepOriginal,
        [int]$TimeoutMinutes = 60
    )

    Test-FfmpegAvailable

    $info = Get-MediaInfo -Path $Path
    if (-not $info) {
        return [pscustomobject]@{ Name = (Split-Path -Leaf $Path); Status = 'ERROR'; Reason = 'nie mozna odczytac pliku'; OldVideo = ''; OldAudio = ''; NewVideo = ''; NewAudio = ''; SizeMB = 0 }
    }
    if ($info.Compatible) {
        return [pscustomobject]@{ Name = (Split-Path -Leaf $Path); Status = 'SKIP'; Reason = ''; OldVideo = $info.VideoCodec; OldAudio = $info.AudioCodec; NewVideo = $info.VideoCodec; NewAudio = $info.AudioCodec; SizeMB = [math]::Round((Get-Item -LiteralPath $Path).Length / 1MB, 1) }
    }

    $dir  = Split-Path -Parent $Path
    $base = [System.IO.Path]::GetFileNameWithoutExtension($Path)
    $tmp  = Join-Path $dir ($base + '.compat.mp4')
    $target = Join-Path $dir ($base + '.mp4')

    if (Test-Path -LiteralPath $tmp) { Remove-Item -LiteralPath $tmp -Force }

    $ffArgs = @(
        '-hide_banner', '-loglevel', 'warning', '-nostdin', '-y'
        '-i', $Path
        '-map', '0:v:0'
    )
    if ($info.AudioCodec) { $ffArgs += @('-map', '0:a:0?') }

    $ffArgs += @(
        '-c:v', 'libx264'
        '-preset', $Preset
        '-crf', [string]$Crf
        '-profile:v', 'main'
        '-pix_fmt', 'yuv420p'
        '-vf', 'scale=trunc(iw/2)*2:trunc(ih/2)*2'
        '-movflags', '+faststart'
        '-map_metadata', '0'
    )

    if ($info.AudioCodec -eq 'aac') {
        $ffArgs += @('-c:a', 'copy')
    }
    elseif ($info.AudioCodec) {
        $ffArgs += @('-c:a', 'aac', '-b:a', '192k', '-ac', '2')
    }
    else {
        $ffArgs += @('-an')
    }

    $ffArgs += @($tmp)

    # ffmpeg uruchamiamy przez System.Diagnostics.Process: wlasne cytowanie
    # argumentow (sciezki ze spacjami!), asynchroniczny odczyt strumieni
    # (brak blokady na potoku) i limit czasu na plik.
    $argString = ($ffArgs | ForEach-Object {
        $a = [string]$_
        if ($a -match '\s') { '"' + $a + '"' } else { $a }
    }) -join ' '

    $started = Get-Date
    $timedOut = $false
    $code = -1
    $ffmpegMessage = ''

    $psi = New-Object System.Diagnostics.ProcessStartInfo
    $psi.FileName = (Get-Command ffmpeg -ErrorAction Stop).Source
    $psi.Arguments = $argString
    $psi.UseShellExecute = $false
    $psi.CreateNoWindow = $true
    $psi.RedirectStandardOutput = $true
    $psi.RedirectStandardError = $true

    $proc = New-Object System.Diagnostics.Process
    $proc.StartInfo = $psi
    [void]$proc.Start()
    $outTask = $proc.StandardOutput.ReadToEndAsync()
    $errTask = $proc.StandardError.ReadToEndAsync()

    if (-not $proc.WaitForExit($TimeoutMinutes * 60 * 1000)) {
        $timedOut = $true
        try { $proc.Kill() } catch { }
        try { $proc.WaitForExit(10000) | Out-Null } catch { }
    }
    else {
        $code = $proc.ExitCode
    }
    $elapsed = (Get-Date) - $started

    try { [void]$outTask.Result } catch { }
    try {
        $errText = [string]$errTask.Result
        $errLines = @($errText -split "`r?`n" | Where-Object { $_.Trim() })
        if ($errLines.Count -gt 0) {
            $ffmpegMessage = $errLines[$errLines.Count - 1].Trim()
            if ($ffmpegMessage.Length -gt 140) { $ffmpegMessage = $ffmpegMessage.Substring(0, 140) }
        }
    }
    catch { }

    if ($code -ne 0 -or -not (Test-Path -LiteralPath $tmp)) {
        if (Test-Path -LiteralPath $tmp) { Remove-Item -LiteralPath $tmp -Force -ErrorAction SilentlyContinue }
        $reason = if ($timedOut) { "przekroczono limit $TimeoutMinutes min" } elseif ($ffmpegMessage) { $ffmpegMessage } else { "ffmpeg kod $code" }
        return [pscustomobject]@{ Name = (Split-Path -Leaf $Path); Status = 'ERROR'; Reason = $reason; OldVideo = $info.VideoCodec; OldAudio = $info.AudioCodec; NewVideo = ''; NewAudio = ''; SizeMB = 0 }
    }

    $check = Get-MediaInfo -Path $tmp
    if (-not $check -or -not $check.Compatible) {
        Remove-Item -LiteralPath $tmp -Force -ErrorAction SilentlyContinue
        return [pscustomobject]@{ Name = (Split-Path -Leaf $Path); Status = 'ERROR'; Reason = 'weryfikacja wyniku nieudana'; OldVideo = $info.VideoCodec; OldAudio = $info.AudioCodec; NewVideo = ''; NewAudio = ''; SizeMB = 0 }
    }

    if ($KeepOriginal) {
        $backup = Join-Path $dir ($base + '.orig' + [System.IO.Path]::GetExtension($Path))
        if (Test-Path -LiteralPath $backup) { Remove-Item -LiteralPath $backup -Force }
        Move-Item -LiteralPath $Path -Destination $backup
    }
    else {
        Remove-Item -LiteralPath $Path -Force
    }

    if (Test-Path -LiteralPath $target) { Remove-Item -LiteralPath $target -Force -ErrorAction SilentlyContinue }
    Move-Item -LiteralPath $tmp -Destination $target

    return [pscustomobject]@{
        Name     = (Split-Path -Leaf $target)
        Status   = 'CONVERTED'
        Reason   = $info.Reason
        OldVideo = $info.VideoCodec
        OldAudio = $info.AudioCodec
        NewVideo = $check.VideoCodec
        NewAudio = $check.AudioCodec
        SizeMB   = [math]::Round((Get-Item -LiteralPath $target).Length / 1MB, 1)
        Seconds  = [math]::Round($elapsed.TotalSeconds, 1)
    }
}

function Repair-MediaCodecs {
    <#
    .SYNOPSIS
        Sprawdza kodeki w katalogu i (z -Apply) transkoduje niezgodne pliki.
    .DESCRIPTION
        Domyslnie tylko raportuje (dry-run). -Since ogranicza sie do plikow
        zmodyfikowanych po danej dacie (przydatne po pobraniu). -WhatIf nie jest
        potrzebne: bez -Apply nic nie jest zmieniane.
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true, Position = 0)]
        [string]$Path,

        [switch]$Recurse,
        [switch]$Apply,

        [datetime]$Since,
        [int]$Crf = 20,
        [string]$Preset = 'fast',
        [switch]$KeepOriginal,
        [int]$TimeoutMinutes = 60,
        [string]$LogPath
    )

    if (-not (Test-Path -LiteralPath $Path)) { throw "Nie znaleziono: $Path" }
    Test-FfmpegAvailable

    $item = Get-Item -LiteralPath $Path
    if ($item.PSIsContainer) {
        $files = @(Get-ChildItem -LiteralPath $item.FullName -File -Recurse:$Recurse -Force -ErrorAction SilentlyContinue |
            Where-Object {
                $script:MediaExtensions -contains $_.Extension.ToLowerInvariant() -and
                $_.DirectoryName -notmatch '[\\/]\.(archives|staging)([\\/]|$)'
            })
    }
    else {
        $files = @($item)
    }

    if ($PSBoundParameters.ContainsKey('Since')) {
        $files = @($files | Where-Object { $_.LastWriteTime -ge $Since })
    }

    $files = @($files | Sort-Object FullName)
    $results = New-Object System.Collections.Generic.List[object]

    foreach ($file in $files) {
        $info = Get-MediaInfo -Path $file.FullName
        if (-not $info) {
            $results.Add([pscustomobject]@{ Name = $file.Name; Status = 'ERROR'; Reason = 'brak danych'; OldVideo = ''; OldAudio = ''; NewVideo = ''; NewAudio = ''; SizeMB = 0 })
            continue
        }
        if ($info.Compatible) { continue }

        if (-not $Apply) {
            Write-Host ("  DO NAPRAWY  {0}  ({1})" -f $file.Name, $info.Reason) -ForegroundColor Yellow
            $results.Add([pscustomobject]@{ Name = $file.Name; Status = 'DRYRUN'; Reason = $info.Reason; OldVideo = $info.VideoCodec; OldAudio = $info.AudioCodec; NewVideo = ''; NewAudio = ''; SizeMB = [math]::Round($file.Length / 1MB, 1) })
            continue
        }

        Write-Host ("  TRANSKOD  {0}  ({1})" -f $file.Name, $info.Reason) -ForegroundColor Cyan
        $result = ConvertTo-CompatibleMedia -Path $file.FullName -Crf $Crf -Preset $Preset -KeepOriginal:$KeepOriginal -TimeoutMinutes $TimeoutMinutes
        if ($result.Status -eq 'CONVERTED') {
            Write-Host ("  OK        {0}  ({1} MB, {2} s)" -f $result.Name, $result.SizeMB, $result.Seconds) -ForegroundColor Green
        }
        else {
            Write-Host ("  BLAD      {0}  ({1})" -f $result.Name, $result.Reason) -ForegroundColor Red
        }
        $results.Add($result)
    }

    if ($LogPath -and $results.Count -gt 0) {
        $logDir = Split-Path -Parent $LogPath
        if ($logDir -and -not (Test-Path -LiteralPath $logDir)) {
            New-Item -ItemType Directory -Force -Path $logDir | Out-Null
        }
        $results | Select-Object Name, Status, Reason, OldVideo, OldAudio, NewVideo, NewAudio, SizeMB, Seconds |
            Export-Csv -LiteralPath $LogPath -NoTypeInformation -Encoding UTF8
    }

    return $results.ToArray()
}
