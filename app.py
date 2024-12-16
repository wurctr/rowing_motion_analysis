import os
import cv2
import math
import mediapipe as mp
from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from src.utils.landmarks import extract_landmarks, get_single_pelvis_bounds, calculate_pelvis_orientation
from src.utils.drawing import draw_landmarks, draw_pelvis_bounds, draw_pelvis_orientation
from src.utils.features import calculate_joint_angles, calculate_stroke_cycle

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['OUTPUT_FOLDER'] = 'static/output'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

mp_pose = mp.solutions.pose

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # ファイルがアップロードされたかチェック
        if 'file' not in request.files:
            return "No file part", 400
        file = request.files['file']
        if file.filename == '':
            return "No selected file", 400
        
        # ファイルを保存
        input_filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(input_filepath)

        # アップロードされた動画を解析
        output_filename = run_analysis(input_filepath)
        return redirect(url_for('processed', filename=output_filename))
    return render_template('index.html')

@app.route('/processed/<filename>')
def processed(filename):
    # 解析済み動画の表示ページ
    return render_template('processed.html', video_url=url_for('static', filename='output/' + filename))

def run_analysis(input_filepath):
    """
    アップロードされた動画を解析し、解析済み動画を出力する関数。
    """
    # Mediapipeの初期化
    pose = mp_pose.Pose(static_image_mode=False, min_detection_confidence=0.5, min_tracking_confidence=0.5)

    cap = cv2.VideoCapture(input_filepath)
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # 出力ファイル名の生成
    base_name = os.path.splitext(os.path.basename(input_filepath))[0]
    output_filename = base_name + '_annotated.avi'
    output_filepath = os.path.join(app.config['OUTPUT_FOLDER'], output_filename)

    out = cv2.VideoWriter(output_filepath, cv2.VideoWriter_fourcc(*"XVID"), fps, (width, height))

    wrist_y_coords = []

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose.process(rgb_frame)
        landmarks = extract_landmarks(results)

        if landmarks:
            # 手首のY座標を記録（右手首: index=15）
            wrist_y_coords.append(landmarks[15][1])

            # 骨盤の四角形・向き
            pelvis_bounds = get_single_pelvis_bounds(landmarks, side="right")
            pelvis_angle = calculate_pelvis_orientation(pelvis_bounds)

            # 関節角度計算（例: 膝角度）
            joint_angles = calculate_joint_angles(landmarks)

            # 骨盤、ランドマーク、角度を描画
            frame = draw_pelvis_bounds(frame, pelvis_bounds)
            frame = draw_pelvis_orientation(frame, pelvis_angle)
            cv2.putText(frame, f"Knee Angle: {joint_angles['knee']:.2f} deg", (50, 100), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

            # 接続例（右肩-骨盤-膝-足首）
            connections = [(12, 24), (24, 26), (26, 28)]
            frame = draw_landmarks(frame, landmarks, connections)

        out.write(frame)

    cap.release()
    out.release()
    pose.close()

    # ストロークサイクル計算
    if wrist_y_coords:
        stroke_cycle_time = calculate_stroke_cycle([(0, y) for y in wrist_y_coords], fps)
        print(f"Average Stroke Cycle Time: {stroke_cycle_time:.2f} seconds")

    return output_filename

if __name__ == "__main__":
    app.run(debug=True)
