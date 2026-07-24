$html = [System.IO.File]::ReadAllText("d:\farm\index.html")
if ($html -match '(?i)(<footer[^>]*>.*?</footer>)') {
    [System.IO.File]::WriteAllText("d:\farm\footer.txt", $matches[1])
}
