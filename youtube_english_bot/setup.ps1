$ErrorActionPreference = "Stop"

function Get-PythonCommand {
    $python = Get-Command python -ErrorAction SilentlyContinue
    if ($python -and $python.Source -notlike "*WindowsApps*") {
        return $python.Source
    }

    $py = Get-Command py -ErrorAction SilentlyContinue
    if ($py) {
        return $py.Source
    }

    $bundled = "C:\Users\User\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
    if (Test-Path $bundled) {
        return $bundled
    }

    throw "Python bulunamadi. https://www.python.org/downloads/windows/ adresinden Python kurun."
}

$pythonExe = Get-PythonCommand
Write-Host "Python: $pythonExe"

& $pythonExe -m pip install -r requirements.txt

if (-not (Get-Command ffmpeg -ErrorAction SilentlyContinue)) {
    Write-Host "FFmpeg bulunamadi, WinGet ile kuruluyor..."
    winget install --id Gyan.FFmpeg -e --accept-package-agreements --accept-source-agreements
}

if (-not (Test-Path .env)) {
    Copy-Item .env.example .env
    Write-Host ".env olusturuldu."
}

Write-Host "Kurulum tamam."
