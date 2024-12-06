const videoElement = document.getElementById('videoElement');
const videoContainer = document.querySelector('.video-container');
const scannedValueDisplay = document.getElementById('scannedValue');
const filterForm = document.getElementById('filterForm');

let codeReader = null;
let stream = null;

document.getElementById('startScanButton').addEventListener('click', startScanning);
document.getElementById('stopScanButton').addEventListener('click', stopScanning);

async function startScanning() {
    videoContainer.style.display = 'block'; // Show video container
    toggleScanButtons();

    codeReader = new ZXing.BrowserMultiFormatReader();

    try {
        // Access the user's camera
        stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: "environment" } });
        videoElement.srcObject = stream; // Set video source
        videoElement.play(); // Start playing the video feed

        // Start decoding from the video feed
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
    filterForm.querySelector('[name="sku"]').value = scannedValue; // Populate the hidden input with scanned value
    filterForm.submit(); // Automatically submit the form
    stopScanning(); // Stop scanning after a successful scan
}

function stopScanning() {
    if (codeReader) {
        codeReader.reset(); // Stop the code reader
        codeReader = null;
    }
    if (stream) {
        stream.getTracks().forEach(track => track.stop()); // Stop the video stream
        stream = null;
    }
    videoContainer.style.display = 'none'; // Hide video container
    toggleScanButtons();
}

function toggleScanButtons() {
    document.getElementById('startScanButton').classList.toggle('d-none');
    document.getElementById('stopScanButton').classList.toggle('d-none');
}

