$report = Join-Path $PSScriptRoot 'html_report.txt'
$log = Join-Path $PSScriptRoot 'fix_html_log.txt'
if (-not (Test-Path $report)) { Write-Error "Report file not found: $report"; exit 1 }
$paths = Get-Content -LiteralPath $report | Where-Object { $_ -like 'FILE:*' } | ForEach-Object { $_.Substring(6).Trim() }
$ampRegex = [regex] '&(?!(?:nbsp|lt|gt|amp|quot|apos|#\d+|#x[0-9A-Fa-f]+);)'
$xCompatRegex = [regex] '<meta\s+http-equiv="X-UA-Compatible"[^>]*>'
$viewportRegex = [regex] '<meta\s+name="viewport"[^>]*>'
function RemoveDuplicateMeta($text, $regex) {
    $first = $null
    $result = ''
    $lastIndex = 0
    foreach ($match in $regex.Matches($text)) {
        if (-not $first) {
            $first = $true
            continue
        }
        $result += $text.Substring($lastIndex, $match.Index - $lastIndex)
        $lastIndex = $match.Index + $match.Length
    }
    if ($lastIndex -gt 0) {
        $result += $text.Substring($lastIndex)
        return $result
    }
    return $text
}
function NormalizeHtmlWithCom($text) {
    try {
        $ie = New-Object -ComObject 'InternetExplorer.Application'
        $ie.Visible = $false
        $doc = $ie.Document
        $doc.open()
        $doc.write($text)
        $doc.close()
        $output = $doc.documentElement.outerHTML
        $ie.Quit()
        return $output
    } catch {
        Write-Host "COM normalization failed: $($_.Exception.Message)"
        return $null
    }
}

Remove-Item -LiteralPath $log -ErrorAction SilentlyContinue
foreach ($path in $paths) {
    if (-not (Test-Path $path)) {
        Add-Content -LiteralPath $log "MISSING: $path"
        continue
    }
    $text = Get-Content -Raw -Encoding utf8 -LiteralPath $path
    $orig = $text
    $changed = $false
    if ($ampRegex.IsMatch($text)) {
        $text = $ampRegex.Replace($text, '&amp;')
        $changed = $true
        Add-Content -LiteralPath $log "AMP fixed: $path"
    }
    $old = $text
    if ($xCompatRegex.Matches($text).Count -gt 1) {
        $text = RemoveDuplicateMeta $text $xCompatRegex
        if ($text -ne $old) { $changed = $true; Add-Content -LiteralPath $log "X-UA-Compatible duplicate removed: $path" }
    }
    $old = $text
    if ($viewportRegex.Matches($text).Count -gt 1) {
        $text = RemoveDuplicateMeta $text $viewportRegex
        if ($text -ne $old) { $changed = $true; Add-Content -LiteralPath $log "viewport duplicate removed: $path" }
    }
    $openCount = [regex]::Matches($text,'<a\b','IgnoreCase').Count
    $closeCount = [regex]::Matches($text,'</a>','IgnoreCase').Count
    if ($openCount -ne $closeCount -or $changed) {
        $normalized = NormalizeHtmlWithCom($text)
        if ($normalized) {
            $text = $normalized
            $changed = $true
            Add-Content -LiteralPath $log "COM normalized: $path"
        } else {
            Add-Content -LiteralPath $log "Skipped COM normalize: $path"
        }
    }
    if ($changed -and $text -ne $orig) {
        Set-Content -LiteralPath $path -Encoding utf8 -Value $text
        Add-Content -LiteralPath $log "SAVED: $path"
    }
}
Add-Content -LiteralPath $log "Done."