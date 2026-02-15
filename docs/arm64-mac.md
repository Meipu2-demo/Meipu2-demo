# 想定読者
高校生でも実行できるように、できるだけわかりやすくなるように書くよう心がけています。\
もしわかりにくい部分があれば、お気軽にissueにてご報告いただけると幸いです。


# 前提環境
- Arm版Mac(M1, M2, M3)
- IntelMacは未検証

## 重要な注意事項
- **日本語を含むディレクトリパスでは実行できません**。必ず英数字のみのパスを使用してください。
- 例：`/Users/田中/Meipu2-demo` → **動作しません**
- 正しい例：`/Users/tanaka/Meipu2-demo` または `/Users/username/Meipu2-demo`

## 前提環境のインストール

### Homebrewのインストール

#### インストール
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

#### パスの設定
インストール後、以下のコマンドを実行してパスを設定：

```bash
echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zshrc
source ~/.zshrc
```

#### インストール確認
```bash
brew --version
```

### Gitのインストール
```bash
brew install git
source ~/.zshrc
which git  # /opt/homebrew/bin/git と表示されることを確認
```

### uvのインストール

#### インストール
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
source ~/.zshrc
```

#### インストール確認
```bash
uv --version
```

### direnvのインストール

#### インストール
```bash
brew install direnv
```

#### シェル設定
```bash
echo 'eval "$(direnv hook zsh)"' >> ~/.zshrc
source ~/.zshrc
```

#### インストール確認
```bash
direnv --version
```

<!-- TODO: ここにインストール/チェックスクリプト -->
これらのツールのインストールをまとめたスクリプトがあるので、これを実行します。
```bash
./core/scripts/install-tools-arm64-mac.sh
./core/scripts/check-tools-arm64-mac.sh
```

# 設定手順

## 1. 任意のディレクトリでclone
```bash
# 任意のディレクトリ
cd ~/
git clone https://github.com/Meipu2-demo/Meipu2-demo.git
```

## 2. サブモジュールの初期化
Meipu2-demoディレクトリに移動し、`contents` と `dictation-kit` のサブモジュールを初期化します。

```bash
cd ~/Meipu2-demo
git submodule update --init --recursive contents dictation-kit
```


## 3. MMDAgent-EXの実行バイナリをビルド
https://mmdagent-ex.dev/ja/docs/build/#macos
を参考にビルドをしてください。
```bash
cd ~/Meipu2-demo
git clone https://github.com/mmdagent-ex/MMDAgent-EX.git MMDAgent-EX
cd ./MMDAgent-EX
brew install cmake glew libjpeg jpeg-turbo re2 portaudio minizip libsndfile libsamplerate sox rabbitmq-c libomp librdkafka
cmake -S. -Bbuild -DCMAKE_BUILD_TYPE=Release
cmake --build build
```

エラーが出る場合は[こちら](https://mmdagent-ex.dev/ja/docs/build/#%e3%82%a8%e3%83%a9%e3%83%bc%e3%82%b1%e3%83%bc%e3%82%b9%ef%bc%91libomp-%e9%96%a2%e9%80%a3%e3%81%a7%e3%82%a8%e3%83%a9%e3%83%bc%e3%81%8c%e5%87%ba%e3%82%8b)を参考にしてください。\
また、issueを立てて質問していただいても構いません。

## 4.各APIの準備
主に2つのAPIを使用します。これらは料金がかかる場合があります。\
これらの使用による損害は一切責任を負いかねます。また、入力されたデータは外部サービスに送信されるため、個人情報や機密情報を含む入力は避けてください。データのプライバシー保護、情報漏洩、API利用料金の発生、サービスの利用制限等に関する一切の責任は負いかねますので、各APIの利用規約とプライバシーポリシーを十分にご確認の上、自己責任でご利用ください。

### 4.1.Speech-To-Text
GCP(Google Cloud Platform)にて、Speech-To-Text APIを有効化し、認証JSONを作成、\
Meipu2-demo/credentials.jsonを作成し、内容をペーストしてください。\
詳しくは以下の記事の手順[1,2,3,4,5]を参考にしてください。\
使用したいAPIは「Cloud Speech-to-Text API」です。

https://qiita.com/tsubasamusu/items/f60879a623803ea2e208
<!-- todo: 手順書 -->

### 4.2.Gemini API
[Google AI Studio](https://aistudio.google.com/app/apikey?hl=ja) で無料で取得できます。
詳しくは以下の記事を参考にしてください。

https://monomonotech.jp/kurage/memo/m240725_get_gemini_api_key.html

<!-- todo: 手順書 -->

## 5. 環境を設定
```bash
# 任意のディレクトリ
cd ~/Meipu2-demo
uv sync
cp .envrc.example .envrc
# ファイルを編集して、MEIPU_GEMINI_API_KEYにGemini APIを設定
nano .envrc
direnv allow .
```

## 設定後のフォルダ構成
```
/
└─ Meipu2-demo
      ├─ .venv/
      ├─ contents/
      ├─ core/
      ├─ dictation-kit/
      ├─ docs/
      ├─ meipu-contents/
      ├─ MMDAgent-EX
      │     ├─ ...
      │     ├─ Release
      │     │     ├─ AppData/
      │     │     ├─ DLLs/
      │     │     ├─ Plugins/
      │     │     ├─ MMDAgent-EX
      │     │     ├─ MMDAgent-EX.mdf
      │     │     └─ README.txt
      │     └─ ...
      ├─ Record/
      ├─ .envrc
      ├─ .envrc.example
      ├─ .gitattributes
      ├─ .gitignore
      ├─ .gitmodules
      ├─ .python-version
      ├─ credentials.json
      ├─ pyproject.toml
      ├─ README.md
      ├─ requirements.txt
      └─ uv.lock
```

# 実行
2つターミナルを使用します。
AとBと呼称します。

Aを立ち上げ、
```bash
# 任意のディレクトリ
cd ~/Meipu2-demo
./core/scripts/julius-arm64-mac.sh
```
を実行

Bを立ち上げ、
```bash
# 任意のディレクトリ
cd ~/Meipu2-demo
./MMDAgent-EX/Release/MMDAgent-EX ./meipu-contents/main.mdf
```
を実行します。するとウィンドウが立ち上がるので、対話を開始してください。
