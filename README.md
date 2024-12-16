# Rowing Motion Analysis
This project analyzes rowing motion using Python and MediaPipe. 
Features include pose detection, motion tracking, and stroke cycle analysis.

## 概要
ローイングの動作解析を行うアプリケーション。真横からの動画を入力し、以下のデータを計測します。
- 体幹の角度変化
- ストロークサイクルの時間
- 股関節の可動域など

## 構成
- `app.py`: 実行用スクリプト
- `src/utils/landmarks.py`: ランドマーク検出モジュール
- `src/utils/features.py`: 特徴量計算モジュール
- `src/utils/drawing.py`: 描画モジュール

rowing-analysis-web/
├── app.py
├── src/
│   ├── utils/
│   │   ├── landmarks.py
│   │   ├── drawing.py
│   │   ├── features.py
│   └── __init__.py
├── static/
│   ├── output/
│   │   └── (解析後の動画ファイルがここに出力される)
│   └── ...
└── templates/
    └── index.html
