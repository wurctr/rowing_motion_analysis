# ベースイメージとしてpython:3.10-slimを使用
# slimは軽量なDebianベースイメージ
FROM python:3.10-slim

# 作業ディレクトリを/appに設定
WORKDIR /app

# システムパッケージのインストール
# mediapipeやopencvが動作するために必要なライブラリをインストール
# libglib2.0-0などはcv2が動作するために必要な場合あり
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    libsm6 \
    libxext6 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# requirements.txtをコンテナにコピー
COPY requirements.txt .

# Pythonパッケージをインストール
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションソースをコンテナにコピー
COPY . .

# Flaskアプリケーションが動作するホストとポートを環境変数で指定
# 例: Flask標準の開発サーバーを使用、ポート5000で起動
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=5000
ENV DEBUG=False

# ホスト側からコンテナへのポートマッピング用
EXPOSE 5000

# コンテナ起動時に実行するコマンド
# 本番環境では、gunicornなどのWSGIサーバーを使用するとよい。
CMD ["flask", "run"]
