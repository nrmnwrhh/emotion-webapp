const video = document.getElementById('video');
const canvas = document.getElementById('canvas');
const result = document.getElementById('result');
const context = canvas.getContext('2d');

async function startCamera() {
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        result.innerText = "❌ Your browser does not support webcam access.";
        return;
    }

    try {
        const stream = await navigator.mediaDevices.getUserMedia({ video: true });
        video.srcObject = stream;
    } catch (err) {
        result.innerText = "❌ Camera access blocked or unavailable: " + err.message;
        console.error("Camera error:", err);
    }
}

function capture() {
    context.drawImage(video, 0, 0, canvas.width, canvas.height);
    const imageData = canvas.toDataURL('image/png');

    fetch('/submit', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: `image=${encodeURIComponent(imageData)}`
    })
    .then(res => res.json())
    .then(data => {
        if (data.error) {
            result.innerText = "❌ " + data.error;
        } else {
            result.innerText = `✅ Emotion: ${data.emotion}, Rating: ${data.rating}⭐`;
        }
    })
    .catch(error => {
        result.innerText = "❌ Failed to send image.";
        console.error("Submit error:", error);
    });
}

window.onload = startCamera;
