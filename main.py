import cv2
import mediapipe as mp
import csv

# MediaPipe Poseセットアップ
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()
mp_drawing = mp.solutions.drawing_utils

# 動画読み込み
video_path = "data/rowing_video.mp4"
cap = cv2.VideoCapture(video_path)

# CSVファイルに保存
csv_file = open("outputs/landmarks.csv", "w", newline="")
csv_writer = csv.writer(csv_file)
csv_writer.writerow(["frame", "landmark", "x", "y", "z", "visibility"])

frame_count = 0
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # フレームをRGBに変換
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = pose.process(rgb_frame)

    # 骨格ランドマークを取得
    if result.pose_landmarks:
        for i, landmark in enumerate(result.pose_landmarks.landmark):
            csv_writer.writerow([frame_count, i, landmark.x, landmark.y, landmark.z, landmark.visibility])

    # 骨格描画
    if result.pose_landmarks:
        mp_drawing.draw_landmarks(frame, result.pose_landmarks, mp_pose.POSE_CONNECTIONS)

    frame_count += 1

cap.release()
csv_file.close()
