import cv2


def draw_landmarks(image, landmarks, connections=None, color=(0, 255, 0)):
    """
    ランドマークを画像上に描画。
    - image: 描画対象の画像。
    - landmarks: ランドマークのリスト [(x1, y1), (x2, y2), ...]。
    - connections: ランドマーク間の接続リスト [(start_idx, end_idx), ...]。
    - color: 描画する色。
    """
    for idx, lm in enumerate(landmarks):
        x, y = int(lm[0] * image.shape[1]), int(lm[1] * image.shape[0])
        cv2.circle(image, (x, y), 5, color, -1)

    if connections:
        for start_idx, end_idx in connections:
            start_point = (
                int(landmarks[start_idx][0] * image.shape[1]),
                int(landmarks[start_idx][1] * image.shape[0]),
            )
            end_point = (
                int(landmarks[end_idx][0] * image.shape[1]),
                int(landmarks[end_idx][1] * image.shape[0]),
            )
            cv2.line(image, start_point, end_point, color, 2)

    return image


def draw_pelvis_bounds(image, pelvis_bounds, color=(0, 255, 255)):
    """
    骨盤を囲む四角形を描画。
    - image: 描画対象の画像（numpy array）。
    - pelvis_bounds: 骨盤を囲む四角形の頂点リスト [(x1, y1), (x2, y2), ...]。
    - color: 四角形の色 (B, G, R)。
    """
    top_left, top_right, bottom_left, bottom_right = pelvis_bounds

    # 四角形を描画
    def scale_coordinates(point, image_shape):
        return (int(point[0] * image_shape[1]), int(point[1] * image_shape[0]))

    top_left = scale_coordinates(top_left, image.shape)
    top_right = scale_coordinates(top_right, image.shape)
    bottom_left = scale_coordinates(bottom_left, image.shape)
    bottom_right = scale_coordinates(bottom_right, image.shape)

    cv2.line(image, top_left, top_right, color, 2)
    cv2.line(image, top_right, bottom_right, color, 2)
    cv2.line(image, bottom_right, bottom_left, color, 2)
    cv2.line(image, bottom_left, top_left, color, 2)

    return image


def draw_pelvis_orientation(image, pelvis_angle, position=(50, 50), color=(255, 0, 0)):
    """
    骨盤の向きを画像上に描画。
    - image: 描画対象の画像（numpy array）。
    - pelvis_angle: 骨盤の傾き（角度）。
    - position: テキストを描画する位置（x, y）。
    - color: テキストの色 (B, G, R)。
    """
    cv2.putText(
        image,
        f"Pelvis Angle: {pelvis_angle:.2f} degrees",
        position,
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        color,
        2,
    )
    return image
