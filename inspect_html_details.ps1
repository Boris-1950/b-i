$patterns = @(
    'avn\\dvm\\ogl_dvm.htm',
    'avn\\armi_polit.htm',
    'avn\\kachestvo.htm',
    'avn\\okr_ru.htm',
    'avn\\p_p.htm',
    'avn\\snesarev2.htm',
    'avn\\sozmat.htm',
    'avn\\sss1941.htm',
    'dvm\\ogl_dvm.htm',
    'galaxy\\galactik (3).htm',
    'galaxy\\galactik2 (3).htm',
    'gkg\\g3.htm',
    'gkg\\g5.htm',
    '041170.htm',
    '12_1993.htm',
    '1953.htm',
    '1972-gxz.htm',
    '1may.htm',
    '5sutok.htm',
    'am.htm',
    'analit.htm',
    'antifashist.htm',
    'bez_gor.htm',
    'b_vas.htm',
    'chro.htm',
    'ddd.htm',
    'dembel.htm',
    'duma.htm',
    'e_mail.htm',
    'fdgfg.htm',
    'feoktist.htm',
    'foto.htm',
    'gag_biog.htm',
    'gar.htm',
    'g_mir.htm',
    'hjd.htm',
    'Honor.html',
    'ii.htm',
    'kara.htm',
    'kursant.htm',
    'muchen.htm',
    'nashest.htm',
    'nb.htm',
    'ne_chleb.htm',
    'pollider.htm',
    'pppp.htm',
    'runaz.htm',
    'russia.htm',
    'schest.htm',
    'sistema.htm',
    'ssilki.htm',
    'sys.htm',
    'sz.htm',
    'values.htm',
    'vlasty.htm',
    'vor.htm',
    'yakovlev.htm'
)
$ampRegex = [regex] '&(?!(?:nbsp|lt|gt|amp|quot|apos|#\d+|#x[0-9A-Fa-f]+);)'
$linkRegex = [regex] '<a\b|</a>'
foreach($rel in $patterns){
    $path = Join-Path $PWD $rel
    if(-not (Test-Path $path)){
        Write-Host "MISSING: $rel"
        continue
    }
    $text = Get-Content -Raw -Encoding utf8 $path
    $amps = $ampRegex.Matches($text)
    $links = $linkRegex.Matches($text)
    $opens = [regex]::Matches($text, '<a\b', 'IgnoreCase').Count
    $closes = [regex]::Matches($text, '</a>', 'IgnoreCase').Count
    if($amps.Count -gt 0 -or $opens -ne $closes){
        Write-Host "=== $rel ==="
        Write-Host " raw_amp=$($amps.Count) opens=$opens closes=$closes"
        if($amps.Count -gt 0){
            foreach($m in $amps){
                $line = ($text.Substring(0, $m.Index) -split "`n").Count
                $snippet = $text.Substring([math]::Max(0,$m.Index-20), [math]::Min(80, $m.Length + 40)).Replace("`n", ' ')
                Write-Host "  RAW $line: $snippet"
            }
        }
        if($opens -ne $closes){
            Write-Host "  OPEN/CLOSE mismatch"
            $i=0
            foreach($m in [regex]::Matches($text, '<a\b|</a>', 'IgnoreCase')){
                $line = ($text.Substring(0, $m.Index) -split "`n").Count
                Write-Host "   $line: $($m.Value) -> $($text.Substring($m.Index, [math]::Min(120, $text.Length-$m.Index)).Split("`n")[0])"
                $i++
                if($i -ge 20){break}
            }
        }
        Write-Host
    }
}
