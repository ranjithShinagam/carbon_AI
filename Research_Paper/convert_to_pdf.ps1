$word = New-Object -ComObject Word.Application
$word.Visible = $false
try {
    $docxPath = "d:\CarbonAI_3\Research_Paper\Research_Paper_Final.docx"
    $pdfPath = "d:\CarbonAI_3\Research_Paper\Research_Paper_Final.pdf"
    
    Write-Host "Opening document: $docxPath"
    $doc = $word.Documents.Open($docxPath)
    
    Write-Host "Exporting to PDF: $pdfPath"
    # 17 corresponds to wdFormatPDF
    $doc.SaveAs([ref]$pdfPath, [ref]17)
    $doc.Close()
    Write-Host "SUCCESS: PDF created successfully!"
}
catch {
    Write-Error $_
}
finally {
    $word.Quit()
    [System.Runtime.Interopservices.Marshal]::ReleaseComObject($word) | Out-Null
}
