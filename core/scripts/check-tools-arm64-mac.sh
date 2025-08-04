#!/bin/bash

# macOSツールインストール確認スクリプト
# 確認対象: brew, git, git lfs, uv, direnv

echo "=== macOS ツールインストール状況確認 ==="
echo

# 色の定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 結果を格納する配列
installed_tools=()
missing_tools=()

# 各ツールをチェックする関数
check_tool() {
    local tool_name="$1"
    local check_command="$2"
    echo -n "[$tool_name] "
    if eval "$check_command" >/dev/null 2>&1; then
        echo -e "${GREEN}✓ インストール済み${NC}"
        # バージョン情報を表示
        case "$tool_name" in
            "Homebrew")
                version=$(brew --version | head -n1)
                ;;
            "Git")
                version=$(git --version)
                ;;
            "Git LFS")
                version=$(git lfs version | head -n1)
                ;;
            "uv")
                version=$(uv --version 2>/dev/null || echo "バージョン情報取得できず")
                ;;
            "direnv")
                version=$(direnv version)
                ;;
        esac
        echo "    → $version"
        installed_tools+=("$tool_name")
    else
        echo -e "${RED}✗ 未インストール${NC}"
        missing_tools+=("$tool_name")
    fi
    echo
}

# 各ツールのチェック実行
check_tool "Homebrew" "which brew"
check_tool "Git" "which git"
check_tool "Git LFS" "git lfs version"
check_tool "uv" "which uv"
check_tool "direnv" "which direnv"

# 結果のサマリー表示
echo "=== 確認結果サマリー ==="
echo

if [ ${#installed_tools[@]} -gt 0 ]; then
    echo -e "${GREEN}✓ インストール済み (${#installed_tools[@]}個):${NC}"
    for tool in "${installed_tools[@]}"; do
        echo "  - $tool"
    done
    echo
fi

if [ ${#missing_tools[@]} -gt 0 ]; then
    echo -e "${RED}✗ 未インストール (${#missing_tools[@]}個):${NC}"
    for tool in "${missing_tools[@]}"; do
        echo "  - $tool"
    done
    echo

    echo -e "${YELLOW}=== インストール方法 ===${NC}"
    for tool in "${missing_tools[@]}"; do
        case "$tool" in
            "Homebrew")
                echo "• Homebrew:"
                echo '  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"'
                ;;
            "Git")
                echo "• Git:"
                echo "  brew install git"
                ;;
            "Git LFS")
                echo "• Git LFS:"
                echo "  brew install git-lfs"
                echo "  git lfs install"
                ;;
            "uv")
                echo "• uv:"
                echo "  brew install uv"
                ;;
            "direnv")
                echo "• direnv:"
                echo "  brew install direnv"
                ;;
        esac
        echo
    done
else
    echo -e "${GREEN}🎉 すべてのツールがインストールされています！${NC}"
fi

echo "確認完了。"
