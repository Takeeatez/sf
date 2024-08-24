const ANGLE_THRESHOLD = 15;

export function detectSquat(pose) {
    const leftHip = pose.keypoints.find(kp => kp.part === 'leftHip');
    const leftKnee = pose.keypoints.find(kp => kp.part === 'leftKnee');
    const leftAnkle = pose.keypoints.find(kp => kp.part === 'leftAnkle');
    const rightHip = pose.keypoints.find(kp => kp.part === 'rightHip');
    const rightKnee = pose.keypoints.find(kp => kp.part === 'rightKnee');
    const rightAnkle = pose.keypoints.find(kp => kp.part === 'rightAnkle');

    const leftKneeAngle = calculateAngle(leftHip, leftKnee, leftAnkle);
    const rightKneeAngle = calculateAngle(rightHip, rightKnee, rightAnkle);
    const leftHipAngle = calculateAngle(
        pose.keypoints.find(kp => kp.part === 'leftShoulder'),
        leftHip,
        leftKnee
    );
    const rightHipAngle = calculateAngle(
        pose.keypoints.find(kp => kp.part === 'rightShoulder'),
        rightHip,
        rightKnee
    );

    const isKneeAngleCorrect = 
        (leftKneeAngle >= 65 && leftKneeAngle <= 165) &&
        (rightKneeAngle >= 65 && rightKneeAngle <= 165) &&
        Math.abs(leftKneeAngle - rightKneeAngle) <= ANGLE_THRESHOLD;

    const isHipAngleCorrect = 
        (leftHipAngle >= 50 && leftHipAngle <= 165) &&
        (rightHipAngle >= 50 && rightHipAngle <= 165) &&
        Math.abs(leftHipAngle - rightHipAngle) <= ANGLE_THRESHOLD;

    const isKneeAligned = 
        Math.abs(leftKnee.position.x - leftAnkle.position.x) <= 0.1 &&
        Math.abs(rightKnee.position.x - rightAnkle.position.x) <= 0.1;

    return {
        isCorrect: isKneeAngleCorrect && isHipAngleCorrect && isKneeAligned,
        feedback: generateSquatFeedback(isKneeAngleCorrect, isHipAngleCorrect, isKneeAligned)
    };
}

export function detectPushup(pose) {
    const leftShoulder = pose.keypoints.find(kp => kp.part === 'leftShoulder');
    const leftElbow = pose.keypoints.find(kp => kp.part === 'leftElbow');
    const leftWrist = pose.keypoints.find(kp => kp.part === 'leftWrist');
    const rightShoulder = pose.keypoints.find(kp => kp.part === 'rightShoulder');
    const rightElbow = pose.keypoints.find(kp => kp.part === 'rightElbow');
    const rightWrist = pose.keypoints.find(kp => kp.part === 'rightWrist');

    const leftElbowAngle = calculateAngle(leftShoulder, leftElbow, leftWrist);
    const rightElbowAngle = calculateAngle(rightShoulder, rightElbow, rightWrist);

    const isElbowAngleCorrect = 
        (leftElbowAngle >= 70 && leftElbowAngle <= 110) &&
        (rightElbowAngle >= 70 && rightElbowAngle <= 110) &&
        Math.abs(leftElbowAngle - rightElbowAngle) <= ANGLE_THRESHOLD;

    const isBodyAligned = checkBodyAlignment(pose);

    return {
        isCorrect: isElbowAngleCorrect && isBodyAligned,
        feedback: generatePushupFeedback(isElbowAngleCorrect, isBodyAligned)
    };
}

export function detectPlank(pose) {
    const leftShoulder = pose.keypoints.find(kp => kp.part === 'leftShoulder');
    const leftHip = pose.keypoints.find(kp => kp.part === 'leftHip');
    const leftAnkle = pose.keypoints.find(kp => kp.part === 'leftAnkle');
    const rightShoulder = pose.keypoints.find(kp => kp.part === 'rightShoulder');
    const rightHip = pose.keypoints.find(kp => kp.part === 'rightHip');
    const rightAnkle = pose.keypoints.find(kp => kp.part === 'rightAnkle');

    const isBodyStraight = 
        Math.abs(calculateAngle(leftShoulder, leftHip, leftAnkle) - 180) <= ANGLE_THRESHOLD &&
        Math.abs(calculateAngle(rightShoulder, rightHip, rightAnkle) - 180) <= ANGLE_THRESHOLD;

    const isHipAligned = Math.abs(leftHip.position.y - rightHip.position.y) <= 0.1;

    return {
        isCorrect: isBodyStraight && isHipAligned,
        feedback: generatePlankFeedback(isBodyStraight, isHipAligned)
    };
}

function calculateAngle(pointA, pointB, pointC) {
    const vectorBA = { x: pointA.position.x - pointB.position.x, y: pointA.position.y - pointB.position.y };
    const vectorBC = { x: pointC.position.x - pointB.position.x, y: pointC.position.y - pointB.position.y };
    
    const dotProduct = vectorBA.x * vectorBC.x + vectorBA.y * vectorBC.y;
    const magnitudeBA = Math.sqrt(vectorBA.x * vectorBA.x + vectorBA.y * vectorBA.y);
    const magnitudeBC = Math.sqrt(vectorBC.x * vectorBC.x + vectorBC.y * vectorBC.y);
    
    const angle = Math.acos(dotProduct / (magnitudeBA * magnitudeBC));
    return angle * (180 / Math.PI);
}

function checkBodyAlignment(pose) {
    const shoulder = pose.keypoints.find(kp => kp.part === 'leftShoulder');
    const hip = pose.keypoints.find(kp => kp.part === 'leftHip');
    const ankle = pose.keypoints.find(kp => kp.part === 'leftAnkle');

    const bodyAngle = calculateAngle(shoulder, hip, ankle);
    return Math.abs(bodyAngle - 180) <= ANGLE_THRESHOLD;
}

function generateSquatFeedback(isKneeAngleCorrect, isHipAngleCorrect, isKneeAligned) {
    let feedback = [];
    if (!isKneeAngleCorrect) {
        feedback.push("무릎 각도를 조정하세요. 90도에 가깝게 구부려야 합니다.");
    }
    if (!isHipAngleCorrect) {
        feedback.push("엉덩이를 더 뒤로 빼세요. 상체를 약간 앞으로 기울이세요.");
    }
    if (!isKneeAligned) {
        feedback.push("무릎이 발끝을 넘어가지 않도록 주의하세요.");
    }
    return feedback;
}

function generatePushupFeedback(isElbowAngleCorrect, isBodyAligned) {
    let feedback = [];
    if (!isElbowAngleCorrect) {
        feedback.push("팔꿈치 각도를 90도에 가깝게 유지하세요.");
    }
    if (!isBodyAligned) {
        feedback.push("몸을 일직선으로 유지하세요. 엉덩이가 처지거나 올라가지 않도록 주의하세요.");
    }
    return feedback;
}

function generatePlankFeedback(isBodyStraight, isHipAligned) {
    let feedback = [];
    if (!isBodyStraight) {
        feedback.push("몸을 일직선으로 유지하세요. 등이 굽거나 엉덩이가 처지지 않도록 주의하세요.");
    }
    if (!isHipAligned) {
        feedback.push("엉덩이 높이를 조정하세요. 너무 높거나 낮지 않아야 합니다.");
    }
    return feedback;
}

export function detectPullup(pose) {
    const leftShoulder = pose.keypoints.find(kp => kp.part === 'leftShoulder');
    const leftElbow = pose.keypoints.find(kp => kp.part === 'leftElbow');
    const leftWrist = pose.keypoints.find(kp => kp.part === 'leftWrist');
    const rightShoulder = pose.keypoints.find(kp => kp.part === 'rightShoulder');
    const rightElbow = pose.keypoints.find(kp => kp.part === 'rightElbow');
    const rightWrist = pose.keypoints.find(kp => kp.part === 'rightWrist');

    const leftArmAngle = calculateAngle(leftShoulder, leftElbow, leftWrist);
    const rightArmAngle = calculateAngle(rightShoulder, rightElbow, rightWrist);

    const isArmExtended = leftArmAngle > 150 && rightArmAngle > 150;
    const isArmFlexed = leftArmAngle < 60 && rightArmAngle < 60;

    const isShoulderAligned = Math.abs(leftShoulder.position.y - rightShoulder.position.y) < 0.1;
    
    let stage = '';
    if (isArmExtended) {
        stage = 'down';
    } else if (isArmFlexed) {
        stage = 'up';
    }

    const isCorrect = isShoulderAligned && (stage === 'up' || stage === 'down');

    return {
        isCorrect: isCorrect,
        feedback: generatePullupFeedback(isShoulderAligned, stage),
        stage: stage
    };
}

function generatePullupFeedback(isShoulderAligned, stage) {
    let feedback = [];
    if (!isShoulderAligned) {
        feedback.push("어깨를 수평으로 유지하세요.");
    }
    if (stage === '') {
        feedback.push("팔을 완전히 펴거나 턱을 바에 닿게 당기세요.");
    }
    return feedback;
}