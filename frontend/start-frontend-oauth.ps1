$ErrorActionPreference = "SilentlyContinue"

$port = 5300
$pids = @()

$connections = Get-NetTCPConnection -LocalPort $port
if ($connections) {
    $pids += $connections | Select-Object -ExpandProperty OwningProcess -Unique
}

if (-not $pids -or $pids.Count -eq 0) {
    $netstatLines = netstat -ano | Select-String ":$port"
    foreach ($line in $netstatLines) {
        $parts = ($line.ToString() -split "\s+") | Where-Object { $_ -ne "" }
        if ($parts.Count -ge 5) {
            $pidCandidate = $parts[-1]
            if ($pidCandidate -match "^\d+$") {
                $pids += [int]$pidCandidate
            }
        }
    }
}

$pids = $pids | Where-Object { $_ -and $_ -ne 0 } | Select-Object -Unique
foreach ($processId in $pids) {
    Stop-Process -Id $processId -Force
}

Start-Sleep -Milliseconds 500

$ErrorActionPreference = "Stop"
npm run dev
