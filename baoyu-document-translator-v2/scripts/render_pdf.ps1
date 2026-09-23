# Render DOCX -> PDF for rendered QA (v2 addendum).
# Usage: pwsh -File render_pdf.ps1 -Docx path\to\file.docx [-Pdf out.pdf]
# Tries Word COM first (also proves the file is not schema-corrupt), then LibreOffice.
param(
  [Parameter(Mandatory=$true)][string]$Docx,
  [string]$Pdf = ""
)
if (-not $Pdf) { $Pdf = [System.IO.Path]::ChangeExtension($Docx, ".pdf") }
$ok = $false
try {
  $w = New-Object -ComObject Word.Application
  $w.Visible = $false; $w.DisplayAlerts = 0
  try {
    $d = $w.Documents.Open($Docx, $false, $true)
    # refresh TOC fields so stale WPS cached entries are replaced (SEQ results are
    # deliberately blanked by localize fields; caption numbers come from static text)
    try { foreach ($f in $d.Fields) { if ($f.Code.Text -match '^\s*TOC') { $f.Update() | Out-Null } } } catch { }
    $d.SaveAs2($Pdf, 17)
    $d.Close($false)
    $ok = $true
    Write-Output "WORD OK -> $Pdf"
  } finally { $w.Quit() }
} catch {
  Write-Output "Word COM failed: $($_.Exception.Message)"
}
if (-not $ok) {
  $cand = @("C:\Program Files\LibreOffice\program\soffice.exe", "soffice")
  foreach ($c in $cand) {
    try {
      & $c --headless --convert-to pdf --outdir ([System.IO.Path]::GetDirectoryName($Pdf)) $Docx | Out-Null
      if (Test-Path $Pdf) { $ok = $true; Write-Output "LIBREOFFICE OK -> $Pdf"; break }
    } catch { }
  }
}
if (-not $ok) { Write-Output "RENDER FAILED: install Word or LibreOffice"; exit 1 }
