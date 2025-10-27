$ErrorActionPreference = 'Stop'

$packageName = 'redoubt'
$toolsDir = "$(Split-Path -parent $MyInvocation.MyCommand.Definition)"
$url = 'https://github.com/OWNER/REPO/releases/download/v0.1.0/redoubt-release-template.pyz'
$checksum = 'REPLACE_WITH_SHA256_FROM_RELEASE'
$checksumType = 'sha256'

# Download the .pyz file
$pyzFile = Join-Path $toolsDir 'redoubt-release-template.pyz'
Get-ChocolateyWebFile -PackageName $packageName `
                      -FileFullPath $pyzFile `
                      -Url $url `
                      -Checksum $checksum `
                      -ChecksumType $checksumType

# Create a wrapper batch file
$batFile = Join-Path $toolsDir 'redoubt.bat'
@"
@echo off
python "%~dp0redoubt-release-template.pyz" %*
"@ | Out-File -FilePath $batFile -Encoding ASCII

# Add to PATH
Install-ChocolateyPath -PathToInstall $toolsDir -PathType 'User'

Write-Host "Redoubt has been installed successfully!"
Write-Host "Run 'redoubt --version' to verify installation"
Write-Host "Run 'redoubt verify' to validate security attestations"
