from flask_cors import CORS
from flask import Flask, render_template, Response, request, jsonify
import cv2
import numpy as np
import mediapipe as mp
from main_model import poseDetector, analyze_squat, analyze_pushup, analyze_pullup, put_korean_text, save_exercise_data
from datetime import datetime
import json
import os

app = Flask(__name__, template_folder='../../src/main/resources/templates')
CORS(app)
camera = cv2.VideoCapture(0)
detector = poseDetector()

exercise_data = {
    'exercise_type': "",
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


# 비디오 스트리밍 및 포즈 감지
def generate_frames():
    global count, dir, current_set, total_accuracy, total_count, start_time
    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            frame = cv2.flip(frame, 1)
            frame = detector.findPose(frame)
            lmList = detector.findPosition(frame, draw=False)

            if len(lmList) != 0 and exercise_data['exercise_type'] != "":
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
                    frame = put_korean_text(frame, fb, (10, 150 + i * 40), 30, (0, 0, 255))

                # 세트당 반복 횟수가 다 찼을 때만 세트 수 증가
                if int(count) == exercise_data["reps"]:
                    current_set += 1
                    count = 0  # 반복 횟수 초기화
                    if current_set >= exercise_data["sets"]:  # 세트 완료
                        end_time = datetime.now()
                        duration = (end_time - start_time).total_seconds()
                        avg_accuracy = (total_accuracy / total_count) if total_count > 0 else 0
                        save_exercise_data(exercise_data["exercise_type"], exercise_data["sets"], exercise_data["reps"],
                                           avg_accuracy, duration)
                        break

            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()

            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


# 기본 페이지 라우팅
@app.route('/')
def index():
    return render_template('setting.html')


# 비디오 스트리밍 라우팅
@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


# 운동 설정
@app.route('/set_exercise', methods=['POST'])
def set_exercise():
    global exercise_data, current_set, count, dir, total_accuracy, total_count, start_time

    # JSON 데이터 가져오기
    data = request.get_json()

    # 운동 유형 변환
    exercise_type_map = {
        1: "스쿼트",
        2: "푸시업",
        3: "풀업"
    }

    # 1. exercise_type 유효성 검사
    exercise_type = exercise_type_map.get(data.get('exercise_type'))
    if not exercise_type:
        return jsonify({'status': 'error', 'message': 'Invalid or missing exercise type'}), 400

    # 2. sets 유효성 검사
    sets = data.get('sets')
    if not sets or not isinstance(sets, int) or sets <= 0:
        return jsonify({'status': 'error', 'message': 'Invalid or missing sets value'}), 400

    # 3. reps 유효성 검사
    reps = data.get('reps')
    if not reps or not isinstance(reps, int) or reps <= 0:
        return jsonify({'status': 'error', 'message': 'Invalid or missing reps value'}), 400

    # 모든 유효성 검사를 통과한 경우 데이터 저장
    exercise_data['exercise_type'] = exercise_type
    exercise_data['sets'] = sets
    exercise_data['reps'] = reps

    current_set = 0  # 세트 수를 0으로 초기화
    count = 0
    dir = 0
    total_accuracy = 0
    total_count = 0
    start_time = datetime.now()
    return jsonify({'status': 'success', 'exercise': exercise_type})


if __name__ == '__main__':
    app.run(debug=True)
