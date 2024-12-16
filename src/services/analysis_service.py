import os
import csv
import logging
from datetime import datetime
import cv2
import mediapipe as mp
from src.utils.landmarks import extract_landmarks, get_single_pelvis_bounds, calculate_pelvis_orientation
from src.utils.drawing import draw_landmarks, draw_pelvis_bounds, draw_pelvis_orientation
from src.utils.features import calculate_joint_angles, calculate_stroke_cycle

logger = logging.getLogger(__name__)
mp_pose = mp.solutions.pose

def analyze_video(input_filepath, player, output_folder, results_csv):
    if not os.path.exists(input_filepath):
        raise FileNotFoundError("Input video file not found.")

    cap = cv2.VideoCapture(input_filepath)
    fps = cap.get(cv2.CAP_PROP_FPS)
    if fps <= 0:
        raise ValueError("Invalid FPS or unable to read video.")

    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    base_name = os.path.splitext(os.path.basename(input_filepath))[0]
    output_filename = base_name + '_annotated.avi'
    output_filepath = os.path.join(output_folder, output_filename)

    out = cv2.VideoWriter(output_filepath, cv2.VideoWriter_fourcc(*"XVID"), fps, (width, height))
    pose = mp_pose.Pose(static_image_mode=False, min_detection_confidence=0.5, min_tracking_confidence=0.5)

    wrist_y_coords = []
    pelvis_angle_avg = []
    knee_angle_avg = []
    ankle_angle_avg = []

    frame_count = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frame_count += 1

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose.process(rgb_frame)
        landmarks = extract_landmarks(results)

        if landmarks:
            wrist_y_coords.append(landmarks[15][1])
            pelvis_bounds = get_single_pelvis_bounds(landmarks, side="right")
            pelvis_angle = calculate_pelvis_orientation(pelvis_bounds)
            pelvis_angle_avg.append(pelvis_angle)

            joint_angles = calculate_joint_angles(landmarks)
            if joint_angles["knee"] is not None:
                knee_angle_avg.append(joint_angles["knee"])
            if joint_angles["ankle"] is not None:
                ankle_angle_avg.append(joint_angles["ankle"])

            frame = draw_pelvis_bounds(frame, pelvis_bounds)
            frame = draw_pelvis_orientation(frame, pelvis_angle)
            if joint_angles["knee"] is not None:
                cv2.putText(frame, f"Knee: {joint_angles['knee']:.2f} deg", (50, 100),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
            if joint_angles["ankle"] is not None:
                cv2.putText(frame, f"Ankle: {joint_angles['ankle']:.2f} deg", (50, 140),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2)

            connections = [(12, 24), (24, 26), (26, 28)]
            frame = draw_landmarks(frame, landmarks, connections)

        out.write(frame)

    cap.release()
    out.release()
    pose.close()

    if len(wrist_y_coords) == 0:
        raise ValueError("No valid landmarks detected. Possibly not a rowing video or detection failed.")

    stroke_cycle_time = calculate_stroke_cycle([(0, y) for y in wrist_y_coords], fps) if wrist_y_coords else 0
    avg_pelvis_angle = sum(pelvis_angle_avg) / len(pelvis_angle_avg) if pelvis_angle_avg else 0
    avg_knee_angle = sum(knee_angle_avg) / len(knee_angle_avg) if knee_angle_avg else 0
    avg_ankle_angle = sum(ankle_angle_avg) / len(ankle_angle_avg) if ankle_angle_avg else 0

    analysis_results = {
        "timestamp": datetime.now().isoformat(),
        "input_filename": os.path.basename(input_filepath),
        "output_filename": output_filename,
        "player": player,
        "stroke_cycle_time": stroke_cycle_time if stroke_cycle_time else 0,
        "pelvis_angle": avg_pelvis_angle,
        "knee_angle": avg_knee_angle,
        "ankle_angle": avg_ankle_angle
    }

    write_results_to_csv(analysis_results, results_csv)
    logger.info(f"Analysis complete for {input_filepath}: {analysis_results}")
    return analysis_results

def write_results_to_csv(results_dict, results_csv):
    file_exists = os.path.exists(results_csv)
    with open(results_csv, 'a', newline='') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["timestamp", "filename", "player", "stroke_cycle_time", "pelvis_angle", "knee_angle", "ankle_angle"])
        writer.writerow([
            results_dict["timestamp"],
            results_dict["output_filename"],
            results_dict["player"],
            results_dict["stroke_cycle_time"],
            results_dict["pelvis_angle"],
            results_dict["knee_angle"],
            results_dict["ankle_angle"]
        ])

def find_record_by_filename(filename, results_csv):
    if not os.path.exists(results_csv):
        return None
    with open(results_csv, 'r', newline='') as f:
        reader = csv.reader(f)
        header = next(reader, None)
        if header is None:
            return None
        for row in reader:
            if row[1] == filename:
                return row
    return None
