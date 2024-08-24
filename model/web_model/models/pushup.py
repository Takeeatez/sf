import cv2
import numpy as np
import mediapipe as mp
import math
from utils import poseDetector, put_korean_text

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
    
    progress = np.interp(elbow_angle, (70, 160), (100, 0))
    return elbow_angle, progress, feedback

def process_pushup(frame, detector):
    img = detector.findPose(frame)
    lmList = detector.findPosition(img, draw=False)
    
    if len(lmList) != 0:
        angle, progress, feedback = analyze_pushup(detector, img)
        
        color = (0, 255, 0) if not feedback else (0, 0, 255)
        img = put_korean_text(img, f'푸시업', (10, 30), 30, color)
        img = put_korean_text(img, f'진행도: {int(progress)}%', (10, 70), 30, color)
        
        for i, fb in enumerate(feedback):
            img = put_korean_text(img, fb, (10, 110 + i*40), 30, (0, 0, 255))

    return img, progress, feedback