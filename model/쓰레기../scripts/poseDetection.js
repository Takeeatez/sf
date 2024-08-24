let net;

export async function setupCamera() {
    const video = document.getElementById('video');
    const stream = await navigator.mediaDevices.getUserMedia({video: true});
    video.srcObject = stream;
    return new Promise((resolve) => {
        video.onloadedmetadata = () => {
            resolve(video);
        };
    });
}

export async function initializePoseNet() {
    net = await posenet.load({
        architecture: 'MobileNetV1',
        outputStride: 16,
        inputResolution: { width: 640, height: 480 },
        multiplier: 0.75
    });
    return net;
}

export async function detectPose(video) {
    const pose = await net.estimateSinglePose(video, {
        flipHorizontal: true
    });
    return pose;
}

export function drawPose(pose, ctx) {
    if (pose.score >= 0.1) {
        pose.keypoints.forEach((keypoint) => {
            if (keypoint.score > 0.5) {
                ctx.beginPath();
                ctx.arc(keypoint.position.x, keypoint.position.y, 5, 0, 2 * Math.PI);
                ctx.fillStyle = 'red';
                ctx.fill();
            }
        });
    }
}