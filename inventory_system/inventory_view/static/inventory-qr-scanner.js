const videoElement = document.getElementById('videoElement');
const scannedValueDisplay = document.getElementById('scannedValue');
const filterForm = document.getElementById('filterForm');
const videoContainer = document.querySelector('.video-container');

let codeReader = null;
let stream = null;

document.getElementById('startScanButton').addEventListener('click', startScanning);
document.getElementById('stopScanButton').addEventListener('click', stopScanning);

async function startScanning() {
    videoContainer.style.display = 'block'; // Show video container
    toggleScanButtons();

    // Initialize the ZXing code reader
    codeReader = new ZXing.BrowserMultiFormatReader();

    try {
        stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: "environment" } });
        videoElement.srcObject = stream;
        videoElement.play();

        // Start decoding from video stream
        codeReader.decodeFromVideoDevice(null, videoElement, (result, error) => {
            if (result) {
                handleScannedValue(result.text);
            }
            if (error && error.message !== "No MultiFormat Readers were able to detect the code.") {
                console.error("ZXing error:", error);
            }
        });
    } catch (error) {
        console.error("Error accessing webcam:", error);
        document.getElementById('videoError').style.display = 'block'; // Show error message
    }
}

function handleScannedValue(scannedValue) {
    scannedValueDisplay.textContent = `Scanned Value: ${scannedValue}`;
    filterForm.querySelector('[name="sku"]').value = scannedValue; // Populate input with lowercase 'sku'
    filterForm.submit(); // Submit the form
    stopScanning(); // Stop scanning after successful scan
}

function stopScanning() {
    if (codeReader) {
        codeReader.reset(); // Stop ZXing
        codeReader = null;
    }
    if (stream) {
        stream.getTracks().forEach(track => track.stop());
        stream = null;
    }
    videoContainer.style.display = 'none'; // Hide video container
    toggleScanButtons();
}

function toggleScanButtons() {
    document.getElementById('startScanButton').classList.toggle('d-none');
    document.getElementById('stopScanButton').classList.toggle('d-none');
}
