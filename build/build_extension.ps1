[CmdletBinding()]
param(
    [string]$BlenderExe = "D:\SteamLibrary\steamapps\common\Blender\blender.exe",
    [string]$SourceDir = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..")).Path,
    [string]$OutputDir = (Join-Path $PSScriptRoot "dist")
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path -LiteralPath $BlenderExe -PathType Leaf)) {
    throw "Blender executable not found: $BlenderExe"
}

$ResolvedSourceDir = (Resolve-Path -LiteralPath $SourceDir).Path

if (-not (Test-Path -LiteralPath $OutputDir -PathType Container)) {
    New-Item -ItemType Directory -Path $OutputDir | Out-Null
}

$ResolvedOutputDir = (Resolve-Path -LiteralPath $OutputDir).Path

Write-Host "Building Blender extension:"
Write-Host "  Source : $ResolvedSourceDir"
Write-Host "  Output : $ResolvedOutputDir"
Write-Host "  Blender: $BlenderExe"

& $BlenderExe --factory-startup --command extension build --source-dir $ResolvedSourceDir --output-dir $ResolvedOutputDir
if ($LASTEXITCODE -ne 0) {
    throw "Blender extension build failed with exit code $LASTEXITCODE"
}
