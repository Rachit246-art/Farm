$html = [System.IO.File]::ReadAllText("d:\farm\index.html")

$html = $html.Replace('Kamala Infra', 'Skygate')
$html = $html.Replace('kamalainfra', 'skygate')
$html = $html.Replace('Kamala', 'Skygate')

[System.IO.File]::WriteAllText("d:\farm\index.html", $html)

Copy-Item "d:\farm\images\logo.png" "d:\farm\favicon-logo.png" -Force
Copy-Item "d:\farm\images\logo.png" "d:\farm\logo-web.png" -Force
