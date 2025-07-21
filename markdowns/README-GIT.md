git rm --cached .env.development .env.production

git reset HEAD~1  # 回退上一个提交（或更多）
# 然后重新提交，不包含 .env.*
git add .
git commit -m "fix: remove env files"
git push --force

# 官方推荐用 pip 安装
pip install git-filter-repo

git filter-repo --path-glob '.env*' --invert-paths

git push origin --force --all
git push origin --force --tags

git log --all -- .env


# 使用国内代理、只 clone .git 内容
git clone --mirror https://ghproxy.com/https://github.com/xxx/your-repo.git cleaned-repo
cd cleaned-repo

# 删除 .env.* 文件（全部匹配）
git filter-repo --path-glob '.env*' --invert-paths

# 推回远程（慎用 --force）
git push --force --all
git push --force --tags


cd newblog

# 使用 filter-repo 清理 .env.* 文件相关历史
git filter-repo --path-glob '.env*' --invert-paths
git filter-repo --path-glob '.env*' --path-glob 'secret.json' --invert-paths

# 请确保你了解这样做会永久改变远程历史，所有协作者都需要强制拉取或重克隆：
git remote -v  # 确保 remote 正确
git push --force --all
git push --force --tags

cd myblog

# 清理所有本地改动
git reset --hard

git fetch --all
git reset --hard origin/main  # 如果主分支叫 main


# 安全同步方案
cd myblog
git stash push -m "本地临时保存"

cd myblog
# 拉取远程新历史（需要 --force）
git fetch --all
git reset --hard origin/main  # ⚠️ 会覆盖本地代码（已 stash/备份就不怕）

git stash list           # 看你是否能看到你之前的那条记录
git stash pop            # 恢复改动

