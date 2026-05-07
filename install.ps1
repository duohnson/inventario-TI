$ErrorActionPreference = "Stop"

$sourceDir = Join-Path $PSScriptRoot "dist\Inventario TI"
$destDir = Join-Path $env:APPDATA "Inventario TI App"

Write-Host "Copiando a $destDir..."
if (Test-Path $destDir) {
    Remove-Item -Path "$destDir\*" -Recurse -Force
} else {
    New-Item -ItemType Directory -Force -Path $destDir | Out-Null
}

Copy-Item -Path "$sourceDir\*" -Destination $destDir -Recurse -Force

$desktop = [Environment]::GetFolderPath("Desktop")
$shortcutPath = Join-Path $desktop "Inventario TI.lnk"
$targetPath = Join-Path $destDir "Inventario TI.exe"

Write-Host "Creando acceso directo en el Escritorio..."
$wshShell = New-Object -ComObject WScript.Shell
$shortcut = $wshShell.CreateShortcut($shortcutPath)
$shortcut.TargetPath = $targetPath
$shortcut.WorkingDirectory = $destDir
$shortcut.IconLocation = "$targetPath, 0"
$shortcut.Save()

Write-Host "Instalación completada exitosamente!"
