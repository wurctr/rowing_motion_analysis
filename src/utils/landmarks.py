import mediapipe as mp
import math

mp_pose = mp.solutions.pose


def extract_landmarks(results):
    """
    Mediapipeのランドマークを抽出してリストに変換する関数。
    - results: MediapipeのPoseプロセス結果。
    - 返り値: ランドマークのリスト [(x1, y1, z1), (x2, y2, z2), ...]。
    """
    if not results.pose_landmarks:
        return None
    landmarks = []
    for lm in results.pose_landmarks.landmark:
        landmarks.append((lm.x, lm.y, lm.z))
    return landmarks


def get_single_pelvis_bounds(landmarks, side="right"):
    """
    横から見た骨盤を囲む四角形の座標を計算。
    - landmarks: Mediapipeのランドマークリスト。
    - side: "right"（右側）または "left"（左側）を指定。
    - 返り値: 骨盤を囲む四角形の頂点リスト [(x1, y1), (x2, y2), ...]。
    """
    if side == "right":
        hip = landmarks[24]  # 右骨盤
        shoulder = landmarks[12]  # 右肩
    elif side == "left":
        hip = landmarks[23]  # 左骨盤
        shoulder = landmarks[11]  # 左肩
    else:
        raise ValueError("Invalid side. Use 'right' or 'left'.")

    # 骨盤の高さを肩と骨盤の垂直距離の50%と仮定
    pelvis_height = abs(shoulder[1] - hip[1]) * 0.5

    # 四角形の頂点を計算
    top_left = (hip[0] - pelvis_height / 2, hip[1] - pelvis_height)
    top_right = (hip[0] + pelvis_height / 2, hip[1] - pelvis_height)
    bottom_left = (hip[0] - pelvis_height / 2, hip[1])
    bottom_right = (hip[0] + pelvis_height / 2, hip[1])

    return [top_left, top_right, bottom_left, bottom_right]


def calculate_pelvis_orientation(pelvis_bounds):
    """
    骨盤の向きを計算（水平軸からの角度）。
    - pelvis_bounds: 四角形の頂点リスト [(x1, y1), (x2, y2), ...]。
    - 返り値: 骨盤の傾き（角度、度単位）。
    """
    top_left, top_right, _, _ = pelvis_bounds

    # 水平軸との角度を計算
    dx = top_right[0] - top_left[0]
    dy = top_right[1] - top_left[1]
    angle = math.atan2(dy, dx) * (180 / math.pi)

    return angle
