import cv2

def draw_landmarks_with_skeleton(frame, landmarks):
    """ランドマークと骨格を描画"""
    for lm in landmarks:
        x, y = int(lm.x * frame.shape[1]), int(lm.y * frame.shape[0])
        cv2.circle(frame, (x, y), 5, (0, 255, 0), -1)

    # 骨格の例: 肩 - 肘 - 手首
    connections = [(11, 13), (13, 15)]  # Mediapipeのランドマーク番号
    for start, end in connections:
        start_point = (int(landmarks[start].x * frame.shape[1]), int(landmarks[start].y * frame.shape[0]))
        end_point = (int(landmarks[end].x * frame.shape[1]), int(landmarks[end].y * frame.shape[0]))
        cv2.line(frame, start_point, end_point, (255, 0, 0), 2)

    return frame
