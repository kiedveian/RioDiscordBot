
Push-Location $PSScriptRoot
try {
    & .\RunBotLatest.ps1 test test
}
finally {
    Pop-Location
}
