import mediapipe as mp

mp_pose = mp.solutions.pose

def extract_landmarks(frame, pose):
    """Mediapipe Poseでランドマークを取得"""
    results = pose.process(frame)
    if results.pose_landmarks:
        return results.pose_landmarks.landmark
    return None
