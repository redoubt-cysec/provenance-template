$ErrorActionPreference = 'Stop'

$toolsDir = "$(Split-Path -parent $MyInvocation.MyCommand.Definition)"

# Remove files
Remove-Item -Path (Join-Path $toolsDir 'provenance-demo.pyz') -Force -ErrorAction SilentlyContinue
Remove-Item -Path (Join-Path $toolsDir 'provenance-demo.bat') -Force -ErrorAction SilentlyContinue

Write-Host "Provenance Demo has been uninstalled successfully!"
