# ================================
# GitHub SSH Key Setup Script (Fully Automated)
# ================================

# 请修改这里：你的 GitHub 邮箱 & GitHub Token
$github_email = "contemnewton@163.com"
$github_token = "ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"

# GitHub API endpoint
$github_api = "https://api.github.com/user/keys"

Write-Host "🔍 检查 SSH Key..."

$ssh_folder = "$HOME\.ssh"
$ssh_key = "$ssh_folder\id_ed25519"
$ssh_pub = "$ssh_key.pub"

# 确保 .ssh 文件夹存在
if (!(Test-Path -Path $ssh_folder)) {
    New-Item -ItemType Directory -Force -Path $ssh_folder | Out-Null
}

# 生成新的 key（如果不存在）
#ssh-keygen -t ed25519 -C contemnewton@163.com 
if (!(Test-Path -Path $ssh_key)) {
    Write-Host "⚡ 生成新的 SSH Key..."
    cmd /c "ssh-keygen -t ed25519 -C `"$github_email`" -f `"$ssh_key`" -N `""`"
} else {
    Write-Host "✅ 已存在 SSH Key: $ssh_key"
}

# 启动 ssh-agent
Write-Host "🚀 启动 ssh-agent..."
Start-Service ssh-agent
Get-Service ssh-agent | Set-Service -StartupType Automatic

# 添加 key
Write-Host "➕ 添加 SSH Key 到 ssh-agent..."
ssh-add $ssh_key

# 读取公钥内容
$public_key = Get-Content $ssh_pub -Raw

# 上传到 GitHub
Write-Host "🌐 上传 SSH Key 到 GitHub..."
$headers = @{
    Authorization = "token $github_token"
    "User-Agent"  = "PowerShell"
    Accept        = "application/vnd.github+json"
}
$body = @{
    title = "Windows-$(hostname)-$(Get-Date -Format yyyyMMddHHmmss)"
    key   = $public_key
} | ConvertTo-Json

$response = Invoke-RestMethod -Uri $github_api -Headers $headers -Method POST -Body $body

if ($response.id) {
    Write-Host "✅ SSH Key 已成功上传到 GitHub (ID: $($response.id))"
} else {
    Write-Host "❌ 上传失败，请检查 Token 权限"
}

# 测试连接
Write-Host "`n🔑 测试连接 GitHub..."
ssh -T git@github.com
