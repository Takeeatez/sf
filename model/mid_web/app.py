from flask import Flask, render_template, Response, jsonify
import cv2
from main_model import poseDetector, analyze_squat, analyze_pushup, analyze_pullup

app = Flask(__name__)

detector = poseDetector()

def gen_frames():
    cap = cv2.VideoCapture(0)
    while True:
        success, img = cap.read()
        if not success:
            break
        else:
            img = cv2.flip(img, 1)
            img = detector.findPose(img)
            detector.findPosition(img, draw=False)
            ret, buffer = cv2.imencode('.jpg', img)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/exercise/<exercise_type>')
def exercise(exercise_type):
    return render_template('exercise.html', exercise_type=exercise_type)

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/analyze/<exercise_type>')
def analyze(exercise_type):
    if len(detector.lmList) != 0:
        if exercise_type == "squat":
            angle, feedback = analyze_squat(detector, detector.lmList)
        elif exercise_type == "pushup":
            angle, feedback = analyze_pushup(detector, detector.lmList)
        elif exercise_type == "pullup":
            angle, feedback = analyze_pullup(detector, detector.lmList)
        else:
            return jsonify({'error': 'Unknown exercise type'})
        return jsonify({'angle': angle, 'feedback': feedback})
    return jsonify({'error': 'No landmarks detected'})

if __name__ == '__main__':
    app.run(debug=True)