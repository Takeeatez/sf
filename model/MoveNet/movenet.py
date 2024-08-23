import cv2
import tensorflow as tf
import numpy as np
import os

# 모델 파일 경로 설정
MODEL_PATH = "/Users/02.011x/Documents/GitHub/sf/model/MoveNet/4.tflite"  # 실제 모델 파일 경로로 변경해야 합니다.

# 모델이 존재하는지 확인
if not os.path.exists(MODEL_PATH):
    print(f"오류: 모델 파일을 찾을 수 없습니다: {MODEL_PATH}")
    print("다음 URL에서 모델을 다운로드하고 경로를 올바르게 설정해주세요:")
    print("https://tfhub.dev/google/lite-model/movenet/singlepose/lightning/tflite/float16/4")
    exit(1)

# 모델 로드
interpreter = tf.lite.Interpreter(model_path=MODEL_PATH)
interpreter.allocate_tensors()

def detect_pose(image):
    # 입력 세부 정보 가져오기
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()

    # 입력 형태 및 타입 확인
    input_shape = input_details[0]['shape']

    # 이미지 전처리
    input_image = cv2.resize(image, (input_shape[1], input_shape[2]))
    input_image = cv2.cvtColor(input_image, cv2.COLOR_BGR2RGB)
    input_image = np.expand_dims(input_image, axis=0)

    # UINT8로 변환 (0-255 범위)
    input_image = input_image.astype(np.uint8)

    # 모델 입력
    interpreter.set_tensor(input_details[0]['index'], input_image)
    
    # 포즈 추정
    interpreter.invoke()
    keypoints = interpreter.get_tensor(output_details[0]['index'])

    return keypoints[0]

def draw_keypoints(image, keypoints):
    y, x, c = image.shape
    shaped = np.squeeze(np.multiply(keypoints, [y,x,1]))

    for kp in shaped:
        ky, kx, kp_conf = kp
        if kp_conf > 0.2:
            cv2.circle(image, (int(kx), int(ky)), 4, (0,255,0), -1) 

    return image

def analyze_squat(keypoints):
    # MoveNet 모델의 키포인트 인덱스
    LEFT_HIP = 11
    LEFT_KNEE = 13
    RIGHT_HIP = 12
    RIGHT_KNEE = 14

    # 키포인트 데이터 구조 확인
    if keypoints.shape[0] == 17 and keypoints.shape[1] == 3:
        left_hip = keypoints[LEFT_HIP]
        left_knee = keypoints[LEFT_KNEE]
        right_hip = keypoints[RIGHT_HIP]
        right_knee = keypoints[RIGHT_KNEE]

        # y 좌표는 두 번째 요소 (인덱스 1)
        if left_hip[1] > left_knee[1] and right_hip[1] > right_knee[1]:
            return "스쿼트 자세가 정확합니다."
        else:
            return "무릎을 더 구부리세요."
    else:
        return "포즈를 감지할 수 없습니다."

def main():
    # 웹캠 열기
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("웹캠을 열 수 없습니다.")
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            print("프레임을 캡처할 수 없습니다.")
            break

        # 포즈 추정
        keypoints = detect_pose(frame)

        # 키포인트 그리기
        frame = draw_keypoints(frame, keypoints)

        # 스쿼트 자세 분석
        feedback = analyze_squat(keypoints)
        cv2.putText(frame, feedback, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        # 결과 표시
        cv2.imshow('Pose Estimation', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()