[CmdletBinding()]
param(
    [string]$BlenderExe = "D:\SteamLibrary\steamapps\common\Blender\blender.exe",
    [string]$SourceDir = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..")).Path
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path -LiteralPath $BlenderExe -PathType Leaf)) {
    throw "Blender executable not found: $BlenderExe"
}

$ResolvedSourceDir = (Resolve-Path -LiteralPath $SourceDir).Path

Write-Host "Validating Blender extension source:"
Write-Host "  Source : $ResolvedSourceDir"
Write-Host "  Blender: $BlenderExe"

& $BlenderExe --factory-startup --command extension validate $ResolvedSourceDir
if ($LASTEXITCODE -ne 0) {
    throw "Blender extension validation failed with exit code $LASTEXITCODE"
}
