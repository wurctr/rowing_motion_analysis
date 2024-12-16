import math
from landmarks import calculate_pelvis_orientation, get_single_pelvis_bounds


def analyze_pelvis_movement(landmarks, side="right"):
    """
    骨盤の動き（向きの角度）を解析する関数。
    - landmarks: Mediapipeのランドマークリスト。
    - side: "right"または"left"を指定。
    - 返り値: 骨盤の角度（度単位）と骨盤四角形の座標。
    """
    # 骨盤の四角形を計算
    pelvis_bounds = get_single_pelvis_bounds(landmarks, side=side)

    # 骨盤の角度を計算
    angle = calculate_pelvis_orientation(pelvis_bounds)

    return angle, pelvis_bounds


def calculate_joint_angles(landmarks):
    """
    各関節（膝、股関節、足首）の角度を計算。
    - landmarks: Mediapipeのランドマークリスト。
    - 返り値: 辞書形式で関節の角度。
        {"knee": knee_angle, "hip": hip_angle, "ankle": ankle_angle}
    """
    def calculate_angle(a, b, c):
        """
        三点間の角度を計算。
        - a, b, c: 各点の座標 (x, y)。
        - 返り値: 角度（度単位）。
        """
        ba = (a[0] - b[0], a[1] - b[1])  # ベクトルBA
        bc = (c[0] - b[0], c[1] - b[1])  # ベクトルBC
        dot_product = ba[0] * bc[0] + ba[1] * bc[1]
        magnitude_ba = math.sqrt(ba[0] ** 2 + ba[1] ** 2)
        magnitude_bc = math.sqrt(bc[0] ** 2 + bc[1] ** 2)
        if magnitude_ba == 0 or magnitude_bc == 0:
            return None  # 計算不能の場合
        cos_angle = dot_product / (magnitude_ba * magnitude_bc)
        angle = math.acos(max(min(cos_angle, 1.0), -1.0)) * (180 / math.pi)
        return angle

    # 膝の角度（股関節-膝-足首）
    knee_angle = calculate_angle(landmarks[24], landmarks[26], landmarks[28])  # 右側の場合
    # 股関節の角度（肩-骨盤-膝）
    hip_angle = calculate_angle(landmarks[12], landmarks[24], landmarks[26])  # 右側の場合
    # 足首の角度（膝-足首-つま先）
    ankle_angle = calculate_angle(landmarks[26], landmarks[28], landmarks[32])  # 右側の場合

    return {"knee": knee_angle, "hip": hip_angle, "ankle": ankle_angle}


def calculate_stroke_cycle(hand_landmarks, fps):
    """
    手首の座標からストロークサイクルの時間を計算。
    - hand_landmarks: Mediapipeの手首ランドマークリスト [(x1, y1), ...]。
    - fps: 動画のフレームレート。
    - 返り値: ストロークサイクルの時間（秒）。
    """
    # y座標の変動（上下運動）を基にピークを検出
    y_coords = [hand[1] for hand in hand_landmarks]
    peaks = []
    for i in range(1, len(y_coords) - 1):
        if y_coords[i] < y_coords[i - 1] and y_coords[i] < y_coords[i + 1]:  # ピーク検出
            peaks.append(i)

    # ピーク間の平均フレーム数を計算
    if len(peaks) < 2:
        return None  # ピークが少なすぎる場合
    average_peak_distance = sum(peaks[i] - peaks[i - 1] for i in range(1, len(peaks))) / (len(peaks) - 1)

    # フレーム数から秒数に変換
    stroke_cycle_time = average_peak_distance / fps

    return stroke_cycle_time


def analyze_leg_movement(landmarks):
    """
    膝、足首、股関節の可動域拡大が止まるまでの時間を計算。
    - landmarks: Mediapipeのランドマークリスト。
    - 返り値: 辞書形式で各可動域の変化時間。
        {"knee_time": t_knee, "hip_time": t_hip, "ankle_time": t_ankle}
    """
    # TODO: 動画の時間情報を受け取りながらフレームごとに解析を行う（未実装の部分）。
    pass
