import { setupCamera, initializePoseNet, detectPose, drawPose } from './poseDetection.js';
import { detectSquat, detectPushup, detectPlank } from './exerciseDetection.js';
import { updateFeedback, resetCounter } from './feedback.js';

let currentExercise = 'squat';

async function init() {
    const video = await setupCamera();
    video.play();
    const net = await initializePoseNet();
    const canvas = document.getElementById('output');
    const ctx = canvas.getContext('2d');

    canvas.width = video.width;
    canvas.height = video.height;

    setupExerciseButtons();

    detectFrame(video, net, ctx);
}

function setupExerciseButtons() {
    document.getElementById('squat-btn').addEventListener('click', () => {
        currentExercise = 'squat';
        resetCounter();
    });
    document.getElementById('pushup-btn').addEventListener('click', () => {
        currentExercise = 'pushup';
        resetCounter();
    });
    document.getElementById('plank-btn').addEventListener('click', () => {
        currentExercise = 'plank';
        resetCounter();
    });
}

async function detectFrame(video, net, ctx) {
    const pose = await detectPose(video);
    ctx.clearRect(0, 0, ctx.canvas.width, ctx.canvas.height);
    ctx.drawImage(video, 0, 0, ctx.canvas.width, ctx.canvas.height);
    drawPose(pose, ctx);

    let detectionResult;
    switch (currentExercise) {
        case 'squat':
            detectionResult = detectSquat(pose);
            break;
        case 'pushup':
            detectionResult = detectPushup(pose);
            break;
        case 'plank':
            detectionResult = detectPlank(pose);
            break;
        case 'pullup':
    detectionResult = detectPullup(pose);
    if (detectionResult.isCorrect && detectionResult.stage === 'up' && lastPullupStage === 'down') {
        updateCounter();
    }
    lastPullupStage = detectionResult.stage;
    break;
}

updateFeedback(currentExercise, detectionResult);

requestAnimationFrame(() => detectFrame(video, net, ctx));
}

function updateCounter() {
const repCountElement = document.getElementById('rep-count');
let repCount = parseInt(repCountElement.textContent);
repCount++;
repCountElement.textContent = repCount;
}

init();