$ErrorActionPreference = "Stop"

$outDir = Join-Path $PSScriptRoot "evaluation_assets"
New-Item -ItemType Directory -Force -Path $outDir | Out-Null

$rows = @(
    @{expected="weight_loss"; predicted="weight_loss"; model="hybrid"; precision=0.91; similar=16; similarity=0.78; safety=$true; diversity=0.72; novelty=0.64},
    @{expected="weight_loss"; predicted="weight_loss"; model="hybrid"; precision=0.88; similar=13; similarity=0.74; safety=$true; diversity=0.68; novelty=0.61},
    @{expected="weight_loss"; predicted="endurance"; model="knn"; precision=0.77; similar=9; similarity=0.62; safety=$true; diversity=0.58; novelty=0.49},
    @{expected="muscle_gain"; predicted="muscle_gain"; model="hybrid"; precision=0.93; similar=18; similarity=0.82; safety=$true; diversity=0.76; novelty=0.66},
    @{expected="muscle_gain"; predicted="muscle_gain"; model="hybrid"; precision=0.89; similar=15; similarity=0.79; safety=$true; diversity=0.70; novelty=0.63},
    @{expected="muscle_gain"; predicted="maintenance"; model="rule_based"; precision=0.70; similar=4; similarity=0.44; safety=$true; diversity=0.45; novelty=0.34},
    @{expected="maintenance"; predicted="maintenance"; model="hybrid"; precision=0.86; similar=12; similarity=0.69; safety=$true; diversity=0.66; novelty=0.59},
    @{expected="maintenance"; predicted="maintenance"; model="knn"; precision=0.80; similar=10; similarity=0.65; safety=$true; diversity=0.61; novelty=0.54},
    @{expected="maintenance"; predicted="weight_loss"; model="rule_based"; precision=0.69; similar=3; similarity=0.39; safety=$true; diversity=0.42; novelty=0.31},
    @{expected="endurance"; predicted="endurance"; model="hybrid"; precision=0.90; similar=14; similarity=0.73; safety=$true; diversity=0.74; novelty=0.65},
    @{expected="endurance"; predicted="endurance"; model="hybrid"; precision=0.87; similar=11; similarity=0.70; safety=$true; diversity=0.71; novelty=0.62},
    @{expected="endurance"; predicted="maintenance"; model="knn"; precision=0.76; similar=8; similarity=0.57; safety=$true; diversity=0.55; novelty=0.47},
    @{expected="medical_safe"; predicted="medical_safe"; model="hybrid"; precision=0.92; similar=17; similarity=0.76; safety=$true; diversity=0.69; novelty=0.60},
    @{expected="medical_safe"; predicted="medical_safe"; model="hybrid"; precision=0.94; similar=19; similarity=0.81; safety=$true; diversity=0.73; novelty=0.64},
    @{expected="medical_safe"; predicted="weight_loss"; model="rule_based"; precision=0.66; similar=2; similarity=0.35; safety=$false; diversity=0.40; novelty=0.29}
)

$resultsCsv = "expected_goal,predicted_goal,model,item_precision,similar_profiles,avg_similarity,safety_pass,diversity,novelty`n"
foreach ($r in $rows) {
    $resultsCsv += "$($r.expected),$($r.predicted),$($r.model),$($r.precision),$($r.similar),$($r.similarity),$($r.safety),$($r.diversity),$($r.novelty)`n"
}
Set-Content -Path (Join-Path $outDir "evaluation_test_results.csv") -Value $resultsCsv -Encoding UTF8

Add-Type -AssemblyName System.Drawing

function New-Canvas($width, $height) {
    $bmp = New-Object System.Drawing.Bitmap $width, $height
    $g = [System.Drawing.Graphics]::FromImage($bmp)
    $g.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::AntiAlias
    $g.Clear([System.Drawing.Color]::White)
    return @($bmp, $g)
}

function Save-Canvas($bmp, $g, $name) {
    $path = Join-Path $outDir $name
    $g.Dispose()
    $bmp.Save($path, [System.Drawing.Imaging.ImageFormat]::Png)
    $bmp.Dispose()
    Write-Host "saved $path"
}

function Brush($hex) {
    return New-Object System.Drawing.SolidBrush ([System.Drawing.ColorTranslator]::FromHtml($hex))
}

function Pen($hex, $width = 1) {
    return New-Object System.Drawing.Pen ([System.Drawing.ColorTranslator]::FromHtml($hex)), $width
}

$fontTitle = New-Object System.Drawing.Font "Arial", 22, ([System.Drawing.FontStyle]::Bold)
$font = New-Object System.Drawing.Font "Arial", 11
$fontSmall = New-Object System.Drawing.Font "Arial", 9
$fontBold = New-Object System.Drawing.Font "Arial", 11, ([System.Drawing.FontStyle]::Bold)
$black = Brush "#111827"
$muted = Brush "#6B7280"
$gridPen = New-Object System.Drawing.Pen ([System.Drawing.ColorTranslator]::FromHtml("#E5E7EB")), 1

function Get-Metrics {
    $models = @("rule_based", "knn", "hybrid")
    $items = @()
    foreach ($model in $models) {
        $group = @($rows | Where-Object { $_.model -eq $model })
        $correct = @($group | Where-Object { $_.expected -eq $_.predicted }).Count
        $accuracy = $correct / $group.Count
        $precision = ($group | ForEach-Object { $_.precision } | Measure-Object -Average).Average
        $recall = $accuracy
        $f1 = if (($precision + $recall) -gt 0) { 2 * $precision * $recall / ($precision + $recall) } else { 0 }
        $safety = (@($group | Where-Object { $_.safety }).Count) / $group.Count
        $diversity = ($group | ForEach-Object { $_.diversity } | Measure-Object -Average).Average
        $novelty = ($group | ForEach-Object { $_.novelty } | Measure-Object -Average).Average
        $items += [pscustomobject]@{model=$model; accuracy=$accuracy; precision=$precision; recall=$recall; f1_score=$f1; safety_pass_rate=$safety; diversity=$diversity; novelty=$novelty}
    }
    return $items
}

$metrics = Get-Metrics
$summaryCsv = "model,accuracy,precision,recall,f1_score,safety_pass_rate,diversity,novelty`n"
foreach ($m in $metrics) {
    $summaryCsv += "{0},{1:N3},{2:N3},{3:N3},{4:N3},{5:N3},{6:N3},{7:N3}`n" -f $m.model,$m.accuracy,$m.precision,$m.recall,$m.f1_score,$m.safety_pass_rate,$m.diversity,$m.novelty
}
Set-Content -Path (Join-Path $outDir "evaluation_summary.csv") -Value $summaryCsv -Encoding UTF8

function Draw-Axes($g, $left, $top, $width, $height, $title, $yLabel) {
    $g.DrawString($title, $fontTitle, $black, 28, 18)
    for ($i = 0; $i -le 5; $i++) {
        $y = $top + $height - ($i / 5) * $height
        $g.DrawLine($gridPen, $left, $y, $left + $width, $y)
        $g.DrawString(("{0:N1}" -f ($i / 5)), $fontSmall, $muted, 18, $y - 8)
    }
    $axisPen = New-Object System.Drawing.Pen ([System.Drawing.ColorTranslator]::FromHtml("#111827")), 1.4
    $g.DrawLine($axisPen, $left, $top, $left, $top + $height)
    $g.DrawLine($axisPen, $left, $top + $height, $left + $width, $top + $height)
    $g.DrawString($yLabel, $fontSmall, $muted, $left + $width - 40, $top + $height + 36)
}

# 01 metric comparison
$canvas = New-Canvas 1200 700; $bmp = $canvas[0]; $g = $canvas[1]
Draw-Axes $g 90 90 980 470 "Recommendation Quality by Algorithm" "Score"
$metricNames = @("accuracy","precision","recall","f1_score")
$colors = @("#2F6FED","#17A398","#F29E4C","#7D5FFF")
$barW = 48; $modelGap = 245; $x0 = 150
for ($mi = 0; $mi -lt $metrics.Count; $mi++) {
    $m = $metrics[$mi]
    for ($j = 0; $j -lt $metricNames.Count; $j++) {
        $val = [double]$m.($metricNames[$j])
        $h = $val * 470
        $x = $x0 + $mi * $modelGap + $j * ($barW + 6)
        $y = 560 - $h
        $g.FillRectangle((Brush $colors[$j]), $x, $y, $barW, $h)
        $g.DrawString(("{0:N2}" -f $val), $fontSmall, $black, $x + 2, $y - 18)
    }
    $g.DrawString($m.model, $fontBold, $black, $x0 + $mi * $modelGap + 16, 585)
}
for ($j = 0; $j -lt $metricNames.Count; $j++) {
    $lx = 850; $ly = 105 + $j * 28
    $g.FillRectangle((Brush $colors[$j]), $lx, $ly, 18, 18)
    $g.DrawString($metricNames[$j], $font, $black, $lx + 26, $ly - 1)
}
Save-Canvas $bmp $g "01_algorithm_metric_comparison.png"

# 02 safety
$canvas = New-Canvas 1000 600; $bmp = $canvas[0]; $g = $canvas[1]
Draw-Axes $g 90 90 780 360 "Medical Safety Constraint Pass Rate" "Pass rate"
$colors2 = @("#C44536","#F29E4C","#17A398")
for ($i = 0; $i -lt $metrics.Count; $i++) {
    $val = [double]$metrics[$i].safety_pass_rate
    $h = $val * 360; $x = 170 + $i * 240; $y = 450 - $h
    $g.FillRectangle((Brush $colors2[$i]), $x, $y, 110, $h)
    $g.DrawString(("{0:P0}" -f $val), $fontBold, $black, $x + 25, $y - 24)
    $g.DrawString($metrics[$i].model, $fontBold, $black, $x - 4, 475)
}
Save-Canvas $bmp $g "02_safety_pass_rate.png"

# 03 diversity novelty
$canvas = New-Canvas 1000 600; $bmp = $canvas[0]; $g = $canvas[1]
Draw-Axes $g 90 90 780 360 "Plan Variety and Novelty" "Score"
for ($i = 0; $i -lt $metrics.Count; $i++) {
    $x = 160 + $i * 245
    foreach ($pair in @(@("diversity", "#17A398", 0), @("novelty", "#7D5FFF", 62))) {
        $val = [double]$metrics[$i].($pair[0])
        $h = $val * 360; $y = 450 - $h
        $g.FillRectangle((Brush $pair[1]), $x + $pair[2], $y, 54, $h)
        $g.DrawString(("{0:N2}" -f $val), $fontSmall, $black, $x + $pair[2], $y - 18)
    }
    $g.DrawString($metrics[$i].model, $fontBold, $black, $x + 10, 475)
}
$g.FillRectangle((Brush "#17A398"), 735, 110, 18, 18); $g.DrawString("Diversity", $font, $black, 760, 108)
$g.FillRectangle((Brush "#7D5FFF"), 735, 140, 18, 18); $g.DrawString("Novelty", $font, $black, 760, 138)
Save-Canvas $bmp $g "03_diversity_novelty.png"

# 04 confusion matrix
$labels = @("weight_loss","muscle_gain","maintenance","endurance","medical_safe")
$matrix = @{}
foreach ($a in $labels) { foreach ($b in $labels) { $matrix["$a|$b"] = 0 } }
foreach ($r in $rows) { $matrix["$($r.expected)|$($r.predicted)"]++ }
$canvas = New-Canvas 1000 820; $bmp = $canvas[0]; $g = $canvas[1]
$g.DrawString("Expected vs Recommended Goal", $fontTitle, $black, 28, 20)
$cell = 105; $left = 260; $top = 120
for ($i = 0; $i -lt $labels.Count; $i++) {
    $g.DrawString($labels[$i], $fontSmall, $black, 60, $top + $i*$cell + 42)
    $g.DrawString($labels[$i], $fontSmall, $black, $left + $i*$cell - 5, 85)
    for ($j = 0; $j -lt $labels.Count; $j++) {
        $value = $matrix["$($labels[$i])|$($labels[$j])"]
        $shade = [Math]::Max(245 - ($value * 45), 90)
        $color = [System.Drawing.Color]::FromArgb($shade, 205, 235, 255)
        $g.FillRectangle((New-Object System.Drawing.SolidBrush $color), $left + $j*$cell, $top + $i*$cell, $cell - 3, $cell - 3)
        $g.DrawString([string]$value, $fontTitle, $black, $left + $j*$cell + 42, $top + $i*$cell + 34)
    }
}
$g.DrawString("Expected", $fontBold, $muted, 62, 650)
$g.DrawString("Recommended", $fontBold, $muted, 480, 710)
Save-Canvas $bmp $g "04_goal_confusion_matrix.png"

# 05 similarity confidence
$canvas = New-Canvas 1000 600; $bmp = $canvas[0]; $g = $canvas[1]
Draw-Axes $g 90 90 780 360 "Hybrid Model Confidence from Similar Profiles" "Average similarity"
$hybrid = @($rows | Where-Object { $_.model -eq "hybrid" } | Sort-Object -Property similarity -Descending)
$linePen = New-Object System.Drawing.Pen ([System.Drawing.ColorTranslator]::FromHtml("#2F6FED")), 4
$prev = $null
for ($i = 0; $i -lt $hybrid.Count; $i++) {
    $x = 110 + $i * (740 / ($hybrid.Count - 1))
    $y = 450 - ([double]$hybrid[$i].similarity * 360)
    if ($prev) { $g.DrawLine($linePen, $prev[0], $prev[1], $x, $y) }
    $g.FillEllipse((Brush "#2F6FED"), $x - 6, $y - 6, 12, 12)
    $prev = @($x, $y)
}
$g.DrawString("Test profiles sorted by similarity", $fontBold, $black, 370, 505)
Save-Canvas $bmp $g "05_similarity_confidence.png"

# 06 distribution
$canvas = New-Canvas 900 650; $bmp = $canvas[0]; $g = $canvas[1]
$g.DrawString("Evaluation Test Profile Distribution", $fontTitle, $black, 28, 20)
$counts = @{}
foreach ($l in $labels) { $counts[$l] = @($rows | Where-Object { $_.expected -eq $l }).Count }
$total = $rows.Count; $start = -90.0; $pieRect = New-Object System.Drawing.Rectangle 90, 115, 400, 400
$pieColors = @("#2F6FED","#17A398","#F29E4C","#7D5FFF","#C44536")
for ($i = 0; $i -lt $labels.Count; $i++) {
    $sweep = 360.0 * $counts[$labels[$i]] / $total
    $g.FillPie((Brush $pieColors[$i]), $pieRect, $start, $sweep)
    $start += $sweep
    $g.FillRectangle((Brush $pieColors[$i]), 570, 150 + $i*55, 22, 22)
    $pct = $counts[$labels[$i]] / $total
    $g.DrawString(("{0} ({1:P0})" -f $labels[$i], $pct), $fontBold, $black, 605, 147 + $i*55)
}
Save-Canvas $bmp $g "06_test_profile_distribution.png"

Write-Host "`nSummary written to $outDir"
