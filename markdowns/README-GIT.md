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
git branch develop
git checkout -b develop origin/develop
git checkout -b some-feature develop

{
  "init_and_clone": {
    "init": "git init",
    "clone": "git clone <repo_url>"
  },
  "config": {
    "set_username": "git config --global user.name 'Your Name'",
    "set_email": "git config --global user.email 'you@example.com'",
    "check_config": "git config --list"
  },
  "basic": {
    "status": "git status",
    "add": "git add <file> | .",
    "commit": "git commit -m 'message'",
    "diff": "git diff",
    "log": "git log --oneline --graph --decorate --all"
  },
  "branching": {
    "list_branches": "git branch",
    "create_branch": "git branch <branch_name>",
    "switch_branch": "git checkout <branch_name>",
    "create_and_switch": "git checkout -b <branch_name>",
    "delete_branch": "git branch -d <branch_name>",
    "rename_branch": "git branch -m <old_name> <new_name>"
  },
  "remote": {
    "add_remote": "git remote add origin <url>",
    "show_remotes": "git remote -v",
    "fetch": "git fetch origin",
    "pull": "git pull origin <branch>",
    "push": "git push origin <branch>",
    "push_new_branch": "git push -u origin <branch>"
  },
  "stashing": {
    "stash_changes": "git stash",
    "stash_list": "git stash list",
    "apply_stash": "git stash apply",
    "drop_stash": "git stash drop"
  },
  "merging": {
    "merge_branch": "git merge <branch>",
    "abort_merge": "git merge --abort"
  },
  "rebasing": {
    "rebase_branch": "git rebase <branch>",
    "abort_rebase": "git rebase --abort",
    "continue_rebase": "git rebase --continue"
  },
  "reset_and_revert": {
    "soft_reset": "git reset --soft HEAD~1",
    "mixed_reset": "git reset --mixed HEAD~1",
    "hard_reset": "git reset --hard HEAD~1",
    "revert_commit": "git revert <commit_id>"
  },
  "collaboration_flow": {
    "feature_branch": "git checkout -b feature/<name>",
    "commit_changes": "git commit -m 'feat: description'",
    "update_main": "git checkout main && git pull origin main",
    "rebase_feature": "git checkout feature/<name> && git rebase main",
    "push_feature": "git push origin feature/<name>",
    "open_pr": "Create Pull Request on GitHub/GitLab"
  },
  "tags": {
    "create_tag": "git tag <tag_name>",
    "annotated_tag": "git tag -a <tag_name> -m 'message'",
    "push_tag": "git push origin <tag_name>",
    "push_all_tags": "git push origin --tags"
  },
  "cleaning": {
    "remove_untracked": "git clean -f",
    "remove_untracked_dirs": "git clean -fd",
    "prune_remote": "git remote prune origin"
  }
}
# 1. 克隆与初始化
git clone <repo-url>        # 克隆远程仓库
git init                     # 初始化本地仓库
git remote add origin <url>  # 添加远程仓库
# 2. 分支管理
git branch                   # 查看本地分支
git branch -r                # 查看远程分支
git checkout -b feature/x    # 新建并切换分支
git switch main              # 切换分支
git branch -d feature/x      # 删除本地分支
git push origin --delete feature/x  # 删除远程分支
# 3. 提交修改
git status                   # 查看修改状态
git add .                    # 暂存所有修改
git commit -m "feat: add login API"  # 提交修改
git commit --amend           # 修改最近一次提交
# 4. 同步远程
git fetch origin             # 获取远程更新但不合并
git pull origin main         # 拉取并合并
git push origin feature/x    # 推送分支
git push -u origin develop   # 推送并设置跟踪分支
# 5. 合并与变基
git merge feature/x          # 合并分支
git rebase main              # 将当前分支变基到 main
git rebase -i HEAD~3         # 交互式 rebase (压缩/修改提交)
# 6. 回滚与撤销
git reset --hard HEAD~1      # 回退到上一个提交（丢弃修改）
git revert <commit-id>       # 生成一个撤销某次提交的新提交
git restore file.txt         # 撤销文件的修改
# 7. 标签管理
git tag v1.0.0               # 打标签
git tag                      # 查看标签
git push origin v1.0.0       # 推送标签
git push origin --tags       # 推送所有标签

# 1. Feature 开发
git checkout develop
git checkout -b feature/login
# 开发中 ...
git commit -m "feat: add login API"
git push origin feature/login
# 提交 PR → 合并到 develop
# 2. Release 流程
git checkout develop
git checkout -b release/v1.0.0
# 测试和修复 bug ...
git commit -m "chore: update changelog"
git checkout main
git merge release/v1.0.0
git tag v1.0.0
git push origin main --tags
# 3. Hotfix 流程
git checkout main
git checkout -b hotfix/bug-123
# 修复 bug ...
git commit -m "fix: urgent bug fix"
git checkout main
git merge hotfix/bug-123
git checkout develop
git merge hotfix/bug-123
git push origin main develop
# 日常高频命令速查
git stash                     # 临时保存修改
git stash pop                 # 恢复保存的修改
git log --oneline --graph     # 图形化查看提交历史
git diff                      # 查看未暂存的修改
git show <commit-id>          # 查看某次提交详情
{
  "初始化与配置": {
    "初始化仓库": "git init",
    "克隆远程仓库": "git clone <repo_url>",
    "设置用户名": "git config --global user.name 'Your Name'",
    "设置邮箱": "git config --global user.email 'your@email.com'"
  },
  "常用操作": {
    "查看状态": "git status",
    "查看日志": "git log --oneline --graph --decorate --all",
    "添加文件": "git add <file> | git add .",
    "提交": "git commit -m 'message'",
    "修改最后一次提交": "git commit --amend"
  },
  "分支管理": {
    "创建新分支": "git branch <branch>",
    "切换分支": "git checkout <branch>",
    "创建并切换": "git checkout -b <branch>",
    "查看分支": "git branch -a",
    "删除分支": "git branch -d <branch>",
    "合并分支": "git merge <branch>",
    "变基分支": "git rebase <branch>"
  },
  "远程仓库": {
    "添加远程": "git remote add origin <url>",
    "查看远程": "git remote -v",
    "推送到远程": "git push origin <branch>",
    "拉取更新": "git pull origin <branch>",
    "获取更新(不合并)": "git fetch origin"
  },
  "撤销与修复": {
    "撤销未暂存修改": "git checkout -- <file>",
    "撤销已暂存修改": "git reset <file>",
    "回退到某个提交": "git reset --hard <commit>",
    "生成补丁提交": "git revert <commit>",
    "清理未跟踪文件": "git clean -fd"
  },
  "高级操作": {
    "保存临时工作": "git stash",
    "恢复临时工作": "git stash pop",
    "交互式变基": "git rebase -i <commit>",
    "挑选某次提交": "git cherry-pick <commit>",
    "标签": "git tag -a v1.0 -m 'version 1.0'"
  },
  "常见工作流": {
    "feature 分支": "git checkout -b feature/<name>",
    "hotfix 分支": "git checkout -b hotfix/<name>",
    "release 分支": "git checkout -b release/<version>",
    "合并到 develop": "git checkout develop && git merge feature/<name>",
    "合并到 main": "git checkout main && git merge release/<version>"
  }
}

{
  "Git_Flow": {
    "main_branches": ["main", "develop"],
    "feature_branch": {
      "base": "develop",
      "naming": "feature/<name>",
      "purpose": "开发新功能"
    },
    "release_branch": {
      "base": "develop",
      "naming": "release/<version>",
      "purpose": "准备发布版本，修复小问题"
    },
    "hotfix_branch": {
      "base": "main",
      "naming": "hotfix/<issue>",
      "purpose": "紧急修复线上问题"
    },
    "merge_strategy": {
      "feature": "feature -> develop",
      "release": "release -> develop & main",
      "hotfix": "hotfix -> main & develop"
    }
  },
  "GitHub_Flow": {
    "main_branches": ["main"],
    "feature_branch": {
      "base": "main",
      "naming": "<name> 或 feature/<name>",
      "purpose": "基于 main 开发功能，通过 PR 合并"
    },
    "release_branch": {
      "base": "main",
      "naming": "不需要单独分支",
      "purpose": "直接从 main 发布"
    },
    "hotfix_branch": {
      "base": "main",
      "naming": "hotfix/<issue>",
      "purpose": "修复问题，快速合并回 main"
    },
    "merge_strategy": {
      "feature": "feature -> main (PR + review)",
      "release": "main 直接发版",
      "hotfix": "hotfix -> main (PR + review)"
    }
  },
  "Trunk_Based_Development": {
    "main_branches": ["main"],
    "feature_branch": {
      "base": "main",
      "naming": "短期分支，如 feature/<name>",
      "purpose": "快速迭代，通常 1-2 天合并回 main"
    },
    "release_branch": {
      "base": "main",
      "naming": "release/<version>（可选）",
      "purpose": "发布前冻结代码，通常很少使用"
    },
    "hotfix_branch": {
      "base": "main",
      "naming": "hotfix/<issue>",
      "purpose": "紧急修复，立即合并回 main"
    },
    "merge_strategy": {
      "feature": "feature -> main (CI/CD 自动化)",
      "release": "release -> main (如有使用)",
      "hotfix": "hotfix -> main"
    }
  }
}

