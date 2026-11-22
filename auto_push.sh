#!/usr/bin/env bash
# ============================================================
# auto_push.sh : 全自动创建 GitHub 仓库并推送本地目录
# 用法: ./auto_push.sh [目录路径] [仓库名] [可见性: public|private]
# 示例: ./auto_push.sh ./my-project my-repo private
# ============================================================

set -euo pipefail  # 遇错即停，未定义变量报错，管道失败即停

# ---- 参数解析 ----
TARGET_DIR="${1:-.}"          # 默认当前目录
REPO_NAME="${2:-$(basename "$TARGET_DIR")}" # 默认用文件夹名
VISIBILITY="${3:-private}"    # 默认私有
DESCRIPTION="Auto-pushed via gh CLI on $(date -Iseconds)"

echo "🚀 准备推送: $TARGET_DIR -> github.com/$(gh api user --jq .login)/$REPO_NAME ($VISIBILITY)"

# ---- 进入目标目录 ----
cd "$TARGET_DIR"

# ---- 1. 初始化 Git (如果还没初始化) ----
if [ ! -d ".git" ]; then
    echo "📦 初始化 Git 仓库..."
    git init -b main
    # 创建一个基础 .gitignore (可选，防止上传垃圾文件)
    cat > .gitignore <<'EOF'
# OS/IDE
.DS_Store
Thumbs.db
.vscode/
.idea/
*.swp
# Dependency/Build
node_modules/
dist/
build/
target/
__pycache__/
*.pyc
.env
*.log
EOF
fi

# ---- 2. 检查是否有提交，没有则创建首次提交 ----
if ! git rev-parse --verify HEAD >/dev/null 2>&1; then
    echo "📝 创建首次提交..."
    git add .
    git commit -m "chore: initial commit 🎉"
fi

# ---- 3. 核心：gh repo create --source=. --push ----
# --source=.       : 关联当前目录为源
# --push           :