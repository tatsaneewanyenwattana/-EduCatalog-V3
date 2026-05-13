# -------------------------------------------------------
# ส่งต่อ args ไป docker compose โดยบังคับใช้ backend/.env เป็นตัวแทนค่า ${...} ใน compose
# เพราะ compose โดย default อ่านแค่ .env ที่ root — ถ้าไม่ sync จะชนกับ env_file ของ container
# -------------------------------------------------------
param(
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$ComposeArgs
)

$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$root = Split-Path -Parent $here
$envFile = Join-Path $root "backend\.env"

if (-not (Test-Path $envFile)) {
    Write-Error "ไม่พบ $envFile — สร้างจาก backend\.env.example ก่อน"
    exit 1
}

Set-Location $root
& docker compose --env-file $envFile @ComposeArgs
