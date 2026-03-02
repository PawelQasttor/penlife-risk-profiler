# PowerShell script to run text fitting tests with virtual environment

Write-Host "Activating virtual environment..." -ForegroundColor Cyan
& ..\venv\Scripts\Activate.ps1

Write-Host ""
Write-Host "Running text fitting tests..." -ForegroundColor Cyan
Write-Host ""

python test_text_fitting.py

Write-Host ""
Write-Host "Tests completed!" -ForegroundColor Green
Write-Host "Check the output folder for generated PDFs." -ForegroundColor Yellow
Write-Host ""

Read-Host "Press Enter to exit"
