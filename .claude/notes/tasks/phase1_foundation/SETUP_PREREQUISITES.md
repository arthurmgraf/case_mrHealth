# SETUP: Prerequisites Installation Guide

## Current Status

**Environment Check Results:**
- ❌ gcloud CLI: Not installed
- ❌ Python: Not installed

**Action Required:** Install prerequisites before proceeding with Phase 1 tasks.

---

## Installation Steps (Windows)

### 1. Install Python 3.11+

**Option A: Official Python Installer (Recommended)**
1. Download: https://www.python.org/downloads/
2. Run installer
3. ✅ CHECK: "Add Python to PATH"
4. Click "Install Now"
5. Verify:
   ```cmd
   python --version
   # Expected: Python 3.11.x or higher
   ```

**Option B: Microsoft Store**
1. Open Microsoft Store
2. Search "Python 3.11"
3. Click "Get" to install
4. Verify in PowerShell/CMD:
   ```cmd
   python --version
   ```

### 2. Install Google Cloud SDK (gcloud CLI)

**Installation:**
1. Download: https://cloud.google.com/sdk/docs/install
2. Run `GoogleCloudSDKInstaller.exe`
3. Follow installation wizard
4. ✅ CHECK: "Run gcloud init"
5. Complete:
   ```cmd
   gcloud init
   ```
6. Verify:
   ```cmd
   gcloud --version
   # Expected: Google Cloud SDK 4xx.x.x
   ```

### 3. Install Python Dependencies

After Python is installed:

```cmd
pip install faker pandas google-cloud-storage google-cloud-bigquery
```

**Verify installation:**
```cmd
python -c "import faker, pandas; print('Dependencies OK')"
# Expected: Dependencies OK
```

---

## GCP Account Setup

### Step 1: Create GCP Free Tier Account

1. Go to: https://console.cloud.google.com
2. Sign in with Google account
3. Accept terms and start free trial (requires credit card but won't charge)
4. Free tier benefits:
   - $300 credit for 90 days (trial)
   - Always Free tier (permanent after trial)
   - No automatic charges after trial expires

### Step 2: Find Your Billing Account ID

```bash
# After gcloud init, run:
gcloud billing accounts list

# Output example:
# ACCOUNT_ID            NAME                OPEN  MASTER_ACCOUNT_ID
# 012345-ABCDEF-GHIJKL  My Billing Account  True
```

Save your `ACCOUNT_ID` for TASK_001.

---

## Quick Setup Script (PowerShell)

After installing Python and gcloud CLI, run this to verify:

```powershell
# Verify installations
Write-Host "Checking Prerequisites..." -ForegroundColor Cyan

# Check Python
$pythonVersion = python --version 2>&1
if ($pythonVersion -match "Python 3\.([0-9]+)") {
    if ([int]$matches[1] -ge 9) {
        Write-Host "✅ Python: $pythonVersion" -ForegroundColor Green
    } else {
        Write-Host "❌ Python: Version too old (need 3.9+)" -ForegroundColor Red
    }
} else {
    Write-Host "❌ Python: Not found" -ForegroundColor Red
}

# Check gcloud
$gcloudVersion = gcloud --version 2>&1 | Select-String "Google Cloud SDK"
if ($gcloudVersion) {
    Write-Host "✅ gcloud: $gcloudVersion" -ForegroundColor Green
} else {
    Write-Host "❌ gcloud: Not found" -ForegroundColor Red
}

# Check pip packages
try {
    python -c "import faker, pandas" 2>&1 | Out-Null
    Write-Host "✅ Python packages: faker, pandas installed" -ForegroundColor Green
} catch {
    Write-Host "❌ Python packages: Not installed (run: pip install faker pandas)" -ForegroundColor Red
}

Write-Host "`nSetup Status:" -ForegroundColor Cyan
Write-Host "Once all checks are green, proceed to TASK_001" -ForegroundColor Yellow
```

---

## Next Steps After Installation

1. ✅ Verify all prerequisites are installed (run verification script above)
2. 🔧 Run `gcloud init` to authenticate and configure
3. 📋 Get your billing account ID: `gcloud billing accounts list`
4. ▶️ Proceed to TASK_001: GCP Project Setup

---

*Prerequisites Setup Guide -- Case Fictício - Teste MVP*
*Created: 2026-01-29*
