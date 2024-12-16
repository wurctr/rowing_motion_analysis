import cv2
from utils.landmarks import extract_landmarks
from utils.features import calculate_torso_angle, detect_stroke_cycles
from utils.drawing import draw_landmarks_with_skeleton

# 入力動画の読み込み
video_path = "data/input/rowing_video.mp4"
cap = cv2.VideoCapture(video_path)

# 出力動画の準備
output_path = "data/output/annotated_video.avi"
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = int(cap.get(cv2.CAP_PROP_FPS))
out = cv2.VideoWriter(output_path, cv2.VideoWriter_fourcc(*'XVID'), fps, (width, height))

# MediapipeのPose初期化
from mediapipe.solutions.pose import Pose
pose = Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # ランドマークの取得
    landmarks = extract_landmarks(frame, pose)
    if landmarks:
        # 特徴量の計算（例: 体幹の角度）
        torso_angle = calculate_torso_angle(landmarks)
        # 動画へのランドマークと骨格の描画
        frame = draw_landmarks_with_skeleton(frame, landmarks)

    # フレームを出力動画に保存
    out.write(frame)

cap.release()
out.release()
pose.close()
