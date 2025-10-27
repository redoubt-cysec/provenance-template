$ErrorActionPreference = 'Stop'

$toolsDir = "$(Split-Path -parent $MyInvocation.MyCommand.Definition)"

# Remove files
Remove-Item -Path (Join-Path $toolsDir 'redoubt-release-template.pyz') -Force -ErrorAction SilentlyContinue
Remove-Item -Path (Join-Path $toolsDir 'redoubt.bat') -Force -ErrorAction SilentlyContinue

Write-Host "Redoubt has been uninstalled successfully!"
