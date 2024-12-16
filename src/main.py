import cv2
import mediapipe as mp
from landmarks import extract_landmarks, get_single_pelvis_bounds, calculate_pelvis_orientation
from drawing import draw_landmarks, draw_pelvis_bounds, draw_pelvis_orientation
from features import calculate_joint_angles, calculate_stroke_cycle

# Mediapipe Poseの初期化
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(static_image_mode=False, min_detection_confidence=0.5, min_tracking_confidence=0.5)

# 動画ファイルのパス
video_path = "data/input/rowing_video.mp4"
output_path = "data/output/annotated_video.avi"

# 動画読み込み
cap = cv2.VideoCapture(video_path)
fps = int(cap.get(cv2.CAP_PROP_FPS))
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

# 出力動画の設定
out = cv2.VideoWriter(output_path, cv2.VideoWriter_fourcc(*"XVID"), fps, (width, height))

# 手首のy座標を記録するリスト（ストロークサイクル計測用）
wrist_y_coords = []

# メイン処理ループ
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # Mediapipeでランドマークを検出
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = pose.process(rgb_frame)
    landmarks = extract_landmarks(results)

    if landmarks:
        # 手首の座標を記録
        wrist_y_coords.append(landmarks[15][1])  # 右手首（左手首なら landmarks[16]）

        # 骨盤の四角形と向きの計算
        pelvis_bounds = get_single_pelvis_bounds(landmarks, side="right")
        pelvis_angle = calculate_pelvis_orientation(pelvis_bounds)

        # 関節角度の計算
        joint_angles = calculate_joint_angles(landmarks)

        # 骨盤の四角形を描画
        frame = draw_pelvis_bounds(frame, pelvis_bounds)

        # 骨盤の向きを描画
        frame = draw_pelvis_orientation(frame, pelvis_angle)

        # 関節角度の描画（例: 膝の角度）
        cv2.putText(frame, f"Knee Angle: {joint_angles['knee']:.2f} deg", (50, 100), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

        # ランドマークと骨格を描画
        connections = [(12, 24), (24, 26), (26, 28)]  # 右肩-骨盤-膝-足首
        frame = draw_landmarks(frame, landmarks, connections)

    # フレームを出力動画に保存
    out.write(frame)

    # 結果をリアルタイム表示（任意）
    cv2.imshow("Rowing Analysis", frame)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

# ストロークサイクルの計算
if wrist_y_coords:
    stroke_cycle_time = calculate_stroke_cycle([(0, y) for y in wrist_y_coords], fps)
    print(f"Average Stroke Cycle Time: {stroke_cycle_time:.2f} seconds")

# リソース解放
cap.release()
out.release()
pose.close()
cv2.destroyAllWindows()
