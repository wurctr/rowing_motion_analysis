import math

def calculate_torso_angle(landmarks):
    """頭、肩、骨盤のランドマークから体幹の角度を計算"""
    head = (landmarks[0].x, landmarks[0].y)
    shoulder = (landmarks[11].x, landmarks[11].y)
    pelvis_center = (
        (landmarks[23].x + landmarks[24].x) / 2, 
        (landmarks[23].y + landmarks[24].y) / 2
    )
    dx1, dy1 = head[0] - shoulder[0], head[1] - shoulder[1]
    dx2, dy2 = pelvis_center[0] - shoulder[0], pelvis_center[1] - shoulder[1]
    angle = math.atan2(dy1, dx1) - math.atan2(dy2, dx2)
    return abs(math.degrees(angle))

def detect_stroke_cycles(wrist_x_coords, fps):
    """手首の動きからストロークサイクルを検出"""
    cycles = []
    last_catch_frame = None
    for frame_idx, wrist_x in enumerate(wrist_x_coords):
        if last_catch_frame is None or wrist_x < 0.2:  # 条件は調整可能
            if last_catch_frame is not None:
                cycle_time = (frame_idx - last_catch_frame) / fps
                cycles.append(cycle_time)
            last_catch_frame = frame_idx
    return cycles
