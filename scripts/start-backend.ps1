$ErrorActionPreference = "Stop"

Set-Location (Join-Path $PSScriptRoot "..")

function Get-FallbackPythonPath {
  $candidates = @(
    "$env:LOCALAPPDATA\Programs\Python\Python*\python.exe",
    "$env:ProgramFiles\Python*\python.exe",
    "$env:ProgramFiles\Python*\python3*.exe"
  )

  foreach ($pattern in $candidates) {
    $match = Get-ChildItem -Path $pattern -ErrorAction SilentlyContinue | Sort-Object FullName -Descending | Select-Object -First 1
    if ($match -and (Test-Path $match.FullName)) {
      return $match.FullName
    }
  }

  return $null
}

$venvPython = Join-Path (Get-Location) ".venv\Scripts\python.exe"
if (Test-Path $venvPython) {
  & $venvPython -m backend.app
  exit $LASTEXITCODE
}

if (Get-Command py -ErrorAction SilentlyContinue) {
  & py -3 -m backend.app
  exit $LASTEXITCODE
}

if (Get-Command python -ErrorAction SilentlyContinue) {
  & python -m backend.app
  exit $LASTEXITCODE
}

if (Get-Command python3 -ErrorAction SilentlyContinue) {
  & python3 -m backend.app
  exit $LASTEXITCODE
}

$fallbackPython = Get-FallbackPythonPath
if ($fallbackPython) {
  & $fallbackPython -m backend.app
  exit $LASTEXITCODE
}

throw "Python was not found. Install Python 3.11+ (python/py/python3) or create .venv first."
