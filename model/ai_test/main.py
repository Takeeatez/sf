import cv2
import numpy as np
import tensorflow as tf
import tensorflow_hub as hub
from collections import deque
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

class AITrainer:
    def __init__(self):
        self.model = hub.load('https://tfhub.dev/google/movenet/singlepose/lightning/4')
        self.movenet = self.model.signatures['serving_default']
        self.exercise_mode = "bicep_curl"
        self.rep_counter = 0
        self.stage = None
        self.angle_history = deque(maxlen=10)
        self.session_start_time = None
        self.session_data = []
        self.db_conn = sqlite3.connect('workout_sessions.db')
        self.create_table()
        self.posture_score = 100
        self.keypoints = None
        self.angle = 0

    def create_table(self):
        cursor = self.db_conn.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS workout_sessions
        (id INTEGER PRIMARY KEY AUTOINCREMENT,
         date TEXT,
         exercise TEXT,
         reps INTEGER,
         duration INTEGER,
         avg_angle REAL,
         avg_posture_score REAL)
        ''')
        self.db_conn.commit()

    def start_session(self):
        self.session_start_time = datetime.now()
        self.session_data = []
        self.posture_score = 100

    def end_session(self):
        if self.session_start_time:
            duration = (datetime.now() - self.session_start_time).seconds
            avg_angle = sum(angle for _, angle in self.session_data) / len(self.session_data) if self.session_data else 0
            
            cursor = self.db_conn.cursor()
            cursor.execute('''
            INSERT INTO workout_sessions (date, exercise, reps, duration, avg_angle, avg_posture_score)
            VALUES (?, ?, ?, ?, ?, ?)
            ''', (self.session_start_time.strftime("%Y-%m-%d %H:%M:%S"),
                  self.exercise_mode,
                  self.rep_counter,
                  duration,
                  avg_angle,
                  self.posture_score))
            self.db_conn.commit()
            
            self.session_start_time = None
            self.session_data = []
            self.rep_counter = 0
            self.posture_score = 100

    def calculate_angle(self, a, b, c):
        a = np.array(a)
        b = np.array(b)
        c = np.array(c)
        radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
        angle = np.abs(radians*180.0/np.pi)
        if angle > 180.0:
            angle = 360 - angle
        return angle

    def check_bicep_curl_posture(self):
        shoulder = self.keypoints[5]
        elbow = self.keypoints[7]
        wrist = self.keypoints[9]

        angle = self.calculate_angle(shoulder[:2], elbow[:2], wrist[:2])

        feedback = []
        score_deduction = 0
        
        if angle > 160:
            feedback.append("Lower the weight")
            score_deduction += 5
        elif angle < 30:
            feedback.append("Curl the weight higher")
            score_deduction += 5

        hip = self.keypoints[11]
        upper_arm_angle = self.calculate_angle(shoulder[:2], elbow[:2], hip[:2])
        if upper_arm_angle < 150:
            feedback.append("Keep your upper arm close to your body")
            score_deduction += 10

        self.posture_score = max(0, self.posture_score - score_deduction)
        return feedback, angle

    def check_pushup_posture(self):
        shoulder = self.keypoints[5]
        elbow = self.keypoints[7]
        wrist = self.keypoints[9]
        hip = self.keypoints[11]
        knee = self.keypoints[13]
        ankle = self.keypoints[15]

        elbow_angle = self.calculate_angle(shoulder[:2], elbow[:2], wrist[:2])
        body_angle = self.calculate_angle(shoulder[:2], hip[:2], ankle[:2])

        feedback = []
        score_deduction = 0

        if elbow_angle < 80:
            feedback.append("Lower your body more")
            score_deduction += 5
        elif elbow_angle > 160:
            feedback.append("Bend your elbows more")
            score_deduction += 5

        if abs(body_angle - 180) > 15:
            feedback.append("Keep your body straight")
            score_deduction += 10

        self.posture_score = max(0, self.posture_score - score_deduction)
        return feedback, elbow_angle

    def check_pullup_posture(self):
        shoulder = self.keypoints[5]
        elbow = self.keypoints[7]
        wrist = self.keypoints[9]
        hip = self.keypoints[11]

        elbow_angle = self.calculate_angle(shoulder[:2], elbow[:2], wrist[:2])
        body_angle = self.calculate_angle(shoulder[:2], hip[:2], (hip[0], shoulder[1]))

        feedback = []
        score_deduction = 0

        if elbow_angle > 90:
            feedback.append("Pull yourself higher")
            score_deduction += 10

        if abs(body_angle - 180) > 15:
            feedback.append("Keep your body vertical")
            score_deduction += 5

        self.posture_score = max(0, self.posture_score - score_deduction)
        return feedback, elbow_angle

    def check_squat_posture(self):
        hip = self.keypoints[11]
        knee = self.keypoints[13]
        ankle = self.keypoints[15]
        shoulder = self.keypoints[5]

        knee_angle = self.calculate_angle(hip[:2], knee[:2], ankle[:2])
        back_angle = self.calculate_angle(shoulder[:2], hip[:2], knee[:2])

        feedback = []
        score_deduction = 0

        if knee_angle > 100:
            feedback.append("Squat lower")
            score_deduction += 5
        elif knee_angle < 60:
            feedback.append("Don't go too low")
            score_deduction += 5

        if abs(back_angle - 180) > 20:
            feedback.append("Keep your back straight")
            score_deduction += 10

        self.posture_score = max(0, self.posture_score - score_deduction)
        return feedback, knee_angle

    def process_frame(self, frame):
        img = frame.copy()
        img = tf.image.resize_with_pad(tf.expand_dims(img, axis=0), 192, 192)
        input_img = tf.cast(img, dtype=tf.int32)
        
        results = self.movenet(input_img)
        keypoints = results['output_0'].numpy().squeeze()[:17]

        y, x, c = frame.shape
        shaped = np.squeeze(np.multiply(keypoints, [y, x, 1]))

        self.keypoints = shaped

        if self.exercise_mode == "bicep_curl":
            feedback, angle = self.check_bicep_curl_posture()
        elif self.exercise_mode == "pushup":
            feedback, angle = self.check_pushup_posture()
        elif self.exercise_mode == "pullup":
            feedback, angle = self.check_pullup_posture()
        elif self.exercise_mode == "squat":
            feedback, angle = self.check_squat_posture()

        self.angle = angle

        if self.session_start_time:
            self.session_data.append((datetime.now(), angle))

        # Draw keypoints and connections
        edges = [
            (0, 1), (0, 2), (1, 3), (2, 4), (0, 5), (0, 6), (5, 7), (7, 9),
            (6, 8), (8, 10), (5, 6), (5, 11), (6, 12), (11, 12), (11, 13),
            (13, 15), (12, 14), (14, 16)
        ]

        for edge in edges:
            p1, p2 = edge
            y1, x1, c1 = shaped[p1]
            y2, x2, c2 = shaped[p2]
            if c1 > 0.1 and c2 > 0.1:
                cv2.line(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)

        for kp in shaped:
            ky, kx, kp_conf = kp
            if kp_conf > 0.1:
                cv2.circle(frame, (int(kx), int(ky)), 5, (0, 255, 0), -1)

        # Display feedback and stats
        cv2.putText(frame, f"{self.exercise_mode}: {self.rep_counter} reps", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(frame, f"Angle: {self.angle:.2f}", (10, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(frame, f"Posture Score: {self.posture_score}", (10, 90),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        for i, fb in enumerate(feedback):
            cv2.putText(frame, fb, (10, 120 + 30*i), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

        return frame

    def get_analytics(self):
        df = pd.read_sql_query("SELECT * FROM workout_sessions", self.db_conn)
        
        total_reps = df.groupby('exercise')['reps'].sum()
        avg_duration = df.groupby('exercise')['duration'].mean()
        df['date'] = pd.to_datetime(df['date'])
        reps_trend = df.set_index('date').groupby('exercise')['reps'].resample('D').sum().unstack(level=0)
        avg_posture_score = df.groupby('exercise')['avg_posture_score'].mean()
        
        return total_reps, avg_duration, reps_trend, avg_posture_score

def main():
    trainer = AITrainer()
    cap = cv2.VideoCapture(0)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame = trainer.process_frame(frame)
        cv2.imshow('AI Personal Trainer', frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('s'):
            trainer.start_session()
            print("Session started!")
        elif key == ord('e'):
            trainer.end_session()
            print("Session ended and saved!")
        elif key == ord('b'):
            trainer.exercise_mode = "bicep_curl"
            trainer.rep_counter = 0
        elif key == ord('p'):
            trainer.exercise_mode = "pushup"
            trainer.rep_counter = 0
        elif key == ord('u'):
            trainer.exercise_mode = "pullup"
            trainer.rep_counter = 0
        elif key == ord('t'):
            trainer.exercise_mode = "squat"
            trainer.rep_counter = 0
        elif key == ord('a'):
            total_reps, avg_duration, reps_trend, avg_posture_score = trainer.get_analytics()
            
            plt.figure(figsize=(15, 10))
            plt.subplot(221)
            total_reps.plot(kind='bar')
            plt.title('Total Reps by Exercise')
            plt.ylabel('Total Reps')
            
            plt.subplot(222)
            avg_duration.plot(kind='bar')
            plt.title('Average Session Duration by Exercise')
            plt.ylabel('Duration (seconds)')
            
            plt.subplot(223)
            reps_trend.plot()
            plt.title('Reps Trend Over Time')
            plt.ylabel('Reps')
            
            plt.subplot(224)
            avg_posture_score.plot(kind='bar')
            plt.title('Average Posture Score by Exercise')
            plt.ylabel('Score')
            
            plt.tight_layout()
            plt.show()

    cap.release()
    cv2.destroyAllWindows()
    trainer.db_conn.close()

if __name__ == "__main__":
    main()