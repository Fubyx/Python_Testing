import picamera2
import requests  # Import requests library

# Server details (replace with your server's IP and port)
SERVER_IP = "192.168.1.100"
SERVER_PORT = 8080
SERVER_URL = f"http://{SERVER_IP}:{SERVER_PORT}/receive_frame"

def capture_and_send_frame():
    with picamera2.Picamera2() as camera:
        camera.start_preview()
        while True:
            try:
                im = camera.capture_array()
                imgencode = cv2.imencode(".jpg", im)[1].tobytes()  # Compress as JPEG
                response = requests.post(SERVER_URL, files={'image': imgencode})
                response.raise_for_status()  # Raise exception on non-200 status codes
                print(f"Frame sent successfully. Status code: {response.status_code}")
            except Exception as e:
                print(f"Error capturing or sending frame: {e}")
                camera.close()  # Close camera on error
                break

if __name__ == "__main__":
    capture_and_send_frame()