import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')
OUTPUT_FOLDER = os.path.join(BASE_DIR, 'static', 'output')
RESULTS_CSV = os.path.join(BASE_DIR, 'analysis_results.csv')

# ログ設定
LOG_FILE = os.path.join(BASE_DIR, 'app.log')
