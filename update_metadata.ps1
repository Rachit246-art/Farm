$html = Get-Content -Path index.html -Raw
$html = $html.Replace('<meta content="Own a Luxury Sustainable Farmhouse — Kamala Infra" property="og:title"/>', '<meta content="Own a Luxury Sustainable Farmhouse — Skygate" property="og:title"/>')
$html = $html.Replace('<meta content="Own a Luxury Sustainable Farmhouse — Kamala Infra" name="twitter:title"/>', '<meta content="Own a Luxury Sustainable Farmhouse — Skygate" name="twitter:title"/>')
$html = $html.Replace('<meta content="Kamala Infra" property="og:site_name"/>', '<meta content="Skygate" property="og:site_name"/>')
$html = $html.Replace('<meta content="website" property="og:type"/>', '<meta content="https://farm-gamma-one.vercel.app/skygate-metadata.png" property="og:image"/><meta content="https://farm-gamma-one.vercel.app/skygate-metadata.png" name="twitter:image"/><meta content="website" property="og:type"/>')
$html | Set-Content -Path index.html -NoNewline -Encoding UTF8
