import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="google.protobuf.symbol_database")

import cv2
import numpy as np
import time
import PoseModule as pm
from datetime import datetime
import json
from PIL import ImageFont, ImageDraw, Image
from collections import deque

# 포즈 감지기 초기화
detector = pm.poseDetector()

# 전역 변수 설정
count_right_arm = 0
count_left_arm = 0
count_squat = 0
dir_right_arm = 0
dir_left_arm = 0
dir_squat = 0
pTime = 0
exercise_type = ""
target_reps = 0
target_sets = 0
current_set = 1
elbow_pos_right = None
elbow_pos_left = None
elbow_fixed = False
accuracy_list = []
per_right_arm = 0
per_left_arm = 0
per_squat = 0

# 팔꿈치 위치 추적을 위한 변수
elbow_positions = {'right': deque(maxlen=30), 'left': deque(maxlen=30)}  # 3초(30fps * 3초) 1초는 30 *1 
stable_duration = {'right': 0, 'left': 0}

# 한글 폰트 설정 (경로는 시스템에 맞게 수정 필요)
font_path = "/System/Library/Fonts/AppleSDGothicNeo.ttc"
font = ImageFont.truetype(font_path, 32)
small_font = ImageFont.truetype(font_path, 24)

# 운동 기록 저장을 위한 딕셔너리
exercise_history = {}

def save_exercise_history():
    global exercise_history, accuracy_list
    date = datetime.now().strftime("%Y-%m-%d")
    time_now = datetime.now().strftime("%H:%M:%S")
    
    if date not in exercise_history:
        exercise_history[date] = []
    
    avg_accuracy = sum(accuracy_list) / len(accuracy_list) if accuracy_list else 0
    
    exercise_data = {
        "time": time_now,
        "exercise_type": exercise_type,
        "sets": current_set - 1,
        "target_sets": target_sets,
        "target_reps": target_reps,
        "avg_accuracy": round(avg_accuracy, 2)
    }
    
    if exercise_type == "아령 들기":
        exercise_data.update({
            "right_arm_reps": int(count_right_arm),
            "left_arm_reps": int(count_left_arm)
        })
    else:
        exercise_data.update({
            "squat_reps": int(count_squat)
        })
    
    exercise_history[date].append(exercise_data)
    
    with open('exercise_history.json', 'w', encoding='utf-8') as f:
        json.dump(exercise_history, f, ensure_ascii=False, indent=4)

def load_exercise_history():
    global exercise_history
    try:
        with open('exercise_history.json', 'r', encoding='utf-8') as f:
            exercise_history = json.load(f)
    except FileNotFoundError:
        exercise_history = {}

def get_user_input():
    global exercise_type, target_reps, target_sets
    
    while True:
        print("\n운동을 선택하세요: ")
        print("1. 아령 들기")
        print("2. 스쿼트")
        choice = input("선택 (1 또는 2): ")
        
        if choice in ['1', '2']:
            exercise_type = "아령 들기" if choice == "1" else "스쿼트"
            break
        else:
            print("잘못된 선택입니다. 1 또는 2를 입력해주세요.")
    
    while True:
        try:
            target_reps = int(input("목표 반복 횟수를 입력하세요: "))
            if target_reps > 0:
                break
            else:
                print("양수를 입력해주세요.")
        except ValueError:
            print("유효한 숫자를 입력해주세요.")
    
    while True:
        try:
            target_sets = int(input("목표 세트 수를 입력하세요: "))
            if target_sets > 0:
                break
            else:
                print("양수를 입력해주세요.")
        except ValueError:
            print("유효한 숫자를 입력해주세요.")
    
    print(f"\n선택한 운동: {exercise_type}")
    print(f"목표 반복 횟수: {target_reps}")
    print(f"목표 세트 수: {target_sets}")

def put_text(img, text, position, font_color=(255, 255, 255), font_size="normal"):
    pil_img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(pil_img)
    if font_size == "small":
        draw.text(position, text, font=small_font, fill=font_color)
    else:
        draw.text(position, text, font=font, fill=font_color)
    return cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)

def draw_fancy_bar(img, percentage, start_pos, end_pos, color, thickness=30):
    cv2.line(img, start_pos, end_pos, (200, 200, 200), thickness)
    length = int(np.sqrt((end_pos[0] - start_pos[0])**2 + (end_pos[1] - start_pos[1])**2))
    point = (int(start_pos[0] + (end_pos[0] - start_pos[0]) * percentage / 100),
             int(start_pos[1] + (end_pos[1] - start_pos[1]) * percentage / 100))
    cv2.line(img, start_pos, point, color, thickness)
    return img

def check_elbow_stability(side):
    if len(elbow_positions[side]) < 90:  # 3초 동안의 데이터가 없으면 안정적이지 않음
        return False
    
    positions = np.array(list(elbow_positions[side]))
    mean_pos = np.mean(positions, axis=0)
    distances = np.sqrt(np.sum((positions - mean_pos)**2, axis=1))
    return np.mean(distances) < 40  # 평균 거리가 40픽셀 이내면 안정적으로 간주

def main():
    global count_right_arm, count_left_arm, count_squat
    global dir_right_arm, dir_left_arm, dir_squat
    global pTime, exercise_type, target_reps, target_sets, current_set
    global elbow_pos_right, elbow_pos_left, elbow_fixed, accuracy_list
    global per_right_arm, per_left_arm, per_squat
    global stable_duration, elbow_positions

    get_user_input()

    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    while True:
        success, img = cap.read()
        if not success:
            print("카메라에서 프레임을 읽을 수 없습니다.")
            break

        img = cv2.resize(img, (1280, 720))
        img = detector.findPose(img, False)
        lmList = detector.findPosition(img, False)
        
        if len(lmList) != 0:
            if exercise_type == "아령 들기":
                current_right_elbow = lmList[14][1:3]
                current_left_elbow = lmList[13][1:3]
                
                if not elbow_fixed:
                    elbow_positions['right'].append(current_right_elbow)
                    elbow_positions['left'].append(current_left_elbow)

                    right_stable = check_elbow_stability('right')
                    left_stable = check_elbow_stability('left')

                    if right_stable and left_stable:
                        stable_duration['right'] += 1
                        stable_duration['left'] += 1
                        if stable_duration['right'] >= 90 and stable_duration['left'] >= 90:  # 3초 동안 안정적
                            elbow_pos_right = np.mean(list(elbow_positions['right']), axis=0)
                            elbow_pos_left = np.mean(list(elbow_positions['left']), axis=0)
                            elbow_fixed = True
                            print("팔꿈치 위치가 고정되었습니다.")
                    else:
                        stable_duration['right'] = 0
                        stable_duration['left'] = 0

                # 팔꿈치 위치 표시
                cv2.circle(img, tuple(map(int, current_right_elbow)), 10, (0, 255, 0), -1)
                cv2.circle(img, tuple(map(int, current_left_elbow)), 10, (0, 255, 0), -1)
                
                if elbow_fixed:
                    cv2.circle(img, tuple(map(int, elbow_pos_right)), 15, (255, 0, 0), 2)
                    cv2.circle(img, tuple(map(int, elbow_pos_left)), 15, (255, 0, 0), 2)

                # 안내 메시지
                if not elbow_fixed:
                    img = put_text(img, "팔꿈치를 고정 위치에 3초간 유지하세요", (50, 50))
                    img = put_text(img, f"안정화: {min(stable_duration['right'], stable_duration['left'])/30:.1f}/3.0초", (50, 100))
                else:
                    # 운동 중 로직 (각도 계산, 카운트 등)
                    angle_right_arm = detector.findAngle(img, 12, 14, 16)
                    per_right_arm = np.interp(angle_right_arm, (210, 310), (0, 100))
                    
                    angle_left_arm = detector.findAngle(img, 11, 13, 15)
                    per_left_arm = np.interp(angle_left_arm, (210, 310), (0, 100))

                    # 카운트 로직
                    if per_right_arm == 100:
                        if dir_right_arm == 0:
                            count_right_arm += 0.5
                            dir_right_arm = 1
                    if per_right_arm == 0:
                        if dir_right_arm == 1:
                            count_right_arm += 0.5
                            dir_right_arm = 0

                    if per_left_arm == 100:
                        if dir_left_arm == 0:
                            count_left_arm += 0.5
                            dir_left_arm = 1
                    if per_left_arm == 0:
                        if dir_left_arm == 1:
                            count_left_arm += 0.5
                            dir_left_arm = 0

            elif exercise_type == "스쿼트":
                # 스쿼트 로직
                angle_squat = detector.findAngle(img, 24, 26, 28)
                per_squat = np.interp(angle_squat, (210, 310), (100, 0))

                if per_squat == 100:
                    if dir_squat == 0:
                        count_squat += 0.5
                        dir_squat = 1
                if per_squat == 0:
                    if dir_squat == 1:
                        count_squat += 0.5
                        dir_squat = 0

            # 목표 달성 확인 및 UI 표시 로직
            current_count = max(count_right_arm, count_left_arm) if exercise_type == "아령 들기" else count_squat
            if int(current_count) == target_reps:
                if current_set < target_sets:
                    img = put_text(img, f"세트 {current_set} 완료! 다음 세트를 시작하세요.", (50, 200))
                    current_set += 1
                    count_right_arm = 0
                    count_left_arm = 0
                    count_squat = 0
                    # elbow_fixed는 재설정하지 않음
                else:
                    img = put_text(img, "축하합니다! 운동을 완료했습니다!", (50, 200))
                    save_exercise_history()
                    break

            # UI 표시 (오른쪽에 배치)
            info_width = 300
            cv2.rectangle(img, (img.shape[1] - info_width, 0), (img.shape[1], img.shape[0]), (245, 117, 16), -1)
            img = put_text(img, f'{exercise_type}', (img.shape[1] - info_width + 10, 50))
            if exercise_type == "아령 들기":
                img = put_text(img, f'오른팔: {int(count_right_arm)}', (img.shape[1] - info_width + 10, 100))
                img = put_text(img, f'왼팔: {int(count_left_arm)}', (img.shape[1] - info_width + 10, 150))
                img = draw_fancy_bar(img, per_right_arm, (img.shape[1] - info_width + 10, 130), (img.shape[1] - 10, 130), (0, 255, 0), 10)
                img = put_text(img, f'{int(per_right_arm)}%', (img.shape[1] - 50, 125), font_size="small")
                img = draw_fancy_bar(img, per_left_arm, (img.shape[1] - info_width + 10, 180), (img.shape[1] - 10, 180), (0, 255, 0), 10)
                img = put_text(img, f'{int(per_left_arm)}%', (img.shape[1] - 50, 175), font_size="small")
            else:
                img = put_text(img, f'횟수: {int(count_squat)}', (img.shape[1] - info_width + 10, 100))
                img = draw_fancy_bar(img, per_squat, (img.shape[1] - info_width + 10, 130), (img.shape[1] - 10, 130), (0, 255, 0), 10)
                img = put_text(img, f'{int(per_squat)}%', (img.shape[1] - 50, 125), font_size="small")
            
            img = put_text(img, f'세트: {current_set}/{target_sets}', (img.shape[1] - info_width + 10, 230))
            
            # 전체 진행도
            progress = (current_count / target_reps) * 100
            img = draw_fancy_bar(img, progress, (img.shape[1] - info_width + 10, 280), (img.shape[1] - 10, 280), (0, 255, 0), 20)
            img = put_text(img, f'진행도: {int(progress)}%', (img.shape[1] - info_width + 10, 310), font_size="small")

            # 정확도 표시 (팔꿈치 고정 상태일 때만)
            if elbow_fixed and exercise_type == "아령 들기":
                right_accuracy = max(0, 100 - np.sqrt(np.sum((np.array(current_right_elbow) - np.array(elbow_pos_right))**2)))
                left_accuracy = max(0, 100 - np.sqrt(np.sum((np.array(current_left_elbow) - np.array(elbow_pos_left))**2)))
                accuracy = (right_accuracy + left_accuracy) / 2
                accuracy_list.append(accuracy)
                img = put_text(img, f'정확도: {accuracy:.1f}%', (img.shape[1] - info_width + 10, 360))

        cTime = time.time()
        fps = 1 / (cTime - pTime)
        pTime = cTime
        img = put_text(img, f"FPS: {int(fps)}", (11, 30), (255, 255, 255), "small")

        cv2.imshow("AI Personal Trainer", img)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    save_exercise_history()
    print("오늘의 운동 내용이 저장되었습니다.")

if __name__ == "__main__":
    load_exercise_history()
    main()