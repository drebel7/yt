#requires -Version 5.1
<#
    nazwy.ps1 - normalizacja nazw plikow do bezpiecznego ASCII.

    Po co: stare odtwarzacze DVD/Blu-ray, telewizory z USB i udzialy sieciowe
    (DLNA/SMB) czesto nie obsluguja nazw spoza swojej strony kodowej. Emoji,
    znaki pelnoszerokie (CJK), cyrylica i symbole powoduja krzaki, obcinanie
    nazw albo calkowite pomijanie plikow na liscie.

    Funkcje:
      ConvertTo-SafeFileName  - zamienia tytul/kanal na bezpieczna nazwe.
      Rename-ToSafeNames      - masowa zmiana nazw w katalogu (domyslnie dry-run).

    Zasady:
      - wynik jest zawsze czystym ASCII (0x20-0x7E),
      - polskie i inne lacinskie znaki sa transliterowane (a, c, e, l, n, o, s, z),
      - cyrylica jest transliterowana,
      - emoji, symbole i znaki formatujace sa usuwane albo zamieniane na " - ",
      - prefiks "NNN - " (numer pozycji playlisty) jest zachowany bez zmian,
      - funkcja jest idempotentna: drugi przebieg nie zmienia nazwy.

    Przyklad:
        . .\nazwy.ps1
        ConvertTo-SafeFileName '105 - Test - Piosenka' -MaxLength 90

        # podglad bez zmiany plikow
        Rename-ToSafeNames -Path 'downloads\Mix' -Recurse

        # wlasciwa zmiana + log CSV
        Rename-ToSafeNames -Path 'downloads\Mix' -Recurse -Apply -LogPath 'rename.csv'
#>

# Domyslny limit dlugosci nazwy (znaki, bez rozszerzenia). 110 zostawia miejsce
# na artyste i date, a nadal jest daleko od limitu FAT32/NTFS (255) i od
# typowych ograniczen odtwarzaczy.
$script:SafeNameMaxLength = 110

# Cyrylica: zakresy 0x410-0x42F (A..Ja) i 0x430-0x44F (a..ja).
# Uwaga: "jo" (0x401/0x451) lezy poza zakresem i jest dopisane osobno.
$script:CyrillicLatin = @(
    'A', 'B', 'V', 'G', 'D', 'E', 'Zh', 'Z', 'I', 'Y', 'K', 'L', 'M', 'N', 'O', 'P',
    'R', 'S', 'T', 'U', 'F', 'Kh', 'Ts', 'Ch', 'Sh', 'Shch', '', 'Y', '', 'E', 'Yu', 'Ya'
)

$script:CyrillicMap = @{}
for ($i = 0; $i -lt $script:CyrillicLatin.Count; $i++) {
    $upper = $script:CyrillicLatin[$i]
    $lower = $upper.ToLowerInvariant()
    $script:CyrillicMap[[int][char](0x410 + $i)] = $upper
    $script:CyrillicMap[[int][char](0x430 + $i)] = $lower
}
$script:CyrillicMap[0x401] = 'Yo'
$script:CyrillicMap[0x451] = 'yo'

function ConvertTo-SafeFileName {
    <#
    .SYNOPSIS
        Zamienia dowolna nazwe na bezpieczne ASCII.
    .DESCRIPTION
        Normalizuje Unicode (NFC + NFKD), transliteruje litery, usuwa emoji
        i znaki formatujace, zamienia separatory na " - " i porzadkuje spacje.
        Prefiks "NNN - " jest zachowany.
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true, Position = 0)]
        [AllowEmptyString()]
        [string]$Name,

        [int]$MaxLength = $script:SafeNameMaxLength
    )

    if ($MaxLength -lt 20) { $MaxLength = 20 }

    $numberPrefix = ''
    $body = $Name
    if ($body -match '^(\d{3}) - (.*)$') {
        $numberPrefix = $matches[1] + ' - '
        $body = $matches[2]
    }

    $normalized = $body.Normalize([System.Text.NormalizationForm]::FormC)
    $normalized = $normalized.Normalize([System.Text.NormalizationForm]::FormKD)

    $chars = $normalized.ToCharArray()
    $buffer = New-Object System.Text.StringBuilder

    for ($i = 0; $i -lt $chars.Length; $i++) {
        $ch = $chars[$i]
        $code = [int]$ch

        if ($code -lt 128) {
            if ($ch -eq '&') {
                # "X & Y" -> "X i Y"; "G&K" -> "GK" (bez doklejania litery).
                $prev = if ($i -gt 0) { $chars[$i - 1] } else { ' ' }
                $next = if ($i -lt $chars.Length - 1) { $chars[$i + 1] } else { ' ' }
                if ($prev -eq ' ' -and $next -eq ' ') {
                    [void]$buffer.Append(' i ')
                }
                continue
            }

            if ($ch -eq '@') { [void]$buffer.Append(' '); continue }
            if ($ch -eq '#') {
                # "#1" -> "nr 1", ale "#hit2026" -> "hit2026" (bez zbednego "nr").
                $next = if ($i -lt $chars.Length - 1) { $chars[$i + 1] } else { ' ' }
                if ([char]::IsDigit($next)) { [void]$buffer.Append(' nr ') }
                else { [void]$buffer.Append(' ') }
                continue
            }
            if ($ch -eq '$') { [void]$buffer.Append('S'); continue }
            if ($ch -eq '+' -or $ch -eq '|' -or $ch -eq ':' -or $ch -eq '/' -or $ch -eq '\') {
                [void]$buffer.Append(' - ')
                continue
            }
            if ($ch -eq '"') { [void]$buffer.Append(' '); continue }
            if ($ch -eq '*' -or $ch -eq '?' -or $ch -eq '<' -or $ch -eq '>' -or
                $ch -eq '^' -or $ch -eq '~' -or $ch -eq '`') {
                continue
            }

            [void]$buffer.Append($ch)
            continue
        }

        if ($script:CyrillicMap.ContainsKey($code)) {
            [void]$buffer.Append($script:CyrillicMap[$code])
            continue
        }

        $category = [System.Globalization.CharUnicodeInfo]::GetUnicodeCategory($ch)
        if ($category -eq [System.Globalization.UnicodeCategory]::NonSpacingMark -or
            $category -eq [System.Globalization.UnicodeCategory]::SpacingCombiningMark -or
            $category -eq [System.Globalization.UnicodeCategory]::EnclosingMark -or
            $category -eq [System.Globalization.UnicodeCategory]::Surrogate -or
            $category -eq [System.Globalization.UnicodeCategory]::Format) {
            continue
        }

        if ($code -eq 0x142 -or $code -eq 0x141) {          # l z kreska / L z kreska
            [void]$buffer.Append($(if ($code -eq 0x142) { 'l' } else { 'L' }))
            continue
        }
        if ($code -eq 0x00DF) { [void]$buffer.Append('ss'); continue }  # szarfes es
        if ($code -eq 0x00E6) { [void]$buffer.Append('ae'); continue }
        if ($code -eq 0x00C6) { [void]$buffer.Append('AE'); continue }
        if ($code -eq 0x0153) { [void]$buffer.Append('oe'); continue }
        if ($code -eq 0x0152) { [void]$buffer.Append('OE'); continue }
        if ($code -eq 0x00F8) { [void]$buffer.Append('o'); continue }
        if ($code -eq 0x00D8) { [void]$buffer.Append('O'); continue }
        if ($code -eq 0x0111) { [void]$buffer.Append('d'); continue }
        if ($code -eq 0x0110) { [void]$buffer.Append('D'); continue }

        if ($code -eq 0x2018 -or $code -eq 0x2019) { [void]$buffer.Append("'"); continue }
        if ($code -eq 0x201C -or $code -eq 0x201D) { continue }
        if ($code -eq 0x2026) { [void]$buffer.Append('...'); continue }

        # Myslniki, separator "duzy ukosnik", punktory: ujednolicamy do " - ".
        if ($code -eq 0x2013 -or $code -eq 0x2014 -or $code -eq 0x2015 -or
            $code -eq 0x29F8 -or $code -eq 0x2022) {
            [void]$buffer.Append(' - ')
            continue
        }

        if ($category -eq [System.Globalization.UnicodeCategory]::OtherSymbol -or
            $category -eq [System.Globalization.UnicodeCategory]::MathSymbol -or
            $category -eq [System.Globalization.UnicodeCategory]::ModifierSymbol -or
            $category -eq [System.Globalization.UnicodeCategory]::OtherPunctuation) {
            [void]$buffer.Append(' - ')
            continue
        }

        [void]$buffer.Append($ch)
    }

    $text = $buffer.ToString()
    $text = $text -replace "'", ''
    $text = $text -replace '\s+', ' '
    $text = $text.Trim()

    while ($text.Contains(' - - ')) { $text = $text.Replace(' - - ', ' - ') }

    $text = $text -replace '\s*\(\s*', ' ('
    $text = $text -replace '\s*\)', ')'

    $text = $text -replace '^\s*-\s*', ''
    $text = $text -replace '\s*-\s*$', ''
    $text = $text -replace '\s+', ' '
    # Wielokropek usuwamy przed porzadkami, zeby nie zostawial samotnej kropki.
    $text = $text -replace '\.{3,}', ''
    $text = $text -replace '\s+\.', '.'
    $text = $text -replace '\.{2,}', '.'
    # " - ...Tytul" -> " - Tytul", ".ukryty" -> "ukryty"
    $text = $text -replace '(^|[\s\-]+)\.', '$1'
    $text = $text -replace '\(\s*\)', ''
    $text = $text.Trim()
    $text = $text.TrimEnd('.', ' ', '-', '_')

    if (-not $text) { $text = 'untitled' }

    $budget = $MaxLength - $numberPrefix.Length
    if ($budget -lt 20) { $budget = 20 }
    if ($text.Length -gt $budget) {
        $cut = $text.Substring(0, $budget)
        $space = $cut.LastIndexOf(' ')
        if ($space -gt 20) { $cut = $cut.Substring(0, $space) }
        $cut = $cut.Trim().TrimEnd('-', '.', '_', ' ')
        if ($cut) { $text = $cut }
    }

    return ($numberPrefix + $text)
}

function Get-FreeName {
    # Zwraca nazwe wolna w danym katalogu; przy kolizji dodaje " (2)", " (3)"...
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)][string]$Directory,
        [Parameter(Mandatory = $true)][string]$BaseName,
        [string]$Extension = '',
        [Parameter(Mandatory = $true)][System.Collections.Generic.HashSet[string]]$Taken
    )

    $candidate = $BaseName + $Extension
    if (-not $Taken.Contains($candidate) -and
        -not (Test-Path -LiteralPath (Join-Path $Directory $candidate))) {
        return $candidate
    }

    $n = 2
    while ($true) {
        $candidate = ('{0} ({1}){2}' -f $BaseName, $n, $Extension)
        if (-not $Taken.Contains($candidate) -and
            -not (Test-Path -LiteralPath (Join-Path $Directory $candidate))) {
            return $candidate
        }
        $n++
    }
}

function Rename-ToSafeNames {
    <#
    .SYNOPSIS
        Zmienia nazwy plikow (i opcjonalnie katalogow) na bezpieczne ASCII.
    .DESCRIPTION
        Domyslnie tylko pokazuje plan zmian (dry-run). Z -Apply wykonuje zmiane
        i zapisuje mapowanie do CSV (jesli podano -LogPath).
        Kolizje rozwiazuje sufiksem " (2)", " (3)" - nigdy nie nadpisuje plikow.
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true, Position = 0)]
        [string]$Path,

        [switch]$Apply,
        [switch]$Recurse,
        [switch]$IncludeDirectories,

        [int]$MaxLength = $script:SafeNameMaxLength,
        [string]$LogPath
    )

    if (-not (Test-Path -LiteralPath $Path)) { throw "Nie znaleziono: $Path" }

    $rootItem = Get-Item -LiteralPath $Path
    $rootPath = $rootItem.FullName
    $records = New-Object System.Collections.Generic.List[object]
    $dirRecords = New-Object System.Collections.Generic.List[object]
    $dirTaken = @{}

    # Katalogi: od najglebszych, zeby sciezki plikow byly juz po zmianie.
    if ($IncludeDirectories -and $rootItem.PSIsContainer) {
        $dirs = @(Get-ChildItem -LiteralPath $rootPath -Directory -Recurse -Force -ErrorAction SilentlyContinue |
            Where-Object {
                $_.Name -notmatch '^\.' -and
                $_.Name -ne '.archives' -and
                $_.Name -ne '.staging'
            } |
            Sort-Object { ($_.FullName.ToCharArray() | Where-Object { $_ -eq '\' }).Count } -Descending)

        foreach ($dir in $dirs) {
            $parent = Split-Path -Parent $dir.FullName
            if (-not $dirTaken.ContainsKey($parent)) {
                $set = [System.Collections.Generic.HashSet[string]]::new([System.StringComparer]::OrdinalIgnoreCase)
                foreach ($sibling in @(Get-ChildItem -LiteralPath $parent -Force -ErrorAction SilentlyContinue)) {
                    [void]$set.Add($sibling.Name)
                }
                $dirTaken[$parent] = $set
            }
            $set = $dirTaken[$parent]

            $newName = ConvertTo-SafeFileName -Name $dir.Name -MaxLength $MaxLength
            if ($newName -eq $dir.Name) { continue }

            $newName = Get-FreeName -Directory $parent -BaseName $newName -Taken $set
            [void]$set.Remove($dir.Name)
            [void]$set.Add($newName)

            $dirRecords.Add([pscustomobject]@{
                Type     = 'Directory'
                FullName = $dir.FullName
                OldName  = $dir.Name
                NewName  = $newName
                Status   = 'DRYRUN'
            })
        }
    }

    # Katalogi zmieniamy od razu, zanim wczytamy liste plikow - inaczej sciezki
    # plikow bylyby nieaktualne i Rename-Item zwrocilby blad.
    foreach ($record in $dirRecords) {
        if ($Apply) {
            try {
                Rename-Item -LiteralPath $record.FullName -NewName $record.NewName -ErrorAction Stop
                $record.Status = 'OK'
            }
            catch {
                $record.Status = 'ERROR'
                Write-Host ("  BLAD: {0} -> {1}: {2}" -f $record.OldName, $record.NewName, $_.Exception.Message) -ForegroundColor Yellow
            }
        }
        $records.Add($record)
    }

    if ($rootItem.PSIsContainer) {
        # Pomijamy katalogi robocze (.archives, .staging) - ich nazwy sa czescia
        # umowy z yt-dlp (ID playlist / indeks transkrypcji).
        $files = @(Get-ChildItem -LiteralPath $rootPath -File -Recurse:$Recurse -Force -ErrorAction SilentlyContinue |
            Where-Object { $_.DirectoryName -notmatch '[\\/]\.(archives|staging)([\\/]|$)' })
    }
    else {
        $files = @($rootItem)
    }

    $fileTaken = @{}
    foreach ($file in $files) {
        $dir = $file.DirectoryName
        if (-not $fileTaken.ContainsKey($dir)) {
            $set = [System.Collections.Generic.HashSet[string]]::new([System.StringComparer]::OrdinalIgnoreCase)
            foreach ($sibling in @(Get-ChildItem -LiteralPath $dir -Force -ErrorAction SilentlyContinue)) {
                [void]$set.Add($sibling.Name)
            }
            $fileTaken[$dir] = $set
        }
        $set = $fileTaken[$dir]

        $base = [System.IO.Path]::GetFileNameWithoutExtension($file.Name)
        $ext  = [System.IO.Path]::GetExtension($file.Name)
        $newBase = ConvertTo-SafeFileName -Name $base -MaxLength $MaxLength
        $newName = $newBase + $ext

        if ($newName -eq $file.Name) { continue }

        $newName = Get-FreeName -Directory $dir -BaseName $newBase -Extension $ext -Taken $set
        [void]$set.Remove($file.Name)
        [void]$set.Add($newName)

        $records.Add([pscustomobject]@{
            Type     = 'File'
            FullName = $file.FullName
            OldName  = $file.Name
            NewName  = $newName
            Status   = 'DRYRUN'
        })
    }

    if ($Apply) {
        foreach ($record in $records) {
            if ($record.Status -ne 'DRYRUN') { continue }  # katalogi zmienione wyzej
            try {
                Rename-Item -LiteralPath $record.FullName -NewName $record.NewName -ErrorAction Stop
                $record.Status = 'OK'
            }
            catch {
                $record.Status = 'ERROR'
                Write-Host ("  BLAD: {0} -> {1}: {2}" -f $record.OldName, $record.NewName, $_.Exception.Message) -ForegroundColor Yellow
            }
        }
    }

    if ($LogPath -and $records.Count -gt 0) {
        $logDir = Split-Path -Parent $LogPath
        if ($logDir -and -not (Test-Path -LiteralPath $logDir)) {
            New-Item -ItemType Directory -Force -Path $logDir | Out-Null
        }
        $records | Select-Object Type, Status, OldName, NewName, FullName |
            Export-Csv -LiteralPath $LogPath -NoTypeInformation -Encoding UTF8
    }

    return $records.ToArray()
}
