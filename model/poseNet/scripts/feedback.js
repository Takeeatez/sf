let repCount = 0;
let isInCorrectPosition = false;

export function updateFeedback(exercise, detectionResult) {
    const feedbackElement = document.getElementById('feedback');
    const repCountElement = document.getElementById('rep-count');

    if (detectionResult.isCorrect) {
        feedbackElement.textContent = "자세가 정확합니다!";
        if (!isInCorrectPosition) {
            isInCorrectPosition = true;
        }
    } else {
        feedbackElement.textContent = detectionResult.feedback.join(" ");
        if (isInCorrectPosition) {
            repCount++;
            repCountElement.textContent = repCount;
            isInCorrectPosition = false;
        }
    }
}

export function resetCounter() {
    repCount = 0;
    isInCorrectPosition = false;
    document.getElementById('rep-count').textContent = repCount;
}

export function getRepCount() {
    return repCount;
}