from flask import Flask, request, jsonify
from flask_cors import CORS
import cv2
import numpy as np
import math
import mediapipe as mp
from datetime import datetime
import json
import os

app = Flask(__name__)
CORS(app)

class poseDetector():
    def __init__(self, mode=False, upBody=False, smooth=True,
                 detectionCon=0.5, trackCon=0.5):
        self.mode = mode
        self.upBody = upBody
        self.smooth = smooth
        self.detectionCon = detectionCon
        self.trackCon = trackCon
        self.mpDraw = mp.solutions.drawing_utils
        self.mpPose = mp.solutions.pose
        self.pose = self.mpPose.Pose(
            static_image_mode=self.mode,
            model_complexity=1,
            smooth_landmarks=self.smooth,
            min_detection_confidence=self.detectionCon,
            min_tracking_confidence=self.trackCon
        )

    def findPose(self, img, draw=True):
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.pose.process(imgRGB)
        if self.results.pose_landmarks:
            if draw:
                self.mpDraw.draw_landmarks(img, self.results.pose_landmarks,
                                           self.mpPose.POSE_CONNECTIONS)
        return img

    def findPosition(self, img, draw=True):
        self.lmList = []
        if self.results.pose_landmarks:
            for id, lm in enumerate(self.results.pose_landmarks.landmark):
                h, w, c = img.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                self.lmList.append([id, cx, cy])
                if draw:
                    cv2.circle(img, (cx, cy), 5, (255, 0, 0), cv2.FILLED)
        return self.lmList

    def findAngle(self, img, p1, p2, p3, draw=True):
        x1, y1 = self.lmList[p1][1:]
        x2, y2 = self.lmList[p2][1:]
        x3, y3 = self.lmList[p3][1:]
        
        angle = math.degrees(math.atan2(y3 - y2, x3 - x2) -
                             math.atan2(y1 - y2, x1 - x2))
        if angle < 0:
            angle += 360
        
        if draw:
            cv2.line(img, (x1, y1), (x2, y2), (255, 255, 255), 3)
            cv2.line(img, (x3, y3), (x2, y2), (255, 255, 255), 3)
            cv2.circle(img, (x1, y1), 10, (0, 0, 255), cv2.FILLED)
            cv2.circle(img, (x1, y1), 15, (0, 0, 255), 2)
            cv2.circle(img, (x2, y2), 10, (0, 0, 255), cv2.FILLED)
            cv2.circle(img, (x2, y2), 15, (0, 0, 255), 2)
            cv2.circle(img, (x3, y3), 10, (0, 0, 255), cv2.FILLED)
            cv2.circle(img, (x3, y3), 15, (0, 0, 255), 2)
            cv2.putText(img, str(int(angle)), (x2 - 50, y2 + 50),
                        cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 255), 2)
        return angle

# 포즈 감지기 초기화
detector = poseDetector()

# 전역 변수 설정
count_squat = 0
count_pushup = 0
count_pullup = 0
dir_squat = 0
dir_pushup = 0
dir_pullup = 0
exercise_type = ""
target_reps = 0
target_sets = 0
current_set = 1
per_squat = 0
per_pushup = 0
per_pullup = 0

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
    
    if exercise_type == "스쿼트":
        exercise_data.update({"squat_reps": int(count_squat)})
    elif exercise_type == "푸시업":
        exercise_data.update({"pushup_reps": int(count_pushup)})
    elif exercise_type == "풀업":
        exercise_data.update({"pullup_reps": int(count_pullup)})
    
    exercise_history[date].append(exercise_data)
    
    with open(HISTORY_FILE_PATH, 'w', encoding='utf-8') as f:
        json.dump(exercise_history, f, ensure_ascii=False, indent=4)
    
    print(f"Exercise history saved to {HISTORY_FILE_PATH}")

@app.route('/process_frame', methods=['POST'])
def process_frame():
    global count_squat, count_pushup, count_pullup
    global dir_squat, dir_pushup, dir_pullup
    global per_squat, per_pushup, per_pullup

    frame_data = request.json['frame']
    nparr = np.frombuffer(frame_data.encode('latin-1'), np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    img = detector.findPose(img, False)
    lmList = detector.findPosition(img, False)

    feedback = []
    if len(lmList) != 0:
        if exercise_type == "스쿼트":
            # 스쿼트 분석
            hip_knee_ankle_angle = detector.findAngle(img, 24, 26, 28)
            spine_hip_angle = detector.findAngle(img, 11, 23, 25)
            knee_x = lmList[26][1]
            ankle_x = lmList[28][1]

            per_squat = np.interp(hip_knee_ankle_angle, (90, 170), (100, 0))
            
            if hip_knee_ankle_angle > 100:
                feedback.append("무릎을 더 굽히세요.")
            if spine_hip_angle < 140 or spine_hip_angle > 190:
                feedback.append("허리를 곧게 펴세요.")
            if knee_x > ankle_x + 0.1 * img.shape[1]:
                feedback.append("무릎이 발끝을 넘어가지 않도록 주의하세요.")

            if per_squat == 100:
                if dir_squat == 0:
                    count_squat += 0.5
                    dir_squat = 1
            if per_squat == 0:
                if dir_squat == 1:
                    count_squat += 0.5
                    dir_squat = 0

        elif exercise_type == "푸시업":
            # 푸시업 분석
            elbow_angle = detector.findAngle(img, 11, 13, 15)
            body_alignment = detector.findAngle(img, 11, 23, 27)
            neck_alignment = detector.findAngle(img, 0, 11, 23)

            per_pushup = np.interp(elbow_angle, (90, 160), (100, 0))
            
            if elbow_angle < 45 or elbow_angle > 110:
                feedback.append("팔꿈치 각도를 90도에 가깝게 유지하세요.")
            if abs(body_alignment - 180) > 15:
                feedback.append("몸을 일직선으로 유지하세요.")
            if neck_alignment < 150 or neck_alignment > 190:
                feedback.append("목을 중립 위치로 유지하세요.")

            if per_pushup == 100:
                if dir_pushup == 0:
                    count_pushup += 0.5
                    dir_pushup = 1
            if per_pushup == 0:
                if dir_pushup == 1:
                    count_pushup += 0.5
                    dir_pushup = 0

        elif exercise_type == "풀업":
            # 풀업 분석
            arm_angle = detector.findAngle(img, 13, 11, 23)
            body_alignment = detector.findAngle(img, 11, 23, 25)
            chin_y = lmList[0][2]
            wrist_y = min(lmList[15][2], lmList[16][2])

            per_pullup = np.interp(arm_angle, (45, 120), (100, 0))
            
            if arm_angle < 45 or arm_angle > 110:
                feedback.append("팔꿈치를 적절히 구부리세요.")
            if abs(body_alignment - 180) > 15:
                feedback.append("몸을 일직선으로 유지하세요.")
            if chin_y > wrist_y:
                feedback.append("턱을 손목 위로 올리세요.")

            if per_pullup == 100:
                if dir_pullup == 0:
                    count_pullup += 0.5
                    dir_pullup = 1
            if per_pullup == 0:
                if dir_pullup == 1:
                    count_pullup += 0.5
                    dir_pullup = 0

    result = {
        'count_squat': int(count_squat),
        'count_pushup': int(count_pushup),
        'count_pullup': int(count_pullup),
        'current_set': current_set,
        'per_squat': int(per_squat),
        'per_pushup': int(per_pushup),
        'per_pullup': int(per_pullup),
        'feedback': feedback
    }

    return jsonify(result)

@app.route('/start_exercise', methods=['POST'])
def start_exercise():
    global exercise_type, target_reps, target_sets, current_set
    global count_squat, count_pushup, count_pullup
    data = request.json
    exercise_type = data['exercise_type']
    target_reps = data['target_reps']
    target_sets = data['target_sets']
    current_set = 1
    count_squat = 0
    count_pushup = 0
    count_pullup = 0
    return jsonify({'status': 'success'})

@app.route('/end_exercise', methods=['POST'])
def end_exercise():
    save_exercise_history()
    return jsonify({'status': 'success', 'message': 'Exercise history saved'})

if __name__ == '__main__':
    load_exercise_history()
    app.run(debug=True)