import cv2
import numpy as np
import mediapipe as mp
import math
from utils import poseDetector, put_korean_text

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
    
    progress = np.interp(elbow_angle, (160, 70), (0, 100))
    return elbow_angle, progress, feedback

def process_pullup(frame, detector):
    img = detector.findPose(frame)
    lmList = detector.findPosition(img, draw=False)
    
    if len(lmList) != 0:
        angle, progress, feedback = analyze_pullup(detector, img)
        
        color = (0, 255, 0) if not feedback else (0, 0, 255)
        img = put_korean_text(img, f'풀업', (10, 30), 30, color)
        img = put_korean_text(img, f'진행도: {int(progress)}%', (10, 70), 30, color)
        
        for i, fb in enumerate(feedback):
            img = put_korean_text(img, fb, (10, 110 + i*40), 30, (0, 0, 255))

    return img, progress, feedback