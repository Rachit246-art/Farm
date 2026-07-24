$html = [System.IO.File]::ReadAllText("d:\farm\index.html")

$target1 = '<meta content="Own a Luxury Sustainable Farmhouse — Kamala Infra" property="og:title"/>'
$repl1 = '<meta content="Own a Luxury Sustainable Farmhouse — Skygate" property="og:title"/>'
$html = $html.Replace($target1, $repl1)

$target2 = '<meta content="Own a Luxury Sustainable Farmhouse — Kamala Infra" name="twitter:title"/>'
$repl2 = '<meta content="Own a Luxury Sustainable Farmhouse — Skygate" name="twitter:title"/>'
$html = $html.Replace($target2, $repl2)

$target3 = '<meta content="Kamala Infra" property="og:site_name"/>'
$repl3 = '<meta content="Skygate" property="og:site_name"/>'
$html = $html.Replace($target3, $repl3)

$target4 = '<meta content="website" property="og:type"/>'
$repl4 = '<meta content="https://farm-gamma-one.vercel.app/images/logo.png" property="og:image"/><meta content="https://farm-gamma-one.vercel.app/images/logo.png" name="twitter:image"/><meta content="website" property="og:type"/>'
$html = $html.Replace($target4, $repl4)

[System.IO.File]::WriteAllText("d:\farm\index.html", $html)
