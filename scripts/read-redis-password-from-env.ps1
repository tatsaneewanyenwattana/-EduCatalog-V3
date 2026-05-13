# Emit REDIS_PASSWORD value from backend/.env (single line stdout, no newline). Makefile $(shell ...) on Win.

$repoRoot = Split-Path -Parent $PSScriptRoot
$envPath = Join-Path $repoRoot 'backend\.env'
if (-not (Test-Path -LiteralPath $envPath)) {
    exit 0
}
$utf8 = New-Object System.Text.UTF8Encoding $false
$content = [System.IO.File]::ReadAllText($envPath, $utf8)
foreach ($line in ($content -split "`r?`n")) {
    if ($line -match '^\s*REDIS_PASSWORD\s*=\s*(.*)$') {
        $val = $Matches[1].Trim()
        Write-Output ($val.Trim([char]0x22))
        exit 0
    }
}
