# Rowing Motion Analysis
This project analyzes rowing motion using Python and MediaPipe. 
Features include pose detection, motion tracking, and stroke cycle analysis.
## 概要
ローイングの動作解析を行うアプリケーション。真横からの動画を入力し、以下のデータを計測します。
- 体幹の角度変化
- ストロークサイクルの時間
- 股関節の可動域など

## 構成
- `src/main.py`: 実行用スクリプト
- `src/utils/landmarks.py`: ランドマーク検出モジュール
- `src/utils/features.py`: 特徴量計算モジュール
- `src/utils/drawing.py`: 描画モジュール

## 実行方法
1. 必要なパッケージをインストール:
   ```bash
   pip install -r requirements.txt
2.	動画を data/input/ に保存。
3.	実行: python src/main.py

rowing-analysis/
├── src/
│   ├── main.py               # メイン実行ファイル（エントリーポイント）
│   ├── utils/
│   │   ├── landmarks.py      # ランドマーク検出関連の処理
│   │   ├── features.py       # 特徴量計算関連の処理
│   │   ├── drawing.py        # 描画・動画作成関連の処理
│   │   └── gui.py            # 手動調整用GUI関連の処理
├── data/
│   ├── input/                # 入力動画の保存先
│   └── output/               # 解析済み動画の保存先
├── requirements.txt          # 必要なPythonパッケージのリスト
├── README.md                 # プロジェクトの概要・使い方説明
└── .gitignore                # Gitで無視するファイルリスト
