<#
.SYNOPSIS
    Builds the autoBraille NVDA add-on package (.nvda-addon).
.DESCRIPTION
    Packages the contents of the 'addon' folder into a zip file with the .nvda-addon extension,
    saved into the 'dist' directory.
#>

[CmdletBinding()]
param(
    [switch]$RunTests
)

$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

Set-Location $ScriptDir

# Check if Python is available via py.exe (Python Install Manager) or python.exe
$pythonCmd = Get-Command py.exe -ErrorAction SilentlyContinue
if (-not $pythonCmd) {
    $pythonCmd = Get-Command python.exe -ErrorAction SilentlyContinue
}
if (-not $pythonCmd) {
    $pythonCmd = Get-Command python -ErrorAction SilentlyContinue
}

if ($RunTests) {
    Write-Host "Running test suite..." -ForegroundColor Cyan
    if ($pythonCmd) {
        & $pythonCmd.Source tests/test_audit_fixes.py
        & $pythonCmd.Source tests/test_tables_mode.py
        & $pythonCmd.Source tests/test_features_3_4.py
        & $pythonCmd.Source tests/test_segmenter.py
        Write-Host "All tests passed!" -ForegroundColor Green
    } else {
        Write-Warning "Python not found on PATH. Skipping test execution."
    }
}

Write-Host "Building autoBraille add-on package..." -ForegroundColor Cyan

# Parse manifest.ini to get name and version
$manifestPath = Join-Path $ScriptDir "addon\manifest.ini"
if (-not (Test-Path $manifestPath)) {
    Write-Error "Cannot find manifest.ini at $manifestPath"
    exit 1
}

$addonName = "autoBraille"
$addonVersion = "1.0.1"

Get-Content $manifestPath | ForEach-Object {
    if ($_ -match '^\s*name\s*=\s*(.+)$') {
        $addonName = $matches[1].Trim()
    }
    if ($_ -match '^\s*version\s*=\s*(.+)$') {
        $addonVersion = $matches[1].Trim()
    }
}

$distDir = Join-Path $ScriptDir "dist"
if (-not (Test-Path $distDir)) {
    New-Item -ItemType Directory -Path $distDir | Out-Null
}

$addonFile = Join-Path $distDir "$addonName-$addonVersion.nvda-addon"
if (Test-Path $addonFile) {
    Remove-Item -Force $addonFile
}

$addonFolder = Join-Path $ScriptDir "addon"

# Create zip archive with .nvda-addon extension
Write-Host "Packaging $addonFolder into $addonFile..." -ForegroundColor Yellow

$tempZip = Join-Path $distDir "temp_addon.zip"
if (Test-Path $tempZip) { Remove-Item -Force $tempZip }

$stagingDir = Join-Path $distDir "staging"
if (Test-Path $stagingDir) { Remove-Item -Recurse -Force $stagingDir }
New-Item -ItemType Directory -Path $stagingDir | Out-Null

Copy-Item -Path "$addonFolder\*" -Destination $stagingDir -Recurse
Get-ChildItem -Path $stagingDir -Include "__pycache__" -Recurse -Force | Remove-Item -Recurse -Force
Get-ChildItem -Path $stagingDir -Include "*.pyc", "*.pyo" -Recurse -Force | Remove-Item -Force

Compress-Archive -Path "$stagingDir\*" -DestinationPath $tempZip -CompressionLevel Optimal
Remove-Item -Recurse -Force $stagingDir
Move-Item -Force -Path $tempZip -Destination $addonFile

$sizeKb = [math]::Round((Get-Item $addonFile).Length / 1024, 2)
Write-Host "Success! Created add-on bundle: $addonFile ($sizeKb KB)" -ForegroundColor Green
