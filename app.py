import os
import cv2
import math
import mediapipe as mp
import csv
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from src.utils.landmarks import extract_landmarks, get_single_pelvis_bounds, calculate_pelvis_orientation
from src.utils.drawing import draw_landmarks, draw_pelvis_bounds, draw_pelvis_orientation
from src.utils.features import calculate_joint_angles, calculate_stroke_cycle

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['OUTPUT_FOLDER'] = 'static/output'
app.config['RESULTS_CSV'] = 'analysis_results.csv'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

mp_pose = mp.solutions.pose

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'file' not in request.files or 'player' not in request.form:
            return "Missing form data", 400
        
        file = request.files['file']
        player = request.form['player']
        
        if file.filename == '':
            return "No selected file", 400
        
        # 動画ファイルを保存
        input_filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(input_filepath)

        # 解析結果取得
        analysis_results = run_analysis(input_filepath, player)
        return redirect(url_for('processed', filename=analysis_results['output_filename']))

    return render_template('index.html')

@app.route('/processed/<filename>')
def processed(filename):
    record = find_record_by_filename(filename)
    if not record:
        return "No results found for this video.", 404

    # CSVヘッダー: ["timestamp", "filename", "player", "stroke_cycle_time", "pelvis_angle", "knee_angle", "ankle_angle"]
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
    if os.path.exists(app.config['RESULTS_CSV']):
        return send_from_directory('.', app.config['RESULTS_CSV'], as_attachment=True)
    else:
        return "No analysis results found.", 404

def run_analysis(input_filepath, player):
    pose = mp_pose.Pose(static_image_mode=False, min_detection_confidence=0.5, min_tracking_confidence=0.5)
    cap = cv2.VideoCapture(input_filepath)
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    base_name = os.path.splitext(os.path.basename(input_filepath))[0]
    output_filename = base_name + '_annotated.avi'
    output_filepath = os.path.join(app.config['OUTPUT_FOLDER'], output_filename)
    out = cv2.VideoWriter(output_filepath, cv2.VideoWriter_fourcc(*"XVID"), fps, (width, height))

    wrist_y_coords = []
    pelvis_angle_avg = []
    knee_angle_avg = []
    ankle_angle_avg = []  # 足首角度蓄積用

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose.process(rgb_frame)
        landmarks = extract_landmarks(results)

        if landmarks:
            wrist_y_coords.append(landmarks[15][1])
            pelvis_bounds = get_single_pelvis_bounds(landmarks, side="right")
            pelvis_angle = calculate_pelvis_orientation(pelvis_bounds)
            pelvis_angle_avg.append(pelvis_angle)

            joint_angles = calculate_joint_angles(landmarks)
            # 膝角度・足首角度を蓄積
            if joint_angles["knee"] is not None:
                knee_angle_avg.append(joint_angles["knee"])
            if joint_angles["ankle"] is not None:
                ankle_angle_avg.append(joint_angles["ankle"])

            # 描画
            frame = draw_pelvis_bounds(frame, pelvis_bounds)
            frame = draw_pelvis_orientation(frame, pelvis_angle)
            # 膝角度表示
            if joint_angles["knee"] is not None:
                cv2.putText(frame, f"Knee Angle: {joint_angles['knee']:.2f} deg", (50, 100), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
            # 足首角度表示（任意）
            if joint_angles["ankle"] is not None:
                cv2.putText(frame, f"Ankle Angle: {joint_angles['ankle']:.2f} deg", (50, 140), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2)

            connections = [(12, 24), (24, 26), (26, 28)]
            frame = draw_landmarks(frame, landmarks, connections)

        out.write(frame)

    cap.release()
    out.release()
    pose.close()

    stroke_cycle_time = None
    if wrist_y_coords:
        stroke_cycle_time = calculate_stroke_cycle([(0, y) for y in wrist_y_coords], fps)

    avg_pelvis_angle = sum(pelvis_angle_avg) / len(pelvis_angle_avg) if pelvis_angle_avg else 0
    avg_knee_angle = sum(knee_angle_avg) / len(knee_angle_avg) if knee_angle_avg else 0
    avg_ankle_angle = sum(ankle_angle_avg) / len(ankle_angle_avg) if ankle_angle_avg else 0

    analysis_results = {
        "timestamp": datetime.now().isoformat(),
        "input_filename": os.path.basename(input_filepath),
        "output_filename": output_filename,
        "player": player,
        "stroke_cycle_time": stroke_cycle_time if stroke_cycle_time else 0,
        "pelvis_angle": avg_pelvis_angle,
        "knee_angle": avg_knee_angle,
        "ankle_angle": avg_ankle_angle
    }

    write_results_to_csv(analysis_results)
    return analysis_results

def write_results_to_csv(results_dict):
    file_exists = os.path.exists(app.config['RESULTS_CSV'])
    with open(app.config['RESULTS_CSV'], 'a', newline='') as f:
        writer = csv.writer(f)
        if not file_exists:
            # CSVヘッダーにankle_angleを追加
            writer.writerow(["timestamp", "filename", "player", "stroke_cycle_time", "pelvis_angle", "knee_angle", "ankle_angle"])
        writer.writerow([
            results_dict["timestamp"],
            results_dict["output_filename"],
            results_dict["player"],
            results_dict["stroke_cycle_time"],
            results_dict["pelvis_angle"],
            results_dict["knee_angle"],
            results_dict["ankle_angle"]
        ])

def find_record_by_filename(filename):
    if not os.path.exists(app.config['RESULTS_CSV']):
        return None
    with open(app.config['RESULTS_CSV'], 'r', newline='') as f:
        reader = csv.reader(f)
        header = next(reader, None)
        if header is None:
            return None
        for row in reader:
            if row[1] == filename:
                return row
    return None

if __name__ == "__main__":
    app.run(debug=True)
