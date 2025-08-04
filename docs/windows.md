# 想定読者
高校生でも実行できるように、できるだけわかりやすくなるように書くよう心がけています。
もしわかりにくい部分があれば、お気軽にissueにてご報告いただけると幸いです。

# 前提環境
- Windows 10 / Windows 11
- 64bit版を推奨

## 重要な注意事項
- **日本語を含むディレクトリパスでは実行できません**。必ず英数字のみのパスを使用してください。
- 例：`C:\Users\田中\Meipu2-demo` → **動作しません**
- 正しい例：`C:\Users\tanaka\Meipu2-demo` または `C:\Meipu2-demo`
- **PowerShell 7.4以降**の使用を推奨します。
- Windows PowerShellでも動作しますが、最新のPowerShellの方が高速で安定しています。

## 前提環境のインストール
- [Git](windows/install_git.md)
- [uv](windows/install_uv.md)

# 設定手順

## 1. 任意のディレクトリでclone
```powershell
# 推奨：Cドライブ直下に配置
cd C:\
git clone https://github.com/Meipu2-demo/Meipu2-demo.git
```

## 2. サブモジュールの初期化
Meipu2-demoディレクトリに移動し、Gitサブモジュールを初期化します。

```powershell
cd C:\Meipu2-demo
git submodule update --init --recursive
```

## 3. MMDAgent-EXの実行バイナリをダウンロード
ビルド済みのMMDAgent-EXを使用します。

https://github.com/mmdagent-ex/MMDAgent-EX/releases から最新のWindows版（MMDAgent-EX-*-windows.zip）をダウンロードし、`Meipu2-demo`フォルダ内の`MMDAgent-EX`フォルダに展開してください。

展開後、以下のような構成になります：
```
Meipu2-demo/
├─ MMDAgent-EX/
│  ├─ MMDAgent-EX.exe
│  ├─ AppData/
│  ├─ DLLs/
│  ├─ Plugins/
│  └─ ...
├─ contents/
│  ├─ demo/
│  ├─ main.mdf
│  ├─ main.fst
│  └─ ...
├─ dictation-kit/
│  ├─ bin/
│  ├─ model/
│  └─ ...
├─ core/
├─ meipu-contents/
└─ ...
```

## 4. 各APIの準備
主に2つのAPIを使用します。これらは料金がかかる場合があります。
これらの使用による損害は一切責任を負いかねます。また、入力されたデータは外部サービスに送信されるため、個人情報や機密情報を含む入力は避けてください。データのプライバシー保護、情報漏洩、API利用料金の発生、サービスの利用制限等に関する一切の責任は負いかねますので、各APIの利用規約とプライバシーポリシーを十分にご確認の上、自己責任でご利用ください。

### 4.1. Speech-To-Text
GCP(Google Cloud Platform)にて、Speech-To-Text APIを有効化し、認証JSONを作成、
Meipu2-demo/credentials.jsonを作成し、内容をペーストしてください。
詳しくは以下の記事の手順[1,2,3,4,5]を参考にしてください。
使用したいAPIは「Cloud Speech-to-Text API」です。

https://qiita.com/tsubasamusu/items/f60879a623803ea2e208

### 4.2. Gemini API
[Google AI Studio](https://aistudio.google.com/app/apikey?hl=ja) で無料で取得できます。
詳しくは以下の記事を参考にしてください。

https://monomonotech.jp/kurage/memo/m240725_get_gemini_api_key.html

## 5. 環境を設定
```powershell
# 任意のディレクトリ
cd C:\Meipu2-demo
uv sync
copy .envrc.example .env
# メモ帳で.envを編集してMEIPU_GEMINI_API_KEYにGemini APIキーを設定
notepad .env
```

Windowsではdirenvが使用できないため、環境変数設定用のバッチファイルを作成しました。

## 設定後のフォルダ構成
```
C:\
└─ Meipu2-demo
      ├─ .venv\
      ├─ contents\
      ├─ dictation-kit\
      ├─ docs\
      ├─ meipu-contents\
      ├─ MMDAgent-EX
      │     ├─ MMDAgent-EX.exe
      │     ├─ AppData\
      │     ├─ DLLs\
      │     ├─ Plugins\
      │     └─ ...
      ├─ Record\
      ├─ .env
      ├─ .envrc.example
      ├─ core\
      │  └─ scripts\
      │     ├─ setup-env-windows.bat
      │     └─ julius-windows.bat
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
2つのPowerShellターミナルを使用します。
AとBと呼称します。


Aを立ち上げ、環境変数を設定してからJuliusを実行：
```powershell
# 任意のディレクトリ
cd C:\Meipu2-demo
.\core\scripts\setup-env-windows.bat
.\core\scripts\julius-windows.bat
```

Bを立ち上げ、環境変数を設定してからMMDAgent-EXを実行：
```powershell
# 任意のディレクトリ
cd C:\Meipu2-demo
.\core\scripts\setup-env-windows.bat
.\MMDAgent-EX\MMDAgent-EX.exe .\meipu-contents\main.mdf
```
を実行します。するとウィンドウが立ち上がるので、対話を開始してください。
