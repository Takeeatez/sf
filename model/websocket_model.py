import asyncio
import websockets
import cv2
import numpy as np
import mediapipe as mp
import math
import json
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import base64
import io

class poseDetector():
    def __init__(self, mode=False, upBody=False, smooth=True, detectionCon=0.5, trackCon=0.5):
        self.mode = mode
        self.upBody = upBody
        self.smooth = smooth
        self.detectionCon = detectionCon
        self.trackCon = trackCon
        self.mpDraw = mp.solutions.drawing_utils
        self.mpPose = mp.solutions.pose
        self.pose = self.mpPose.Pose(static_image_mode=self.mode, model_complexity=1,
                                     smooth_landmarks=self.smooth,
                                     min_detection_confidence=self.detectionCon,
                                     min_tracking_confidence=self.trackCon)

    def findPose(self, img, draw=True):
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.pose.process(imgRGB)
        if self.results.pose_landmarks:
            if draw:
                self.mpDraw.draw_landmarks(img, self.results.pose_landmarks, self.mpPose.POSE_CONNECTIONS,
                                           self.mpDraw.DrawingSpec(color=(255,0,0), thickness=2, circle_radius=2),
                                           self.mpDraw.DrawingSpec(color=(255,0,0), thickness=2, circle_radius=2))
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

        angle = math.degrees(math.atan2(y3-y2, x3-x2) - math.atan2(y1-y2, x1-x2))
        if angle < 0:
            angle += 360

        if draw:
            cv2.line(img, (x1, y1), (x2, y2), (255, 255, 255), 3)
            cv2.line(img, (x3, y3), (x2, y2), (255, 255, 255), 3)
            cv2.circle(img, (x1, y1), 10, (0, 0, 255), cv2.FILLED)
            cv2.circle(img, (x2, y2), 10, (0, 0, 255), cv2.FILLED)
            cv2.circle(img, (x3, y3), 10, (0, 0, 255), cv2.FILLED)
            cv2.putText(img, str(int(angle)), (x2 - 50, y2 + 50), 
                        cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 255), 2)
        return angle

def analyze_squat(detector, img):
    right_shoulder = detector.lmList[12]
    right_hip = detector.lmList[24]
    right_knee = detector.lmList[26]
    right_ankle = detector.lmList[28]

    hip_knee_ankle_angle = detector.findAngle(img, 24, 26, 28)

    shoulder_x, shoulder_y = right_shoulder[1:]
    hip_x, hip_y = right_hip[1:]
    knee_x = right_knee[1]
    ankle_x = right_ankle[1]

    feedback = []

    if hip_knee_ankle_angle < 160:
        if hip_knee_ankle_angle > 90:
            feedback.append("무릎을 더 굽히세요. 허벅지가 바닥과 평행이 되도록 하세요.")
        elif hip_knee_ankle_angle < 70:
            feedback.append("너무 깊게 앉지 마세요. 무릎에 무리가 갈 수 있습니다.")

        shoulder_hip_x_diff = shoulder_x - hip_x
        tolerance = 30

        if abs(shoulder_hip_x_diff) > tolerance:
            if shoulder_hip_x_diff < 0:
                feedback.append("상체가 앞으로 기울어집니다. 어깨를 뒤로 젖혀 수직을 유지하세요.")
            else:
                feedback.append("상체가 뒤로 기울어집니다. 어깨를 앞으로 당겨 수직을 유지하세요.")

        knee_ankle_x_diff = knee_x - ankle_x
        if knee_ankle_x_diff > 30:
            feedback.append("무릎이 발끝을 넘어갑니다. 무릎을 발과 일직선상에 유지하세요.")

        heel = detector.lmList[30]
        if heel[2] < ankle_x - 10:
            feedback.append("발뒤꿈치가 들리지 않도록 주의하세요. 무게 중심을 뒤쪽으로 유지하세요.")

    return hip_knee_ankle_angle, feedback

def analyze_pushup(detector, img):
    elbow_angle = detector.findAngle(img, 12, 14, 16)

    shoulder_y = detector.lmList[12][2]
    hip_y = detector.lmList[24][2]
    ankle_y = detector.lmList[28][2]

    body_angle = detector.findAngle(img, 12, 24, 28, draw=False)
    neck_angle = detector.findAngle(img, 8, 12, 24, draw=False)

    feedback = []

    if elbow_angle < 160:
        if elbow_angle > 110:
            feedback.append("팔을 더 굽히세요.")
        elif elbow_angle < 70:
            feedback.append("팔을 너무 많이 굽히지 마세요.")

        if abs(180 - body_angle) > 15:
            if hip_y < min(shoulder_y, ankle_y):
                feedback.append("엉덩이를 낮추세요. 등을 수평으로 유지하세요.")
            elif hip_y > max(shoulder_y, ankle_y):
                feedback.append("엉덩이를 올리세요. 등을 수평으로 유지하세요.")
            else:
                feedback.append("등을 수평으로 유지하세요.")

        if abs(neck_angle - body_angle) > 15:
            if neck_angle > body_angle:
                feedback.append("고개를 너무 들지 마세요. 목을 척추와 일직선으로 유지하세요.")
            else:
                feedback.append("고개를 너무 숙이지 마세요. 목을 척추와 일직선으로 유지하세요.")

    return elbow_angle, feedback

def analyze_pullup(detector, img):
    shoulder = detector.lmList[12]
    hip = detector.lmList[24]
    ankle = detector.lmList[28]

    body_angle = detector.findAngle(img, 12, 24, 28, draw=False)

    chin_y = detector.lmList[7][2]
    hand_y = detector.lmList[16][2]

    elbow_angle = detector.findAngle(img, 12, 14, 16)

    feedback = []

    if elbow_angle < 160:
        if abs(180 - body_angle) > 15:
            feedback.append("몸을 일직선으로 유지하세요. 엉덩이가 뒤로 빠지지 않도록 주의하세요.")

        if chin_y > hand_y:
            feedback.append("더 높이 당기세요. 턱이 손 높이까지 올라가야 합니다.")

        if hasattr(detector, 'prev_shoulder_x'):
            shoulder_movement = abs(shoulder[1] - detector.prev_shoulder_x)
            if shoulder_movement > 20:
                feedback.append("상체를 안정적으로 유지하세요. 과도한 흔들림에 주의하세요.")

        detector.prev_shoulder_x = shoulder[1]

    return elbow_angle, feedback

def put_korean_text(img, text, position, font_size, color):
    img_pil = Image.fromarray(img)
    draw = ImageDraw.Draw(img_pil)
    font = ImageFont.truetype("/System/Library/Fonts/AppleSDGothicNeo.ttc", font_size)
    draw.text(position, text, font=font, fill=color)
    return np.array(img_pil)

def save_exercise_data(exercise_type, sets, reps, accuracy, duration):
    date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    data = {
        "date": date,
        "exercise_type": exercise_type,
        "sets": sets,
        "reps": reps,
        "accuracy": accuracy,
        "duration": duration
    }
    filename = f"exercise_history_{date.replace(':', '-')}.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print(f"운동 기록이 {filename}에 저장되었습니다.")

class ExerciseAnalyzer:
    def __init__(self):
        self.detector = poseDetector()
        self.exercise_type = None
        self.target_sets = 0
        self.target_reps = 0
        self.count = 0
        self.dir = 0
        self.current_set = 1
        self.total_accuracy = 0
        self.total_count = 0
        self.start_time = None

    async def analyze_frame(self, frame_data):
        img = cv2.imdecode(np.frombuffer(base64.b64decode(frame_data), np.uint8), cv2.IMREAD_COLOR)
        img = cv2.flip(img, 1)  # 좌우 반전
        img = self.detector.findPose(img)
        lmList = self.detector.findPosition(img, draw=False)

        if len(lmList) != 0:
            if self.exercise_type == "스쿼트":
                angle, feedback = analyze_squat(self.detector, img)
                per = np.interp(angle, (90, 160), (100, 0))
            elif self.exercise_type == "푸시업":
                angle, feedback = analyze_pushup(self.detector, img)
                per = np.interp(angle, (70, 160), (100, 0))
            elif self.exercise_type == "풀업":
                angle, feedback = analyze_pullup(self.detector, img)
                per = np.interp(angle, (160, 70), (0, 100))

            if per == 100:
                if self.dir == 0:
                    self.count += 0.5
                    self.dir = 1
            if per == 0:
                if self.dir == 1:
                    self.count += 0.5
                    self.dir = 0

            self.total_accuracy += per
            self.total_count += 1

            color = (0, 255, 0) if not feedback else (0, 0, 255)
            img = put_korean_text(img, f'운동: {self.exercise_type}', (10, 30), 30, color)
            img = put_korean_text(img, f'세트: {self.current_set}/{self.target_sets}', (10, 70), 30, color)
            img = put_korean_text(img, f'횟수: {int(self.count)}/{self.target_reps}', (10, 110), 30, color)

            for i, fb in enumerate(feedback):
                img = put_korean_text(img, fb, (10, 150 + i*40), 30, (0, 0, 255))

            if int(self.count) == self.target_reps:
                self.current_set += 1
                self.count = 0

            _, buffer = cv2.imencode('.jpg', img)
            img_base64 = base64.b64encode(buffer).decode('utf-8')

            return {
                "image": img_base64,
                "feedback": feedback,
                "count": int(self.count),
                "set": self.current_set,
                "exercise_complete": self.current_set > self.target_sets
            }

    def start_exercise(self, exercise_type, target_sets, target_reps):
        self.exercise_type = exercise_type
        self.target_sets = target_sets
        self.target_reps = target_reps
        self.count = 0
        self.dir = 0
        self.current_set = 1
        self.total_accuracy = 0
        self.total_count = 0
        self.start_time = datetime.now()

    def end_exercise(self):
        end_time = datetime.now()
        duration = (end_time - self.start_time).total_seconds()
        avg_accuracy = (self.total_accuracy / self.total_count) if self.total_count > 0 else 0
        save_exercise_data(self.exercise_type, self.target_sets, self.target_reps, avg_accuracy, duration)

async def handle_websocket(websocket, path):
    analyzer = ExerciseAnalyzer()
    try:
        async for message in websocket:
            data = json.loads(message)
            if data['type'] == 'start_exercise':
                analyzer.start_exercise(data['exercise_type'], data['target_sets'], data['target_reps'])
                await websocket.send(json.dumps({"type": "exercise_started"}))
            elif data['type'] == 'analyze_frame':
                result = await analyzer.analyze_frame(data['frame'])
                if result['exercise_complete']:
                    analyzer.end_exercise()
                    result['type'] = 'exercise_complete'
                else:
                    result['type'] = 'frame_analysis'
                await websocket.send(json.dumps(result))
            elif data['type'] == 'end_exercise':
                analyzer.end_exercise()
                await websocket.send(json.dumps({"type": "exercise_ended"}))
    except websockets.exceptions.ConnectionClosed:
        print("Client disconnected")

async def main():
    server = await websockets.serve(handle_websocket, "localhost", 8765)
    print("WebSocket server started on ws://localhost:8765")
    await server.wait_closed()

if __name__ == "__main__":
    asyncio.run(main())