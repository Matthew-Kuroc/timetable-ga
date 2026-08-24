$ErrorActionPreference = "Stop"

$frontendRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$repoRoot = (Resolve-Path (Join-Path $frontendRoot "..")).Path

if (-not $env:E2E_DATABASE_URL) {
  $databaseLine = Get-Content (Join-Path $repoRoot ".env") -ErrorAction SilentlyContinue |
    Where-Object { $_ -match '^DATABASE_URL=' } |
    Select-Object -First 1
  if (-not $databaseLine) {
    throw "Thiếu E2E_DATABASE_URL và không tìm thấy DATABASE_URL trong .env."
  }
  $developmentUrl = $databaseLine -replace '^DATABASE_URL=', ''
  $env:E2E_DATABASE_URL = $developmentUrl -replace '/[^/?]+(?=\?|$)', '/timetable_ga_e2e'
}

$env:DATABASE_URL = $env:E2E_DATABASE_URL
$env:PYTHONPATH = $repoRoot
$env:PYTHONUTF8 = "1"
$env:AUTH_COOKIE_SECURE = "false"
$env:E2E_API_BASE_URL = "http://127.0.0.1:18080"
$env:E2E_FRONTEND_BASE_URL = "http://127.0.0.1:15173"
$env:VITE_API_PROXY_TARGET = $env:E2E_API_BASE_URL
$env:CORS_ORIGINS = $env:E2E_FRONTEND_BASE_URL
$env:E2E_ADMIN_USERNAME = "admin.e2e"
$env:E2E_OFFICE_USERNAME = "office.e2e"
$env:E2E_ACCOUNT_PASSWORD = ([guid]::NewGuid().ToString("N") + "Aa1!")
$env:TIMETABLE_RUNTIME_ROOT = Join-Path $repoRoot ".tmp\e2e-runtime-$PID"

$logRoot = Join-Path $repoRoot ".tmp\e2e-logs"
New-Item -ItemType Directory -Path $logRoot -Force | Out-Null
$apiOutput = Join-Path $logRoot "api-$PID.log"
$apiError = Join-Path $logRoot "api-$PID.err.log"
$viteOutput = Join-Path $logRoot "vite-$PID.log"
$viteError = Join-Path $logRoot "vite-$PID.err.log"

function Wait-ForUrl([string]$Url, [string]$Name) {
  for ($attempt = 0; $attempt -lt 120; $attempt++) {
    try {
      $response = Invoke-WebRequest -Uri $Url -UseBasicParsing -TimeoutSec 2
      if ($response.StatusCode -ge 200 -and $response.StatusCode -lt 500) { return }
    } catch {
      Start-Sleep -Milliseconds 500
    }
  }
  throw "$Name không khởi động đúng thời hạn."
}

$apiProcess = $null
$viteProcess = $null
$exitCode = 1
try {
  python (Join-Path $repoRoot "backend\tests\real_e2e_database.py")
  if ($LASTEXITCODE -ne 0) { throw "Không thể chuẩn bị PostgreSQL E2E." }

  Push-Location $repoRoot
  try {
    python -m alembic upgrade head
    if ($LASTEXITCODE -ne 0) { throw "Migration PostgreSQL E2E thất bại." }
    python (Join-Path $repoRoot "backend\tests\real_e2e_seed.py")
    if ($LASTEXITCODE -ne 0) { throw "Không thể seed tài khoản E2E." }
  } finally {
    Pop-Location
  }

  $apiProcess = Start-Process -FilePath python `
    -ArgumentList @("-m", "uvicorn", "backend.app.main:app", "--host", "127.0.0.1", "--port", "18080") `
    -WorkingDirectory $repoRoot -PassThru -WindowStyle Hidden `
    -RedirectStandardOutput $apiOutput -RedirectStandardError $apiError
  Wait-ForUrl "$($env:E2E_API_BASE_URL)/api/health" "FastAPI"
  if ($apiProcess.HasExited) { throw "FastAPI E2E đã dừng ngoài dự kiến." }

  $viteProcess = Start-Process -FilePath node `
    -ArgumentList @("./node_modules/vite/bin/vite.js", "--host", "127.0.0.1", "--port", "15173", "--strictPort") `
    -WorkingDirectory $frontendRoot -PassThru -WindowStyle Hidden `
    -RedirectStandardOutput $viteOutput -RedirectStandardError $viteError
  Wait-ForUrl $env:E2E_FRONTEND_BASE_URL "Vite"
  if ($viteProcess.HasExited) { throw "Vite E2E đã dừng ngoài dự kiến." }

  Push-Location $frontendRoot
  try {
    npx playwright test --config playwright.real.config.ts
    $exitCode = $LASTEXITCODE
  } finally {
    Pop-Location
  }

  if ($exitCode -eq 0) {
    python (Join-Path $repoRoot "backend\tests\real_e2e_verify.py")
    $exitCode = $LASTEXITCODE
  }
} catch {
  Write-Error $_
  if (Test-Path $apiError) { Get-Content $apiError -Tail 80 }
  if (Test-Path $viteError) { Get-Content $viteError -Tail 80 }
  $exitCode = 1
} finally {
  if ($viteProcess -and -not $viteProcess.HasExited) {
    Stop-Process -Id $viteProcess.Id -Force -ErrorAction SilentlyContinue
  }
  if ($apiProcess -and -not $apiProcess.HasExited) {
    Stop-Process -Id $apiProcess.Id -Force -ErrorAction SilentlyContinue
  }
  $env:E2E_ACCOUNT_PASSWORD = $null
}

exit $exitCode
