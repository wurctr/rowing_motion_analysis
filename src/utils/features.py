import math

def calculate_angle(p1, p2, p3):
    """
    3つの座標から角度を計算（単位: 度）。
    - p1, p2, p3: (x, y)形式のタプル。p2が頂点となる。
    """
    dx1, dy1 = p1[0] - p2[0], p1[1] - p2[1]
    dx2, dy2 = p3[0] - p2[0], p3[1] - p2[1]
    angle = math.atan2(dy1, dx1) - math.atan2(dy2, dx2)
    angle = math.degrees(angle)
    return abs(angle)  # 絶対値を返す


def calculate_torso_angle(landmarks):
    """
    体幹（頭、肩、骨盤）の角度を計算。
    - landmarks: Mediapipeのランドマークリスト。
    """
    head = (landmarks[0].x, landmarks[0].y)
    shoulder = (landmarks[11].x, landmarks[11].y)
    pelvis_center = (
        (landmarks[23].x + landmarks[24].x) / 2,
        (landmarks[23].y + landmarks[24].y) / 2
    )
    return calculate_angle(head, shoulder, pelvis_center)


def calculate_joint_angles(landmarks):
    """
    足首・膝・股関節の角度を計算。
    - landmarks: Mediapipeのランドマークリスト。
    - 返り値: 関節角度の辞書。
    """
    hip = (landmarks[23].x, landmarks[23].y)  # 股関節
    knee = (landmarks[25].x, landmarks[25].y)  # 膝
    ankle = (landmarks[27].x, landmarks[27].y)  # 足首

    # 股関節角度（肩, 骨盤, 膝を結ぶ角度）
    shoulder = (landmarks[11].x, landmarks[11].y)
    hip_angle = calculate_angle(shoulder, hip, knee)

    # 膝角度（骨盤, 膝, 足首を結ぶ角度）
    knee_angle = calculate_angle(hip, knee, ankle)

    # 足首角度（膝, 足首, 地面水平）
    ground_level = (ankle[0] + 0.1, ankle[1])  # 水平線の仮定座標
    ankle_angle = calculate_angle(knee, ankle, ground_level)

    return {
        "hip_angle": hip_angle,
        "knee_angle": knee_angle,
        "ankle_angle": ankle_angle
    }


def detect_stroke_cycles(wrist_x_coords, fps):
    """
    手首のX座標を元にストロークサイクルを検出。
    - wrist_x_coords: 各フレームにおける手首のX座標リスト。
    - fps: 動画のフレームレート。
    - 返り値: 各ストロークサイクルの時間リスト（秒）。
    """
    cycles = []
    last_catch_frame = None
    for frame_idx, wrist_x in enumerate(wrist_x_coords):
        # "キャッチ動作"の検出（例: 手首X座標が一定の閾値を超える場合）
        if last_catch_frame is None or wrist_x < 0.2:  # 条件は調整可能
            if last_catch_frame is not None:
                cycle_time = (frame_idx - last_catch_frame) / fps
                cycles.append(cycle_time)
            last_catch_frame = frame_idx
    return cycles


def calculate_pelvis_orientation(landmarks):
    """
    骨盤の向きを計算。
    - landmarks: Mediapipeのランドマークリスト。
    - 返り値: 骨盤の傾き（度）。
    """
    left_pelvis = (landmarks[23].x, landmarks[23].y)
    right_pelvis = (landmarks[24].x, landmarks[24].y)
    
    # 左右の骨盤を結ぶ線が地面に対してなす角度を計算
    dx = right_pelvis[0] - left_pelvis[0]
    dy = right_pelvis[1] - left_pelvis[1]
    angle = math.atan2(dy, dx)
    return math.degrees(angle)


def detect_joint_freeze_time(landmarks, fps, threshold=5):
    """
    足首・膝・股関節の可動域が閾値以下に収まるまでの時間を計算。
    - landmarks: Mediapipeのランドマークリスト。
    - fps: 動画のフレームレート。
    - threshold: 関節の角度変化を検出する閾値（度単位）。
    - 返り値: 各関節の停止時間（秒）。
    """
    joint_angles_over_time = []  # 時系列で各関節の角度を記録
    freeze_times = {"hip": 0, "knee": 0, "ankle": 0}

    for frame_idx in range(len(landmarks)):
        angles = calculate_joint_angles(landmarks[frame_idx])
        joint_angles_over_time.append(angles)

        for joint, angle in angles.items():
            if abs(angle) < threshold:  # 閾値以下のとき停止時間を加算
                freeze_times[joint] += 1 / fps

    return freeze_times
