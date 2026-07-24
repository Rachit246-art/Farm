$html = [System.IO.File]::ReadAllText("d:\farm\index.html")

$targetFooter = '<footer style="background-color:#0D1B12;color:rgba(235,240,233,0.65);padding:2.5rem 0 calc(env(safe-area-inset-bottom) + 6rem);border-top:1px solid rgba(255,255,255,0.06)">'
$replFooter = '<footer style="background-color:#FFFFFF;color:#404040;padding:2.5rem 0 calc(env(safe-area-inset-bottom) + 6rem);border-top:1px solid rgba(0,0,0,0.08)">'
$html = $html.Replace($targetFooter, $replFooter)

$targetLink = '<a href="mailto:skygate26@gmail.com" style="color:rgba(235,240,233,0.7);text-decoration:none">'
$replLink = '<a href="mailto:skygate26@gmail.com" style="color:#404040;text-decoration:none">'
$html = $html.Replace($targetLink, $replLink)

[System.IO.File]::WriteAllText("d:\farm\index.html", $html)
