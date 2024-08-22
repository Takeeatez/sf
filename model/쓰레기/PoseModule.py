import cv2
import mediapipe as mp
import numpy as np
from collections import deque

class ImprovedPoseDetector:
    def __init__(self, mode=False, model_complexity=2, smooth_landmarks=True,
                 enable_segmentation=False, smooth_segmentation=True,
                 min_detection_confidence=0.5, min_tracking_confidence=0.5):
        self.mpDraw = mp.solutions.drawing_utils
        self.mpPose = mp.solutions.pose
        self.pose = self.mpPose.Pose(
            static_image_mode=mode,
            model_complexity=model_complexity,
            smooth_landmarks=smooth_landmarks,
            enable_segmentation=enable_segmentation,
            smooth_segmentation=smooth_segmentation,
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence
        )
        self.landmark_history = {i: deque(maxlen=30) for i in range(33)}  # 33 landmarks
        self.kf = None

    def initialize_kalman_filter(self):
        self.kf = cv2.KalmanFilter(4, 2)  # 4 state variables (x, y, dx, dy), 2 measurement variables (x, y)
        self.kf.measurementMatrix = np.array([[1, 0, 0, 0],
                                              [0, 1, 0, 0]], np.float32)
        self.kf.transitionMatrix = np.array([[1, 0, 1, 0],
                                             [0, 1, 0, 1],
                                             [0, 0, 1, 0],
                                             [0, 0, 0, 1]], np.float32)
        self.kf.processNoiseCov = np.array([[1, 0, 0, 0],
                                            [0, 1, 0, 0],
                                            [0, 0, 1, 0],
                                            [0, 0, 0, 1]], np.float32) * 0.03

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
                
                # Initialize Kalman filter if not already initialized
                if self.kf is None:
                    self.initialize_kalman_filter()
                    self.kf.statePre = np.array([[cx], [cy], [0], [0]], np.float32)
                
                # Apply Kalman filter
                measured = np.array([[np.float32(cx)], [np.float32(cy)]])
                self.kf.correct(measured)
                predicted = self.kf.predict()
                cx, cy = int(predicted[0]), int(predicted[1])

                # Store landmark history
                self.landmark_history[id].append((cx, cy))
                
                # Smooth landmarks using moving average
                if len(self.landmark_history[id]) == 30:
                    smoothed = np.mean(self.landmark_history[id], axis=0)
                    cx, cy = int(smoothed[0]), int(smoothed[1])

                self.lmList.append([id, cx, cy])
                if draw:
                    cv2.circle(img, (cx, cy), 5, (255, 0, 0), cv2.FILLED)
        return self.lmList

    def calculate_angle(self, a, b, c):
        a = np.array(a)  # First point
        b = np.array(b)  # Mid point
        c = np.array(c)  # End point
        
        radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
        angle = np.abs(radians*180.0/np.pi)
        
        if angle > 180.0:
            angle = 360 - angle
        
        return angle

    def findAngle(self, img, p1, p2, p3, draw=True):
        # Get the landmarks
        x1, y1 = self.lmList[p1][1:]
        x2, y2 = self.lmList[p2][1:]
        x3, y3 = self.lmList[p3][1:]

        # Calculate the Angle
        angle = self.calculate_angle([x1, y1], [x2, y2], [x3, y3])

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

    def get_pose_classification(self, lmList):
        # Implement pose classification logic here
        # This is a placeholder and should be replaced with actual classification logic
        return "Unknown Pose"