# ================================
# Windows PowerShell - Final Minimal Conda Setup
# ================================
$minicondaPath = "$HOME\Miniconda3"
$condaExe = Join-Path $minicondaPath "Scripts\conda.exe"
Test-Path $condaExe
& "$minicondaPath\Scripts\conda.exe" shell.powershell hook | Out-String | Invoke-Expression
conda info
conda activate base
$condaScriptPath = "$minicondaPath\Scripts"
$condaLibraryPath = "$minicondaPath\Library\bin"
$condaBinPath = "$minicondaPath\condabin"

$env:PATH = "$condaScriptPath;$condaLibraryPath;$condaBinPath;$env:PATH"
conda info
conda activate base
& "$HOME\Miniconda3\Scripts\conda.exe" shell.powershell hook | Out-String | Invoke-Expression
$condaScriptPath = "$HOME\Miniconda3\Scripts"
$condaLibraryPath = "$HOME\Miniconda3\Library\bin"
$condaBinPath = "$HOME\Miniconda3\condabin"
$env:PATH = "$condaScriptPath;$condaLibraryPath;$condaBinPath;$env:PATH"
conda activate myenv
Set-Content -Path "$HOME\.last_conda_env.txt" -Value "myenv"
# activate-project.ps1
& "$HOME\Miniconda3\Scripts\conda.exe" shell.powershell hook | Out-String | Invoke-Expression
conda activate myenv
.\activate-project.ps1


conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/main
conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/r
conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/msys2

conda create -y -n test-env python=3.11













