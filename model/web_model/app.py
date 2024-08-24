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
current_reps = 0
current_set = 0
exercise_state = 'start'  # 'start', 'up', 'down'

def gen_frames():
    global exercise_type, target_reps, target_sets, current_reps, current_set, exercise_state
    
    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            frame = cv2.flip(frame, 1)
            
            if exercise_type:
                if exercise_type == 'squat':
                    frame, progress, feedback = process_squat(frame, detector)
                elif exercise_type == 'pushup':
                    frame, progress, feedback = process_pushup(frame, detector)
                elif exercise_type == 'pullup':
                    frame, progress, feedback = process_pullup(frame, detector)
                
                # 운동 상태 및 횟수 계산
                if progress == 100 and exercise_state != 'up':
                    exercise_state = 'up'
                elif progress == 0 and exercise_state == 'up':
                    exercise_state = 'down'
                    current_reps += 1
                    
                    # 세트 완료 확인
                    if current_reps == target_reps:
                        current_set += 1
                        current_reps = 0
                        if current_set == target_sets:
                            exercise_type = None  # 운동 완료
                
                # 화면에 정보 표시
                cv2.putText(frame, f'Exercise: {exercise_type}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                cv2.putText(frame, f'Set: {current_set + 1}/{target_sets}', (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                cv2.putText(frame, f'Rep: {current_reps}/{target_reps}', (10, 110), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                
                # 피드백 표시
                for i, fb in enumerate(feedback):
                    cv2.putText(frame, fb, (10, 150 + i*40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            
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
    global exercise_type, target_reps, target_sets, current_reps, current_set, exercise_state
    data = request.json
    exercise_type = data['exercise_type']
    target_reps = int(data['target_reps'])
    target_sets = int(data['target_sets'])
    current_reps = 0
    current_set = 0
    exercise_state = 'start'
    return jsonify({"status": "success"})

@app.route('/end_exercise', methods=['POST'])
def end_exercise():
    global exercise_type, current_reps, current_set
    # 여기에 운동 데이터 저장 로직 추가
    exercise_type = None
    return jsonify({"status": "success", "message": "Exercise ended and data saved"})

if __name__ == '__main__':
    app.run(debug=True)