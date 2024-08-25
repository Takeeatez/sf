import cv2
import numpy as np
import mediapipe as mp
import math

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

def analyze_squat(detector, lmList):
    # 기존의 analyze_squat 함수 코드를 그대로 유지
    right_shoulder = lmList[12]
    right_hip = lmList[24]
    right_knee = lmList[26]
    right_ankle = lmList[28]

    hip_knee_ankle_angle = detector.findAngle(None, 24, 26, 28)
    
    feedback = []
    
    if hip_knee_ankle_angle < 160:
        if hip_knee_ankle_angle > 90:
            feedback.append("무릎을 더 굽히세요. 허벅지가 바닥과 평행이 되도록 하세요.")
        elif hip_knee_ankle_angle < 70:
            feedback.append("너무 깊게 앉지 마세요. 무릎에 무리가 갈 수 있습니다.")

        shoulder_hip_x_diff = right_shoulder[1] - right_hip[1]
        tolerance = 30

        if abs(shoulder_hip_x_diff) > tolerance:
            if shoulder_hip_x_diff < 0:
                feedback.append("상체가 앞으로 기울어집니다. 어깨를 뒤로 젖혀 수직을 유지하세요.")
            else:
                feedback.append("상체가 뒤로 기울어집니다. 어깨를 앞으로 당겨 수직을 유지하세요.")

        knee_ankle_x_diff = right_knee[1] - right_ankle[1]
        if knee_ankle_x_diff > 30:
            feedback.append("무릎이 발끝을 넘어갑니다. 무릎을 발과 일직선상에 유지하세요.")
        
        if right_ankle[2] < right_ankle[1] - 10:
            feedback.append("발뒤꿈치가 들리지 않도록 주의하세요. 무게 중심을 뒤쪽으로 유지하세요.")

    return hip_knee_ankle_angle, feedback

def analyze_pushup(detector, lmList):
    # 기존의 analyze_pushup 함수 코드를 그대로 유지
    elbow_angle = detector.findAngle(None, 12, 14, 16)
    
    shoulder_y = lmList[12][2]
    hip_y = lmList[24][2]
    ankle_y = lmList[28][2]
    
    body_angle = detector.findAngle(None, 12, 24, 28, draw=False)
    
    neck_angle = detector.findAngle(None, 8, 12, 24, draw=False)
    
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

def analyze_pullup(detector, lmList):
    # 기존의 analyze_pullup 함수 코드를 그대로 유지
    shoulder = lmList[12]
    hip = lmList[24]
    ankle = lmList[28]
    
    body_angle = detector.findAngle(None, 12, 24, 28, draw=False)
    
    chin_y = lmList[7][2]
    hand_y = lmList[16][2]
    
    elbow_angle = detector.findAngle(None, 12, 14, 16)
    
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

