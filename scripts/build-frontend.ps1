# Build frontend on Windows, then launch Docker
# Usage: .\scripts\build-frontend.ps1

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
$FrontendDir = Join-Path $Root "frontend"

Write-Host "=== YOLO Inspection — Frontend Build ===" -ForegroundColor Cyan

# Check Node.js
if (-not (Get-Command node -ErrorAction SilentlyContinue)) {
    Write-Host "ERROR: Node.js not found. Install from https://nodejs.org/" -ForegroundColor Red
    exit 1
}
Write-Host "Node.js: $(node --version)  npm: $(npm --version)" -ForegroundColor Green

Set-Location $FrontendDir

# Install packages (try mirror first, fall back to official)
Write-Host "`nInstalling npm packages..." -ForegroundColor Cyan
npm config set registry https://registry.npmmirror.com
npm install --no-audit --no-fund
if ($LASTEXITCODE -ne 0) {
    Write-Host "Mirror failed — retrying with official registry..." -ForegroundColor Yellow
    npm config set registry https://registry.npmjs.org
    npm install --no-audit --no-fund
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: npm install failed." -ForegroundColor Red
        exit 1
    }
}
npm config set registry https://registry.npmjs.org

# Build
Write-Host "`nBuilding production bundle..." -ForegroundColor Cyan
npm run build
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: npm run build failed." -ForegroundColor Red
    exit 1
}

Write-Host "`nFrontend built successfully -> frontend/dist/" -ForegroundColor Green

# Run Docker
Set-Location $Root
Write-Host "`nStarting Docker services..." -ForegroundColor Cyan
docker compose build --no-cache dashboard
docker compose up -d

Write-Host "`nDone! Open http://localhost:5173" -ForegroundColor Green
Write-Host "Login: engineer / engineer123  |  operator / operator123" -ForegroundColor Yellow
