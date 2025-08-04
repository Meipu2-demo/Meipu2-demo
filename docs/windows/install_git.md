# Gitのインストール

## Git for Windowsのインストール
https://git-scm.com/download/win からGit for Windowsをダウンロードしてインストールします。

### インストール手順
1. 上記リンクから最新版のGit for Windowsをダウンロード
2. ダウンロードしたexeファイルを実行
3. インストールウィザードに従って進む（デフォルト設定で問題ありません）

### インストール確認
コマンドプロンプトまたはPowerShellを開いて以下を実行：
```cmd
git --version
```

# Git LFSのインストール
Git LFSは通常Git for Windowsに含まれていますが、含まれていない場合は以下を実行：

```cmd
git lfs install
```

Git LFSが正しくインストールされているか確認：
```cmd
git lfs version
```
