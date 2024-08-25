import cv2
import numpy as np
import mediapipe as mp
import math
from utils import poseDetector, put_korean_text

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

    progress = np.interp(hip_knee_ankle_angle, (70, 160), (100, 0))
    return hip_knee_ankle_angle, progress, feedback

def process_squat(frame, detector):
    img = detector.findPose(frame)
    lmList = detector.findPosition(img, draw=False)
    
    if len(lmList) != 0:
        angle, progress, feedback = analyze_squat(detector, img)
        
        color = (0, 255, 0) if not feedback else (0, 0, 255)
        img = put_korean_text(img, f'스쿼트', (10, 30), 30, color)
        img = put_korean_text(img, f'진행도: {int(progress)}%', (10, 70), 30, color)
        
        for i, fb in enumerate(feedback):
            img = put_korean_text(img, fb, (10, 110 + i*40), 30, (0, 0, 255))

    return img, progress, feedback