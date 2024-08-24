'''0. 코 (Nose)
1. 왼쪽 눈 안쪽 (Left eye inner)
2. 왼쪽 눈 (Left eye)
3. 왼쪽 눈 바깥쪽 (Left eye outer)
4. 오른쪽 눈 안쪽 (Right eye inner)
5. 오른쪽 눈 (Right eye)
6. 오른쪽 눈 바깥쪽 (Right eye outer)
7. 왼쪽 귀 (Left ear)
8. 오른쪽 귀 (Right ear)
9. 입 왼쪽 (Mouth left)
10. 입 오른쪽 (Mouth right)
11. 왼쪽 어깨 (Left shoulder)
12. 오른쪽 어깨 (Right shoulder)
13. 왼쪽 팔꿈치 (Left elbow)
14. 오른쪽 팔꿈치 (Right elbow)
15. 왼쪽 손목 (Left wrist)
16. 오른쪽 손목 (Right wrist)
17. 왼쪽 새끼손가락 (Left pinky)
18. 오른쪽 새끼손가락 (Right pinky)
19. 왼쪽 검지 (Left index)
20. 오른쪽 검지 (Right index)
21. 왼쪽 엄지 (Left thumb)
22. 오른쪽 엄지 (Right thumb)
23. 왼쪽 엉덩이 (Left hip)
24. 오른쪽 엉덩이 (Right hip)
25. 왼쪽 무릎 (Left knee)
26. 오른쪽 무릎 (Right knee)
27. 왼쪽 발목 (Left ankle)
28. 오른쪽 발목 (Right ankle)
29. 왼쪽 발뒤꿈치 (Left heel)
30. 오른쪽 발뒤꿈치 (Right heel)
31. 왼쪽 발가락 (Left foot index)
32. 오른쪽 발가락 (Right foot index)
'''

import cv2
import numpy as np
import mediapipe as mp
import math
import json
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont

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
    # 관절 좌표 추출
    right_shoulder = detector.lmList[12]
    right_hip = detector.lmList[24]
    right_knee = detector.lmList[26]
    right_ankle = detector.lmList[28]

    # 엉덩이-무릎-발목 각도 계산
    hip_knee_ankle_angle = detector.findAngle(img, 24, 26, 28)
    
    # 어깨와 엉덩이의 x, y 좌표
    shoulder_x, shoulder_y = right_shoulder[1:]
    hip_x, hip_y = right_hip[1:]
    knee_x = right_knee[1]
    ankle_x = right_ankle[1]

    feedback = []
    
    # 초기 자세 (서 있는 상태)가 아닐 때만 분석
    if hip_knee_ankle_angle < 160:
        # 1. 엉덩이-무릎-발목 각도 분석
        if hip_knee_ankle_angle > 90:  # 90도에서 여유를 둠
            feedback.append("무릎을 더 굽히세요. 허벅지가 바닥과 평행이 되도록 하세요.")
        elif hip_knee_ankle_angle < 70:  # 너무 깊게 앉는 것을 방지
            feedback.append("너무 깊게 앉지 마세요. 무릎에 무리가 갈 수 있습니다.")

        # 2. 어깨의 수직 이동 확인
        shoulder_hip_x_diff = shoulder_x - hip_x
        tolerance = 30  # 허용 오차 (픽셀 단위)

        if abs(shoulder_hip_x_diff) > tolerance:
            if shoulder_hip_x_diff < 0:
                feedback.append("상체가 앞으로 기울어집니다. 어깨를 뒤로 젖혀 수직을 유지하세요.")
            else:
                feedback.append("상체가 뒤로 기울어집니다. 어깨를 앞으로 당겨 수직을 유지하세요.")

        # 3. 무릎-발목 정렬 분석
        knee_ankle_x_diff = knee_x - ankle_x
        if knee_ankle_x_diff > 30:  # 30은 픽셀 단위의 허용 오차
            feedback.append("무릎이 발끝을 넘어갑니다. 무릎을 발과 일직선상에 유지하세요.")
        
        # 4. 무게 중심 확인 (발뒤꿈치 들림 방지)
        heel = detector.lmList[30]  # 오른쪽 발뒤꿈치
        if heel[2] < ankle_x - 10:  # y좌표가 더 작으면 (화면상 더 위에 있으면) 발뒤꿈치가 들린 것
            feedback.append("발뒤꿈치가 들리지 않도록 주의하세요. 무게 중심을 뒤쪽으로 유지하세요.")


    return hip_knee_ankle_angle, feedback

def analyze_pushup(detector, img):
    # 오른쪽 팔꿈치 각도
    elbow_angle = detector.findAngle(img, 12, 14, 16)
    
    # 오른쪽 어깨, 엉덩이, 발목의 y 좌표
    shoulder_y = detector.lmList[12][2]
    hip_y = detector.lmList[24][2]
    ankle_y = detector.lmList[28][2]
    
    # 등의 수평 상태 확인 (어깨-엉덩이-발목 선)
    body_angle = detector.findAngle(img, 12, 24, 28, draw=False)
    
    # 목 위치 확인 (귀-어깨-엉덩이 선)
    neck_angle = detector.findAngle(img, 8, 12, 24, draw=False)
    
    feedback = []
    
    if elbow_angle < 160:  # 팔이 완전히 펴진 상태가 아닐 때
        # 팔꿈치 각도 확인
        if elbow_angle > 110:
            feedback.append("팔을 더 굽히세요.")
        elif elbow_angle < 70:
            feedback.append("팔을 너무 많이 굽히지 마세요.")
        
        # 등의 수평 상태 확인
        if abs(180 - body_angle) > 15:
            if hip_y < min(shoulder_y, ankle_y):
                feedback.append("엉덩이를 낮추세요. 등을 수평으로 유지하세요.")
            elif hip_y > max(shoulder_y, ankle_y):
                feedback.append("엉덩이를 올리세요. 등을 수평으로 유지하세요.")
            else:
                feedback.append("등을 수평으로 유지하세요.")
        
        # 목 위치 확인
        if abs(neck_angle - body_angle) > 15:
            if neck_angle > body_angle:
                feedback.append("고개를 너무 들지 마세요. 목을 척추와 일직선으로 유지하세요.")
            else:
                feedback.append("고개를 너무 숙이지 마세요. 목을 척추와 일직선으로 유지하세요.")
    
    return elbow_angle, feedback

def analyze_pullup(detector, img):
    # 오른쪽 어깨-엉덩이-발목 직선 확인
    shoulder = detector.lmList[12]
    hip = detector.lmList[24]
    ankle = detector.lmList[28]
    
    # 오른쪽 어깨-엉덩이-발목 각도 계산
    body_angle = detector.findAngle(img, 12, 24, 28, draw=False)
    
    # 턱과 오른쪽 손의 y 좌표
    chin_y = detector.lmList[7][2]
    hand_y = detector.lmList[16][2]
    
    # 오른쪽 팔꿈치 각도 (운동 진행 상태 확인용)
    elbow_angle = detector.findAngle(img, 12, 14, 16)
    
    feedback = []
    
    # 초기 자세 (팔이 완전히 펴진 상태)가 아닐 때만 분석
    if elbow_angle < 160:
        # 어깨-엉덩이-발목 직선 확인
        if abs(180 - body_angle) > 15:
            feedback.append("몸을 일직선으로 유지하세요. 엉덩이가 뒤로 빠지지 않도록 주의하세요.")
        
        # 턱-손 위치 확인
        if chin_y > hand_y:
            feedback.append("더 높이 당기세요. 턱이 손 높이까지 올라가야 합니다.")
        
        # 상체 흔들림 확인 (이전 프레임과의 x 좌표 차이로 판단)
        if hasattr(detector, 'prev_shoulder_x'):
            shoulder_movement = abs(shoulder[1] - detector.prev_shoulder_x)
            if shoulder_movement > 20:
                feedback.append("상체를 안정적으로 유지하세요. 과도한 흔들림에 주의하세요.")
        
        # 현재 어깨 x 좌표 저장
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

def main():
    exercise_options = {"1": "스쿼트", "2": "푸시업", "3": "풀업"}
    print("운동을 선택하세요:")
    for key, value in exercise_options.items():
        print(f"{key}. {value}")
    choice = input("선택 (1/2/3): ")
    exercise_type = exercise_options[choice]

    target_sets = int(input("목표 세트 수를 입력하세요: "))
    target_reps = int(input("세트당 반복 횟수를 입력하세요: "))

    cap = cv2.VideoCapture(0)
    detector = poseDetector()
    
    count = 0
    dir = 0
    current_set = 1
    total_accuracy = 0
    total_count = 0
    start_time = datetime.now()

    while current_set <= target_sets:
        success, img = cap.read()
        img = cv2.flip(img, 1)  # 좌우 반전
        img = detector.findPose(img)
        lmList = detector.findPosition(img, draw=False)
        
        if len(lmList) != 0:
            if exercise_type == "스쿼트":
                angle, feedback = analyze_squat(detector, img)
                per = np.interp(angle, (90, 160), (100, 0))
            elif exercise_type == "푸시업":
                angle, feedback = analyze_pushup(detector, img)
                per = np.interp(angle, (70, 160), (100, 0))
            elif exercise_type == "풀업":
                angle, feedback = analyze_pullup(detector, img)
                per = np.interp(angle, (160, 70), (0, 100))

            if per == 100:
                if dir == 0:
                    count += 0.5
                    dir = 1
            if per == 0:
                if dir == 1:
                    count += 0.5
                    dir = 0
            
            total_accuracy += per
            total_count += 1

            color = (0, 255, 0) if not feedback else (0, 0, 255)
            img = put_korean_text(img, f'운동: {exercise_type}', (10, 30), 30, color)
            img = put_korean_text(img, f'세트: {current_set}/{target_sets}', (10, 70), 30, color)
            img = put_korean_text(img, f'횟수: {int(count)}/{target_reps}', (10, 110), 30, color)
            
            for i, fb in enumerate(feedback):
                img = put_korean_text(img, fb, (10, 150 + i*40), 30, (0, 0, 255))

            if int(count) == target_reps:
                current_set += 1
                count = 0

        cv2.imshow("Exercise Progress", img)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    avg_accuracy = (total_accuracy / total_count) if total_count > 0 else 0
    save_exercise_data(exercise_type, target_sets, target_reps, avg_accuracy, duration)

if __name__ == "__main__":
    main()