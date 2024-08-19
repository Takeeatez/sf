from flask import Flask, request, jsonify
from flask_cors import CORS
import cv2
import numpy as np
import PoseModule as pm
from datetime import datetime
import json
import os

app = Flask(__name__)
CORS(app)

# 포즈 감지기 초기화
detector = pm.poseDetector()

# 전역 변수 설정
count_right_arm = 0
count_left_arm = 0
count_squat = 0
dir_right_arm = 0
dir_left_arm = 0
dir_squat = 0
exercise_type = ""
target_reps = 0
target_sets = 0
current_set = 1
per_right_arm = 0
per_left_arm = 0
per_squat = 0

# 운동 기록 저장을 위한 딕셔너리
exercise_history = {}

# JSON 파일 저장 경로 설정
HISTORY_FILE_PATH = os.path.join(os.path.dirname(__file__), 'exercise_history.json')

def load_exercise_history():
    global exercise_history
    if os.path.exists(HISTORY_FILE_PATH):
        with open(HISTORY_FILE_PATH, 'r', encoding='utf-8') as f:
            exercise_history = json.load(f)
    else:
        exercise_history = {}

def save_exercise_history():
    global exercise_history
    date = datetime.now().strftime("%Y-%m-%d")
    time_now = datetime.now().strftime("%H:%M:%S")
    
    if date not in exercise_history:
        exercise_history[date] = []
    
    exercise_data = {
        "time": time_now,
        "exercise_type": exercise_type,
        "sets": current_set - 1,
        "target_sets": target_sets,
        "target_reps": target_reps
    }
    
    if exercise_type == "아령 들기":
        exercise_data.update({
            "right_arm_reps": int(count_right_arm),
            "left_arm_reps": int(count_left_arm)
        })
    else:
        exercise_data.update({
            "squat_reps": int(count_squat)
        })
    
    exercise_history[date].append(exercise_data)
    
    with open(HISTORY_FILE_PATH, 'w', encoding='utf-8') as f:
        json.dump(exercise_history, f, ensure_ascii=False, indent=4)
    
    print(f"Exercise history saved to {HISTORY_FILE_PATH}")

@app.route('/process_frame', methods=['POST'])
def process_frame():
    global count_right_arm, count_left_arm, count_squat
    global dir_right_arm, dir_left_arm, dir_squat
    global per_right_arm, per_left_arm, per_squat

    # 프레임 데이터를 받아 처리
    frame_data = request.json['frame']
    nparr = np.frombuffer(frame_data.encode('latin-1'), np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    img = detector.findPose(img, False)
    lmList = detector.findPosition(img, False)

    if len(lmList) != 0:
        if exercise_type == "아령 들기":
            # 오른팔
            angle_right_arm = detector.findAngle(img, 12, 14, 16)
            per_right_arm = np.interp(angle_right_arm, (210, 310), (0, 100))
            
            # 왼팔
            angle_left_arm = detector.findAngle(img, 11, 13, 15)
            per_left_arm = np.interp(angle_left_arm, (210, 310), (0, 100))

            # 카운트 로직
            if per_right_arm == 100:
                if dir_right_arm == 0:
                    count_right_arm += 0.5
                    dir_right_arm = 1
            if per_right_arm == 0:
                if dir_right_arm == 1:
                    count_right_arm += 0.5
                    dir_right_arm = 0

            if per_left_arm == 100:
                if dir_left_arm == 0:
                    count_left_arm += 0.5
                    dir_left_arm = 1
            if per_left_arm == 0:
                if dir_left_arm == 1:
                    count_left_arm += 0.5
                    dir_left_arm = 0

        elif exercise_type == "스쿼트":
            # 스쿼트 로직
            angle_squat = detector.findAngle(img, 24, 26, 28)
            per_squat = np.interp(angle_squat, (210, 310), (100, 0))

            if per_squat == 100:
                if dir_squat == 0:
                    count_squat += 0.5
                    dir_squat = 1
            if per_squat == 0:
                if dir_squat == 1:
                    count_squat += 0.5
                    dir_squat = 0

    result = {
        'count_right_arm': int(count_right_arm),
        'count_left_arm': int(count_left_arm),
        'count_squat': int(count_squat),
        'current_set': current_set,
        'per_right_arm': int(per_right_arm),
        'per_left_arm': int(per_left_arm),
        'per_squat': int(per_squat)
    }

    return jsonify(result)

@app.route('/start_exercise', methods=['POST'])
def start_exercise():
    global exercise_type, target_reps, target_sets, current_set
    global count_right_arm, count_left_arm, count_squat
    data = request.json
    exercise_type = data['exercise_type']
    target_reps = data['target_reps']
    target_sets = data['target_sets']
    current_set = 1
    count_right_arm = 0
    count_left_arm = 0
    count_squat = 0
    return jsonify({'status': 'success'})

@app.route('/end_exercise', methods=['POST'])
def end_exercise():
    save_exercise_history()
    return jsonify({'status': 'success', 'message': 'Exercise history saved'})

if __name__ == '__main__':
    load_exercise_history()
    app.run(debug=True)