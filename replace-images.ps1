$root = "b-i"
$imgFolder = Join-Path $root "images"

# Собираем список webp
$webpFiles = Get-ChildItem $imgFolder -Filter *.webp | ForEach-Object {
    $_.BaseName
}

# Обрабатываем все .htm
Get-ChildItem $root -Filter *.htm | ForEach-Object {
    $file = $_.FullName
    $content = Get-Content $file -Raw

    $original = $content

    # Ищем jpg/png
    foreach ($ext in @("jpg","jpeg","png")) {
        foreach ($img in Get-ChildItem $imgFolder -Filter "*.$ext") {
            $name = $img.BaseName

            # Если есть webp — заменяем
            if ($webpFiles -contains $name) {
                $old = "images/$name.$ext"
                $new = "images/$name.webp"

                $content = $content -replace [regex]::Escape($old), $new
            }
        }
    }

    # Если были изменения — сохраняем
    if ($content -ne $original) {
        Copy-Item $file "$file.bak" -Force
        Set-Content $file $content -Encoding UTF8
        Write-Host "Обновлён: $file"
    } else {
        Write-Host "Без изменений: $file"
    }
}
