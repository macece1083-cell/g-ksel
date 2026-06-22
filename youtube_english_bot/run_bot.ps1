param(
    [ValidateSet("A1", "A2", "B1", "B2", "C1", "C2")]
    [string]$Level = "A2",
    [string]$Topic = "grammar",
    [switch]$Upload,
    [switch]$NoImages
)

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

    throw "Python bulunamadi. Once setup.ps1 calistirin veya Python kurun."
}

$argsList = @("main.py", "--level", $Level, "--topic", $Topic)
if ($Upload) {
    $argsList += "--upload"
}
if ($NoImages) {
    $argsList += "--no-images"
}

& (Get-PythonCommand) @argsList
