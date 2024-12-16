import logging
import os
import uuid
from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from config import UPLOAD_FOLDER, OUTPUT_FOLDER, RESULTS_CSV, LOG_FILE
from src.services.analysis_service import analyze_video, find_record_by_filename
from werkzeug.utils import secure_filename

app = Flask(__name__)

# ロギング設定
logging.basicConfig(filename=LOG_FILE, level=logging.INFO,
                    format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

# ディレクトリ作成
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file = request.files.get('file')
        player = request.form.get('player')
        
        if not file or not player:
            logger.warning("Missing file or player input")
            return render_template('error.html', message="Missing file or player name."), 400

        if file.filename == '':
            logger.warning("Empty filename uploaded")
            return render_template('error.html', message="No selected file."), 400

        if not allowed_file(file.filename):
            logger.warning(f"Unsupported file type: {file.filename}")
            return render_template('error.html', message="Unsupported file format. Use mp4, avi, or mov."), 400

        # ファイル名をユニーク化
        ext = file.filename.rsplit('.', 1)[1].lower()
        unique_name = f"{uuid.uuid4().hex}.{ext}"
        input_filepath = os.path.join(UPLOAD_FOLDER, secure_filename(unique_name))
        file.save(input_filepath)

        # 解析実行
        try:
            analysis_results = analyze_video(input_filepath, player, OUTPUT_FOLDER, RESULTS_CSV)
        except Exception as e:
            logger.exception("Error during analysis")
            return render_template('error.html', message=f"An error occurred during analysis: {str(e)}"), 500

        return redirect(url_for('processed', filename=analysis_results['output_filename']))
    return render_template('index.html')

@app.route('/processed/<filename>')
def processed(filename):
    record = find_record_by_filename(filename, RESULTS_CSV)
    if not record:
        logger.warning(f"No results found for {filename}")
        return render_template('error.html', message="No results found for this video."), 404

    analysis_data = {
        "timestamp": record[0],
        "filename": record[1],
        "player": record[2],
        "stroke_cycle_time": record[3],
        "pelvis_angle": record[4],
        "knee_angle": record[5],
        "ankle_angle": record[6]
    }

    video_url = url_for('static', filename='output/' + filename)
    return render_template('processed.html', video_url=video_url, analysis=analysis_data)

@app.route('/download_results')
def download_results():
    if os.path.exists(RESULTS_CSV):
        return send_from_directory('.', os.path.basename(RESULTS_CSV), as_attachment=True)
    else:
        return render_template('error.html', message="No analysis results found."), 404

if __name__ == "__main__":
    app.run(debug=False)  # 本番ではdebug=False
