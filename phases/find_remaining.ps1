$plFiles = Get-Content -Path C:\poligon\LLM_Traning\phases\pl_files_utf8.txt
$remaining = @()
foreach ($file in $plFiles) {
    if (-not [string]::IsNullOrWhiteSpace($file)) {
        $proFile = $file -replace '\.md$', '_pro.md'
        if (-not (Test-Path -Path $proFile)) {
            $remaining += $file
        }
    }
}
$remaining | Out-File -FilePath C:\poligon\LLM_Traning\phases\remaining.txt -Encoding utf8
Write-Output "Remaining count: $($remaining.Count)"
