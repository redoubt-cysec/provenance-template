$ErrorActionPreference = 'Stop'

$packageName = 'provenance-demo'
$toolsDir = "$(Split-Path -parent $MyInvocation.MyCommand.Definition)"
$url = 'https://github.com/redoubt-cysec/provenance-template/releases/download/v0.1.0/provenance-demo.pyz'
$checksum = 'REPLACE_WITH_SHA256_FROM_RELEASE'
$checksumType = 'sha256'

# Download the .pyz file
$pyzFile = Join-Path $toolsDir 'provenance-demo.pyz'
Get-ChocolateyWebFile -PackageName $packageName `
                      -FileFullPath $pyzFile `
                      -Url $url `
                      -Checksum $checksum `
                      -ChecksumType $checksumType

# Create a wrapper batch file
$batFile = Join-Path $toolsDir 'provenance-demo.bat'
@"
@echo off
python "%~dp0provenance-demo.pyz" %*
"@ | Out-File -FilePath $batFile -Encoding ASCII

# Add to PATH
Install-ChocolateyPath -PathToInstall $toolsDir -PathType 'User'

Write-Host "Provenance Demo has been installed successfully!"
Write-Host "Run 'provenance-demo --version' to verify installation"
Write-Host "Run 'provenance-demo verify' to validate security attestations"
