import cv2

class QRCodeScanner:
    def __init__(self):
        self.cap = cv2.VideoCapture(0)
        self.detector = cv2.QRCodeDetector()
        self.data = None

    def start_scanning(self):
        while True:
            ret, img = self.cap.read()
            if not ret:
                print("Failed to grab frame.")
                break

            self.data, _, _ = self.detector.detectAndDecode(img)
            if self.data:
                break

            cv2.imshow('QR Scanner', img)
            if cv2.waitKey(1) == ord('q'):
                break

    def get_scanned_data(self):
        return self.data

    def display_result(self):
        if self.data:
            print('=================================')
            print(self.data)
            print('=================================')
        else:
            print("No QR code detected.")

    def release_resources(self):
        self.cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    scanner = QRCodeScanner()
    try:
        scanner.start_scanning()
        scanned_value = scanner.get_scanned_data()
        scanner.display_result()
    finally:
        scanner.release_resources()