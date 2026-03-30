$ErrorActionPreference = "Stop"

Set-Location (Join-Path $PSScriptRoot "..")

function Stop-StaleBackendProcesses {
  $pids = netstat -ano |
    Select-String 'LISTENING' |
    Select-String ':5000' |
    ForEach-Object { ($_ -split '\s+')[-1] } |
    Where-Object { $_ -match '^\d+$' -and $_ -ne '0' } |
    Select-Object -Unique

  foreach ($id in $pids) {
    $proc = Get-Process -Id ([int]$id) -ErrorAction SilentlyContinue
    if ($proc -and $proc.ProcessName -like "python*") {
      Stop-Process -Id ([int]$id) -Force -ErrorAction SilentlyContinue
    }
  }
}

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

Stop-StaleBackendProcesses

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

if (Get-Command python3.11 -ErrorAction SilentlyContinue) {
  & python3.11 -m backend.app
  exit $LASTEXITCODE
}

$fallbackPython = Get-FallbackPythonPath
if ($fallbackPython) {
  & $fallbackPython -m backend.app
  exit $LASTEXITCODE
}

throw "Python was not found. Install Python 3.11+ (python/py/python3) or create .venv first."
