# sbv2_dataset_editor

## セットアップ
このプロジェクトでは、Pythonのパッケージ管理に uv を使用しています。以下の手順で簡単に環境を構築できます。

1. リポジトリのクローン
本リポジトリをローカルにコピーし、ディレクトリに移動します。

```Bash
git clone https://github.com/あなたのユーザー名/リポジトリ名.git
cd リポジトリ名
```

2. 環境構築（同期）
以下のコマンドを実行するだけで、適切な Python バージョンのダウンロード、仮想環境（.venv）の作成、および依存ライブラリのインストールが自動的に行われます。

```Bash
uv sync
```
3. プログラムの実行
環境が構築できたら、uv run コマンドを使ってプログラムを実行できます。これにより、自動的に仮想環境内の Python が使用されます。

```Bash
# 例: main.py を実行する場合
uv run main.py
```
また、仮想環境の中に入って作業したい場合は、以下のコマンドを使用してください。

```Bash
# 仮想環境を有効化
source .venv/bin/activate  # macOS / Linux
.venv\Scripts\activate     # Windows
```
