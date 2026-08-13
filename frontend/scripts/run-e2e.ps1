$ErrorActionPreference = "Stop"
$server = Start-Process -FilePath node `
  -ArgumentList @("./node_modules/vite/bin/vite.js", "preview", "--host", "127.0.0.1", "--port", "4173") `
  -WorkingDirectory (Get-Location) -PassThru -WindowStyle Hidden
try {
  Start-Sleep -Seconds 2
  npx playwright test
  $exitCode = $LASTEXITCODE
} finally {
  Stop-Process -Id $server.Id -Force -ErrorAction SilentlyContinue
}
exit $exitCode
