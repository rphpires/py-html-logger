Write-Host "Starting deployment process..." -ForegroundColor Green

# 1. Remove dist and py_html_logger.egg-info folders
Write-Host "Cleaning up previous builds..." -ForegroundColor Yellow
Remove-Item -Recurse -Force -ErrorAction SilentlyContinue dist, src\py_html_logger.egg-info
Write-Host "Cleanup completed!" -ForegroundColor Green

# 2. Execute python -m build with real-time output
Write-Host "Building package..." -ForegroundColor Green

python -m build
if ($LASTEXITCODE -ne 0) {
    Write-Host "Build failed!" -ForegroundColor Red
    exit 1
}

# 3. Execute twine upload dist/* with real-time output
Write-Host "Uploading package to PyPI..." -ForegroundColor Green

twine upload dist/*
if ($LASTEXITCODE -ne 0) {
    Write-Host "Upload failed!" -ForegroundColor Red
    exit 1
}

Write-Host "Deployment process completed successfully!" -ForegroundColor Green