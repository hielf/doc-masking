Write-Host "Applying icon to Doc Masking.exe..." -ForegroundColor Green
Write-Host ""

# Check if rcedit is available
try {
    $rceditPath = Get-Command rcedit -ErrorAction Stop
    Write-Host "Found rcedit at: $($rceditPath.Source)" -ForegroundColor Yellow
} catch {
    Write-Host "rcedit not found. Please install it first:" -ForegroundColor Red
    Write-Host "npm install -g rcedit" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Apply the icon
Write-Host "Applying icon..." -ForegroundColor Yellow
& rcedit "Doc Masking.exe" --set-icon "icon.ico"

if ($LASTEXITCODE -eq 0) {
    Write-Host "Icon applied successfully!" -ForegroundColor Green
} else {
    Write-Host "Failed to apply icon." -ForegroundColor Red
}

Read-Host "Press Enter to exit"
