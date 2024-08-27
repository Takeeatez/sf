from flask import Flask, render_template, Response, request, jsonify
import cv2
import numpy as np
import mediapipe as mp
from main_model import poseDetector, analyze_squat, analyze_pushup, analyze_pullup, put_korean_text, save_exercise_data
from datetime import datetime
import json
import os

# Flask 애플리케이션 초기화 시 템플릿 경로 지정
app = Flask(__name__, template_folder='/Users/02.011x/Documents/GitHub/sf/src/main/resources/templates/webcam.html')
camera = cv2.VideoCapture(0)
detector = poseDetector()

exercise_data = {
    'exercise_type': '',
    'sets': 0,
    'reps': 0,
    'accuracy': 0,
    'duration': 0
}

current_set = 0  # 세트 수를 0으로 초기화
count = 0
dir = 0
total_accuracy = 0
total_count = 0
start_time = None
exercise_finished = False  # 운동 종료 상태 플래그
exercise_checked = False  # 운동 종료가 체크되었는지 여부 플래그

# 비디오 스트리밍 및 포즈 감지
def generate_frames():
    global count, dir, current_set, total_accuracy, total_count, start_time, exercise_finished, exercise_checked
    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            frame = cv2.flip(frame, 1)
            frame = detector.findPose(frame)
            lmList = detector.findPosition(frame, draw=False)

            if len(lmList) != 0 and exercise_data['exercise_type'] != '' and not exercise_finished:
                if exercise_data['exercise_type'] == "스쿼트":
                    angle, feedback = analyze_squat(detector, frame)
                    per = np.interp(angle, (90, 160), (100, 0))
                elif exercise_data['exercise_type'] == "푸시업":
                    angle, feedback = analyze_pushup(detector, frame)
                    per = np.interp(angle, (70, 160), (100, 0))
                elif exercise_data['exercise_type'] == "풀업":
                    angle, feedback = analyze_pullup(detector, frame)
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
                frame = put_korean_text(frame, f'운동: {exercise_data["exercise_type"]}', (10, 30), 30, color)
                frame = put_korean_text(frame, f'세트: {current_set}/{exercise_data["sets"]}', (10, 70), 30, color)
                frame = put_korean_text(frame, f'횟수: {int(count)}/{exercise_data["reps"]}', (10, 110), 30, color)

                for i, fb in enumerate(feedback):
                    frame = put_korean_text(frame, fb, (10, 150 + i*40), 30, (0, 0, 255))

                # 세트당 반복 횟수가 다 찼을 때만 세트 수 증가
                if int(count) == exercise_data["reps"]:
                    current_set += 1
                    count = 0  # 반복 횟수 초기화
                    if current_set >= exercise_data["sets"]:  # 세트 완료
                        end_time = datetime.now()
                        duration = (end_time - start_time).total_seconds()
                        avg_accuracy = (total_accuracy / total_count) if total_count > 0 else 0
                        save_exercise_data(exercise_data["exercise_type"], exercise_data["sets"], exercise_data["reps"], avg_accuracy, duration)
                        exercise_finished = True  # 운동 종료 상태 설정
                        exercise_checked = False  # 운동 종료 상태를 아직 확인하지 않음

            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()

            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

# 기본 페이지 라우팅
@app.route('/')
def index():
    return render_template('index.html')  # my_templates 폴더에서 index.html 파일을 찾음

# 비디오 스트리밍 라우팅
@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

# 운동 설정
@app.route('/set_exercise', methods=['POST'])
def set_exercise():
    global exercise_data, current_set, count, dir, total_accuracy, total_count, start_time, exercise_finished, exercise_checked
    exercise_data['exercise_type'] = request.form.get('exercise_type')
    exercise_data['sets'] = int(request.form.get('sets'))
    exercise_data['reps'] = int(request.form.get('reps'))
    current_set = 0  # 세트 수를 0으로 초기화
    count = 0
    dir = 0
    total_accuracy = 0
    total_count = 0
    start_time = datetime.now()
    exercise_finished = False  # 운동 종료 상태 초기화
    exercise_checked = False  # 운동 종료 확인 상태 초기화
    return jsonify({'status': 'success', 'exercise': exercise_data['exercise_type']})

# 운동 종료 상태 확인 라우팅
@app.route('/check_exercise_status')
def check_exercise_status():
    global exercise_finished, exercise_checked
    if exercise_finished and not exercise_checked:
        exercise_checked = True  # 종료 상태를 확인했으므로 플래그 업데이트
        return jsonify({'finished': True})
    else:
        return jsonify({'finished': False})

if __name__ == '__main__':
    app.run(debug=True)
