# VR-Therapist Server Setup Script
# This script helps set up the VR-Therapist server on Windows

Write-Host "==================================" -ForegroundColor Cyan
Write-Host "VR-Therapist Server Setup" -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan
Write-Host ""

# Check Python installation
Write-Host "Checking Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ Found: $pythonVersion" -ForegroundColor Green
    
    # Check Python version
    $version = python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')"
    if ([decimal]$version -lt 3.8) {
        Write-Host "✗ Python 3.8 or higher is required (found $version)" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "✗ Python not found. Please install Python 3.8 or higher." -ForegroundColor Red
    Write-Host "  Download from: https://www.python.org/downloads/" -ForegroundColor Yellow
    exit 1
}

Write-Host ""

# Check if in correct directory
if (-not (Test-Path "req.txt")) {
    Write-Host "✗ Error: req.txt not found" -ForegroundColor Red
    Write-Host "  Please run this script from the Server directory" -ForegroundColor Yellow
    exit 1
}

# Install dependencies
Write-Host "Installing Python dependencies..." -ForegroundColor Yellow
Write-Host "This may take several minutes..." -ForegroundColor Gray
Write-Host ""

try {
    python -m pip install --upgrade pip
    python -m pip install -r req.txt
    Write-Host "✓ Dependencies installed successfully" -ForegroundColor Green
} catch {
    Write-Host "✗ Failed to install dependencies" -ForegroundColor Red
    Write-Host "  Error: $_" -ForegroundColor Yellow
    exit 1
}

Write-Host ""

# Check for config.json
if (-not (Test-Path "config.json")) {
    Write-Host "Configuration file not found. Creating from example..." -ForegroundColor Yellow
    
    if (Test-Path "config.json.example") {
        Copy-Item "config.json.example" "config.json"
        Write-Host "✓ Created config.json from example" -ForegroundColor Green
        Write-Host ""
        Write-Host "⚠ IMPORTANT: You need to edit config.json with your Hugging Face token" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "Steps:" -ForegroundColor Cyan
        Write-Host "  1. Create account at https://huggingface.co/" -ForegroundColor White
        Write-Host "  2. Go to Settings → Access Tokens" -ForegroundColor White
        Write-Host "  3. Create new token with 'Read' permissions" -ForegroundColor White
        Write-Host "  4. Copy token to config.json" -ForegroundColor White
        Write-Host ""
        
        $response = Read-Host "Press Enter to open config.json for editing (or 'skip' to do it later)"
        if ($response -ne "skip") {
            notepad config.json
        }
    } else {
        Write-Host "✗ config.json.example not found" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "✓ config.json already exists" -ForegroundColor Green
}

Write-Host ""

# Verify configuration
Write-Host "Verifying configuration..." -ForegroundColor Yellow
try {
    $config = Get-Content "config.json" | ConvertFrom-Json
    
    if ($config.HF_TOKEN -like "*your_token*" -or $config.HF_TOKEN -like "*enter your*") {
        Write-Host "⚠ Warning: config.json still has placeholder token" -ForegroundColor Yellow
        Write-Host "  Please update HF_TOKEN with your actual Hugging Face token" -ForegroundColor Gray
    } elseif ($config.HF_TOKEN -match "^hf_[a-zA-Z0-9]+$") {
        Write-Host "✓ HF_TOKEN appears valid" -ForegroundColor Green
    } else {
        Write-Host "⚠ Warning: HF_TOKEN format looks unusual" -ForegroundColor Yellow
        Write-Host "  Expected format: hf_..." -ForegroundColor Gray
    }
    
    if ($config.MODEL_NAME) {
        Write-Host "✓ MODEL_NAME: $($config.MODEL_NAME)" -ForegroundColor Green
    } else {
        Write-Host "ℹ MODEL_NAME not set (will use default)" -ForegroundColor Cyan
    }
} catch {
    Write-Host "⚠ Warning: Could not parse config.json" -ForegroundColor Yellow
    Write-Host "  Make sure it's valid JSON format" -ForegroundColor Gray
}

Write-Host ""

# Download TTS models
Write-Host "Initializing Mozilla TTS models..." -ForegroundColor Yellow
Write-Host "This is a one-time download (~200MB)..." -ForegroundColor Gray
Write-Host ""

try {
    python -c "from TTS.api import TTS; print('Downloading TTS models...'); tts = TTS(model_name='tts_models/en/ljspeech/tacotron2-DDC', progress_bar=True); print('TTS initialized successfully')"
    Write-Host "✓ TTS models initialized" -ForegroundColor Green
} catch {
    Write-Host "⚠ Warning: Could not pre-download TTS models" -ForegroundColor Yellow
    Write-Host "  Models will download on first use" -ForegroundColor Gray
}

Write-Host ""
Write-Host "==================================" -ForegroundColor Cyan
Write-Host "Setup Complete!" -ForegroundColor Green
Write-Host "==================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "  1. Ensure config.json has your Hugging Face token" -ForegroundColor White
Write-Host "  2. Run the server: python app.py" -ForegroundColor White
Write-Host "  3. Server will start on http://localhost:5000" -ForegroundColor White
Write-Host ""

$response = Read-Host "Start server now? (y/n)"
if ($response -eq "y" -or $response -eq "Y") {
    Write-Host ""
    Write-Host "Starting server..." -ForegroundColor Cyan
    Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Gray
    Write-Host ""
    python app.py
} else {
    Write-Host ""
    Write-Host "To start server later, run: python app.py" -ForegroundColor Yellow
}
