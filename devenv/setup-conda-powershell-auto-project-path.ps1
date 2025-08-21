# ================================
# Windows PowerShell - Full Auto Multi-project Conda Management
# Fixed & Optimized Version
# ================================

# Miniconda 安装路径（自动检测 USERPROFILE）
$minicondaPath = "$env:USERPROFILE\Miniconda3"
$condaExe = Join-Path $minicondaPath "Scripts\conda.exe"

# 检查 conda.exe 是否存在
if (-not (Test-Path $condaExe)) {
    throw "❌ 找不到 conda.exe，请检查 Miniconda 安装路径：$minicondaPath"
}

# 初始化 Conda Hook（官方推荐方式）
& $condaExe shell.powershell hook | Out-String | Invoke-Expression

# 文件记录
$lastEnvFile = Join-Path $env:USERPROFILE '.last_conda_env.txt'
$projectEnvMappingFile = Join-Path $env:USERPROFILE '.conda_project_envs.json'

# 确保 JSON 文件存在
if (-not (Test-Path $projectEnvMappingFile)) { '{}' | Out-File -Encoding UTF8 $projectEnvMappingFile }

# 获取指定 Conda 环境 Python 版本
function Get-CondaEnvPythonVersion {
    param([string]$envName)
    try {
        $pythonPath = (& $condaExe run -n $envName where python 2>$null)[0]
        if ($pythonPath) {
            $ver = (& $pythonPath --version).Split()[1]
            return $ver
        }
    } catch { return "" }
}

# 自动绑定项目 Conda 环境
function Set-ProjectCondaEnvBinding {
    $projectPath = (Get-Location).Path

    # 安全读取 JSON
    $mapping = @{}
    try {
        if (Test-Path $projectEnvMappingFile) {
            $mapping = Get-Content $projectEnvMappingFile -Raw | ConvertFrom-Json
        }
    } catch { $mapping = @{} }

    $pythonVersionFile = Join-Path $projectPath '.python-version'
    if (Test-Path $pythonVersionFile) { $requiredPythonVersion = (Get-Content $pythonVersionFile -Raw).Trim() } else { $requiredPythonVersion = "" }

    # 已绑定环境
    if ($mapping.PSObject.Properties.Name -contains $projectPath) {
        $envName = $mapping.$projectPath
        $envExists = (& $condaExe env list | Select-String -Pattern "^$envName\s")
        if ($envExists) {
            $currentPython = Get-CondaEnvPythonVersion $envName
            if ($requiredPythonVersion -and $currentPython -ne $requiredPythonVersion) {
                Write-Host "⚠️ 项目要求 Python $requiredPythonVersion，但环境 $envName 是 $currentPython"
                $action = Read-Host "输入 'c' 创建新环境, 's' 强制激活当前环境, 回车跳过"
                if ($action -eq 'c') {
                    $newEnvName = Read-Host "请输入新虚拟环境名称"
                    & $condaExe create -y -n $newEnvName python=$requiredPythonVersion
                    $mapping.$projectPath = $newEnvName
                    $mapping | ConvertTo-Json | Set-Content $projectEnvMappingFile -Encoding UTF8
                    & $condaExe activate $newEnvName
                    Set-Content -Path $lastEnvFile -Value $newEnvName
                    return
                } elseif ($action -eq 's') {
                    & $condaExe activate $envName
                    Set-Content -Path $lastEnvFile -Value $envName
                    return
                } else { return }
            } else {
                Write-Host "📂 自动激活项目环境 $envName (Python $currentPython)"
                & $condaExe activate $envName
                Set-Content -Path $lastEnvFile -Value $envName
                return
            }
        } else {
            Write-Host "⚠️ 项目指定环境 $envName 不存在"
        }
    }

    # 未绑定或选择其他环境
    $envs = (& $condaExe env list | ForEach-Object { $_.Trim() } | Where-Object { $_ -ne "" -and -not $_ -match "^#" })
    Write-Host "🔹 可选择已有环境或创建新环境："
    for ($i=0; $i -lt $envs.Count; $i++) {
        $name = $envs[$i].Split()[0]
        $pyVer = Get-CondaEnvPythonVersion $name
        Write-Host "[$i] $name ($pyVer)"
    }
    Write-Host "[n] 创建新虚拟环境"
    Write-Host "[Enter] 激活上次使用的环境"

    $choice = Read-Host "选择编号激活环境，输入 'n' 创建新环境，回车使用上次环境"

    if (([string]::IsNullOrWhiteSpace($choice)) -and (Test-Path $lastEnvFile)) {
        $envName = Get-Content $lastEnvFile -Raw
        Write-Host "💡 激活上次环境: $envName"
        & $condaExe activate $envName
        return
    }

    if ($choice -eq 'n') {
        $newEnvName = Read-Host "请输入新虚拟环境名称"
        if (-not $requiredPythonVersion) { 
            $requiredPythonVersion = Read-Host "请输入 Python 版本（回车默认 3.11）"; 
            if (-not $requiredPythonVersion) { $requiredPythonVersion='3.11' } 
        }
        & $condaExe create -y -n $newEnvName python=$requiredPythonVersion
        $mapping.$projectPath = $newEnvName
        $mapping | ConvertTo-Json | Set-Content $projectEnvMappingFile -Encoding UTF8
        & $condaExe activate $newEnvName
        Set-Content -Path $lastEnvFile -Value $newEnvName
    } elseif ($choice -match '^\d+$' -and $choice -lt $envs.Count) {
        $envName = $envs[$choice].Split()[0]
        Write-Host "激活环境: $envName"
        & $condaExe activate $envName
        $mapping.$projectPath = $envName
        $mapping | ConvertTo-Json | Set-Content $projectEnvMappingFile -Encoding UTF8
        Set-Content -Path $lastEnvFile -Value $envName
    } else {
        Write-Host "跳过激活环境"
    }
}

# 自动绑定当前项目 Conda 环境
Set-ProjectCondaEnvBinding

Write-Host "✅ Conda multi-project 自动管理已完成"
