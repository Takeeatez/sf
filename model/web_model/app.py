from flask import Flask, render_template, Response, request, jsonify
import cv2
from utils import poseDetector
from models.squat import process_squat
from models.pushup import process_pushup
from models.pullup import process_pullup

app = Flask(__name__)

camera = cv2.VideoCapture(0)
detector = poseDetector()

exercise_type = None
target_reps = 0
target_sets = 0

def gen_frames():
    global exercise_type, target_reps, target_sets
    count = 0
    set_count = 0
    
    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            frame = cv2.flip(frame, 1)
            
            if exercise_type == 'squat':
                frame, progress, feedback = process_squat(frame, detector)
            elif exercise_type == 'pushup':
                frame, progress, feedback = process_pushup(frame, detector)
            elif exercise_type == 'pullup':
                frame, progress, feedback = process_pullup(frame, detector)
            else:
                # 운동이 선택되지 않았을 때의 처리
                continue
            
            # 운동 횟수와 세트 카운트
            if progress == 100:
                count += 1
                if count == target_reps:
                    set_count += 1
                    count = 0
                    if set_count == target_sets:
                        # 운동 완료 처리
                        exercise_type = None
            
            # 화면에 정보 표시
            cv2.putText(frame, f'Exercise: {exercise_type}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.putText(frame, f'Rep: {count}/{target_reps}', (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.putText(frame, f'Set: {set_count}/{target_sets}', (10, 110), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/exercise')
def exercise():
    return render_template('exercise.html')

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/set_exercise', methods=['POST'])
def set_exercise():
    global exercise_type, target_reps, target_sets
    data = request.json
    exercise_type = data['exercise_type']
    target_reps = int(data['target_reps'])
    target_sets = int(data['target_sets'])
    return jsonify({"status": "success"})

if __name__ == '__main__':
    app.run(debug=True)