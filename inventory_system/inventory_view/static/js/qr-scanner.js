const videoElement = document.getElementById('videoElement');
const scannedValueDisplay = document.getElementById('scannedValue');
const filterForm = document.getElementById('filterForm');
const videoContainer = document.querySelector('.video-container');
const canvas = document.createElement('canvas');
const context = canvas.getContext('2d');
let scanningInterval;

document.getElementById('startScanButton').addEventListener('click', startScanning);
document.getElementById('stopScanButton').addEventListener('click', stopScanning);

async function startScanning() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: "environment" } });
        videoElement.srcObject = stream;
        videoContainer.style.display = 'block'; // Show video container
        videoElement.play();
        scanningInterval = setInterval(scanQRCode, 500);
        toggleScanButtons();
    } catch (error) {
        console.error("Error accessing webcam: ", error);
        document.getElementById('videoError').style.display = 'block'; // Show error message
    }
}

function scanQRCode() {
    if (videoElement.videoWidth > 0 && videoElement.videoHeight > 0) {
        canvas.width = videoElement.videoWidth;
        canvas.height = videoElement.videoHeight;
        context.drawImage(videoElement, 0, 0, canvas.width, canvas.height);
        const imageData = context.getImageData(0, 0, canvas.width, canvas.height);
        const code = jsQR(imageData.data, canvas.width, canvas.height);

        if (code) {
            handleScannedValue(code.data);
        } else {
            scannedValueDisplay.textContent = 'No QR code detected. Try again.';
        }
    }
}

function handleScannedValue(scannedValue) {
    scannedValueDisplay.textContent = `Scanned Value: ${scannedValue}`;
    filterForm.querySelector('[sku="sku"]').value = scannedValue; // Populate input
    filterForm.submit(); // Submit the form
    stopScanning(); // Stop scanning after successful scan
}

function stopScanning() {
    clearInterval(scanningInterval);
    videoContainer.style.display = 'none'; // Hide video container
    toggleScanButtons();
    if (videoElement.srcObject) {
        videoElement.srcObject.getTracks().forEach(track => track.stop());
    }
}

function toggleScanButtons() {
    document.getElementById('startScanButton').classList.toggle('d-none');
    document.getElementById('stopScanButton').classList.toggle('d-none');
}
