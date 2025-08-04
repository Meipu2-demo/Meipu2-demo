#!/bin/bash

# macOSツール自動インストールスクリプト
# インストール対象: brew, git, git lfs, uv, direnv

set -e  # エラー時にスクリプトを終了

# 色の定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# ログ関数
log_info() {echo -e "${BLUE}[INFO]${NC} $1";}
log_success() {echo -e "${GREEN}[SUCCESS]${NC} $1";}
log_warning() {echo -e "${YELLOW}[WARNING]${NC} $1";}
log_error() {echo -e "${RED}[ERROR]${NC} $1";}

# ツールがインストール済みかチェックする関数
is_installed() {
    local tool_name="$1"
    local check_command="$2"
    if eval "$check_command" >/dev/null 2>&1; then
        return 0  # インストール済み
    else
        return 1  # 未インストール
    fi
}

# ユーザー確認を求める関数
ask_confirmation() {
    local message="$1"
    echo -e "${YELLOW}$message${NC}"
    read -p "続行しますか？ [y/N]: " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log_info "インストールをキャンセルしました。"
        exit 0
    fi
}

# Homebrewのインストール
install_homebrew() {
    log_info "Homebrewをインストールしています..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    # Apple Silicon Macの場合、PATHを追加
    if [[ $(uname -m) == "arm64" ]]; then
        echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
        eval "$(/opt/homebrew/bin/brew shellenv)"
    fi
    log_success "Homebrewのインストールが完了しました。"
}

# 各ツールのインストール
install_git() {
    log_info "Gitをインストールしています..."
    brew install git
    log_success "Gitのインストールが完了しました。"
}

install_git_lfs() {
    log_info "Git LFSをインストールしています..."
    brew install git-lfs
    log_info "Git LFSを設定しています..."
    git lfs install
    log_success "Git LFSのインストールと設定が完了しました。"
}

install_uv() {
    log_info "uvをインストールしています..."
    brew install uv
    log_success "uvのインストールが完了しました。"
}

install_direnv() {
    log_info "direnvをインストールしています..."
    brew install direnv
    log_success "direnvのインストールが完了しました。"

    log_warning "direnvを有効にするには、シェル設定ファイルに以下を追加してください："
    echo "  bash: echo 'eval \"\$(direnv hook bash)\"' >> ~/.bashrc"
    echo "  zsh:  echo 'eval \"\$(direnv hook zsh)\"' >> ~/.zshrc"
    echo "  fish: echo 'direnv hook fish | source' >> ~/.config/fish/config.fish"
}

# メイン実行部分
main() {
    echo "=== macOS ツール自動インストールスクリプト ==="
    echo
    echo "このスクリプトは以下のツールをインストールします："
    echo "• Homebrew (パッケージマネージャー)"
    echo "• Git (バージョン管理システム)"
    echo "• Git LFS (Large File Storage)"
    echo "• uv (Python パッケージマネージャー)"
    echo "• direnv (環境変数管理)"
    echo

    ask_confirmation "インストールを開始しますか？"
    echo

    # 現在のインストール状況をチェック
    log_info "現在のインストール状況を確認しています..."
    echo

    tools_to_install=()

    # Homebrew
    if is_installed "Homebrew" "which brew"; then
        log_success "Homebrew: 既にインストール済み ($(brew --version | head -n1))"
    else
        log_warning "Homebrew: 未インストール"
        tools_to_install+=("homebrew")
    fi

    # Git
    if is_installed "Git" "which git"; then
        log_success "Git: 既にインストール済み ($(git --version))"
    else
        log_warning "Git: 未インストール"
        tools_to_install+=("git")
    fi

    # Git LFS
    if is_installed "Git LFS" "git lfs version"; then
        log_success "Git LFS: 既にインストール済み ($(git lfs version | head -n1))"
    else
        log_warning "Git LFS: 未インストール"
        tools_to_install+=("git-lfs")
    fi

    # uv
    if is_installed "uv" "which uv"; then
        log_success "uv: 既にインストール済み ($(uv --version 2>/dev/null || echo 'インストール済み'))"
    else
        log_warning "uv: 未インストール"
        tools_to_install+=("uv")
    fi

    # direnv
    if is_installed "direnv" "which direnv"; then
        log_success "direnv: 既にインストール済み ($(direnv version))"
    else
        log_warning "direnv: 未インストール"
        tools_to_install+=("direnv")
    fi

    echo

    # インストールが必要なツールがない場合
    if [ ${#tools_to_install[@]} -eq 0 ]; then
        log_success "🎉 すべてのツールが既にインストールされています！"
        exit 0
    fi

    # インストール実行
    log_info "以下のツールをインストールします: ${tools_to_install[*]}"
    ask_confirmation "インストールを実行しますか？"
    echo

    for tool in "${tools_to_install[@]}"; do
        case "$tool" in
            "homebrew")
                install_homebrew
                ;;
            "git")
                install_git
                ;;
            "git-lfs")
                install_git_lfs
                ;;
            "uv")
                install_uv
                ;;
            "direnv")
                install_direnv
                ;;
        esac
        echo
    done

    # 最終確認
    log_success "🎉 インストールが完了しました！"
    echo
    log_info "インストール後の確認を実行しています..."
    echo

    # 最終確認（簡易版）
    if is_installed "Homebrew" "which brew"; then
        log_success "✓ Homebrew: $(brew --version | head -n1)"
    fi

    if is_installed "Git" "which git"; then
        log_success "✓ Git: $(git --version)"
    fi

    if is_installed "Git LFS" "git lfs version"; then
        log_success "✓ Git LFS: $(git lfs version | head -n1)"
    fi

    if is_installed "uv" "which uv"; then
        log_success "✓ uv: $(uv --version 2>/dev/null || echo 'インストール済み')"
    fi

    if is_installed "direnv" "which direnv"; then
        log_success "✓ direnv: $(direnv version)"
    fi

    echo
    log_info "追加設定が必要な場合："
    echo "• direnvを使用する場合は、シェル設定ファイルへの追加が必要です"
    echo "• 新しいターミナルセッションを開始するか、'source ~/.zshrc' などでシェル設定を再読み込みしてください"
    echo
    log_info "次のステップ："
    echo "• `. ./core/scripts/check-tools-arm64-mac.sh` を実行してツールの確認を行ってください"
    log_success "セットアップ完了！開発環境をお楽しみください 🚀"
}

# スクリプトがsourceされずに直接実行された場合のみmainを実行
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
