
Push-Location $PSScriptRoot
try {
    & .\RunBotLatest.ps1 mei mei
}
finally {
    Pop-Location
}
