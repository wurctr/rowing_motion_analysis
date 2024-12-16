import cv2


def draw_pelvis_bounds(image, pelvis_bounds, color=(0, 255, 255)):
    """
    骨盤を囲む四角形を描画。
    - image: 描画対象の画像（numpy array）。
    - pelvis_bounds: 骨盤を囲む四角形の頂点リスト [(x1, y1), (x2, y2), ...]。
    - color: 四角形の色 (B, G, R)。
    """
    top_left, top_right, bottom_left, bottom_right = pelvis_bounds

    # 四角形を描画
    cv2.line(image, (int(top_left[0]), int(top_left[1])), (int(top_right[0]), int(top_right[1])), color, 2)
    cv2.line(image, (int(top_right[0]), int(top_right[1])), (int(bottom_right[0]), int(bottom_right[1])), color, 2)
    cv2.line(image, (int(bottom_right[0]), int(bottom_right[1])), (int(bottom_left[0]), int(bottom_left[1])), color, 2)
    cv2.line(image, (int(bottom_left[0]), int(bottom_left[1])), (int(top_left[0]), int(top_left[1])), color, 2)

    return image


def draw_landmarks(image, landmarks, connections=None, color=(0, 255, 0)):
    """
    ランドマークを画像上に描画。
    - image: 描画対象の画像。
    - landmarks: ランドマークのリスト [(x1, y1), (x2, y2), ...]。
    - connections: ランドマーク間の接続リスト [(start_idx, end_idx), ...]。
    - color: 描画する色。
    """
    for idx, lm in enumerate(landmarks):
        x, y = int(lm[0]), int(lm[1])
        cv2.circle(image, (x, y), 5, color, -1)

    if connections:
        for start_idx, end_idx in connections:
            start_point = (int(landmarks[start_idx][0]), int(landmarks[start_idx][1]))
            end_point = (int(landmarks[end_idx][0]), int(landmarks[end_idx][1]))
            cv2.line(image, start_point, end_point, color, 2)

    return image
