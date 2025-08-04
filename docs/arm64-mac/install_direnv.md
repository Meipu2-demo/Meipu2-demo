# direnvのインストール
https://github.com/direnv/direnv/blob/master/docs/hook.md#zsh

```bash
brew install direnv
```

## 仮想環境のプロンプト表示
このプロジェクトでは、uvによる仮想環境を使用することを想定しています。\
direnvにて仮想環境を自動的に有効化しますが、プロンプトに仮想環境の名前を表示しません。\
例: `user@MacBook-Pro Meipu2-demo % `\
そこで、スクリプトを.zshrcに追加し、プロンプトに仮想環境の名前を表示するようにします。\
例: `(Meipu2-demo) user@MacBook-Pro Meipu2-demo % `


### 必要がない場合

```bash
echo 'export EDITOR=nano' >> ~/.zshrc
echo 'eval "$(direnv hook zsh)"' >> ~/.zshrc
source ~/.zshrc
```

### 必要な場合はこちら
```bash
cat <<'EOF' >> ~/.zshrc
```
以下を全文貼り付けてください。
```sh
# direnv prompt integration
_update_prompt_virtualenv() {
  if [[ -n "$VIRTUAL_ENV" ]]; then
    PS1="($(basename "$(dirname "$VIRTUAL_ENV")")) $OLD_PS1"
  else
    PS1="$OLD_PS1"
  fi
}

if [[ -z "$OLD_PS1" ]]; then
  OLD_PS1=$PS1
fi

autoload -Uz add-zsh-hook
add-zsh-hook precmd _update_prompt_virtualenv

export EDITOR=nano
eval "$(direnv hook zsh)"
EOF
```

最後に、.zshrcを読み込みます。
```bash
source ~/.zshrc
```
もっと良い方法があれば教えてくださると嬉しいです。
