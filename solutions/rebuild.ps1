param(
    [string]$Pac = "pac"
)
$ErrorActionPreference = "Stop"
Push-Location $PSScriptRoot
try {
    python -B .\tools\sync_reference.py
    if ($LASTEXITCODE -ne 0) { throw "Portable source compilation failed." }
    & $Pac solution pack --zipfile .\CorpNetSearchHubReference_1_0_0_0_unmanaged.zip --folder .\src --packagetype Unmanaged --errorlevel Warning
    if ($LASTEXITCODE -ne 0) { throw "Supported solution packing failed." }
    & $Pac solution create-settings --solution-zip .\CorpNetSearchHubReference_1_0_0_0_unmanaged.zip --settings-file .\deployment-settings.template.json
    if ($LASTEXITCODE -ne 0) { throw "Deployment settings generation failed." }
    python -B -m unittest discover -s .\tests -v
    if ($LASTEXITCODE -ne 0) { throw "Solution reference validation failed." }
    python -B .\tools\record_build.py
    if ($LASTEXITCODE -ne 0) { throw "Local build inventory failed." }
} finally {
    Pop-Location
}
