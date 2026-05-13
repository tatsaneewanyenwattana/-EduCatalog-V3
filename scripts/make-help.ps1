# Parse Makefile "##" target descriptions (Windows make has no awk/sh for help).

$root = Split-Path -Parent $PSScriptRoot
$makefile = Join-Path $root 'Makefile'
if (-not (Test-Path -LiteralPath $makefile)) {
    Write-Error "Makefile not found: $makefile"
    exit 1
}

# ReadAllText + split: stable on Windows PowerShell 5 for both LF and CRLF.
$utf8NoBom = New-Object System.Text.UTF8Encoding $false
$raw = [System.IO.File]::ReadAllText($makefile, $utf8NoBom)
$lines = $raw -split "`r?`n"

foreach ($line in $lines) {
    if ($line -match '^([a-zA-Z0-9_.-]+):.*## (.+)') {
        $t = $Matches[1].Trim()
        $d = $Matches[2].Trim()
        # ASCII separator so Windows PowerShell 5 parses this file under any default code page
        '  {0,-16} - {1}' -f $t, $d
    }
}
