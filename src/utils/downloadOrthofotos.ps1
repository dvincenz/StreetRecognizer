$baseUrl = 'https://maps.zh.ch/download/orthofoto/sommer/2014/rgb/jpeg/'

$allUrls = (Invoke-WebRequest -Uri $baseUrl).Links


foreach ($url in $allUrls) {
    $outFile = $url.outerText
    Invoke-WebRequest -Uri "$($baseUrl)$($outFile)" -OutFile "$outFile"
}
