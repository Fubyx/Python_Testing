
import requests  # Import requests library
import cv2

# Server details (replace with your server's IP and port)
SERVER_IP = "127.0.0.1"
SERVER_PORT = 8080
SERVER_URL = f"http://{SERVER_IP}:{SERVER_PORT}/receive_frame"

def capture_and_send_frame():
    camera = cv2.VideoCapture(0)
    while True:
        try:
            ret, im = camera.read()

            imgencode = cv2.imencode(".jpg", cv2.cvtColor(im, cv2.COLOR_BGR2RGB))[1].tobytes()  # Compress as JPEG
            response = requests.post(SERVER_URL, files={'image': imgencode})
            response.raise_for_status()  # Raise exception on non-200 status codes
            print(f"Frame sent successfully. Status code: {response.status_code}")
        except Exception as e:
            print(f"Error capturing or sending frame: {e}")
            camera.release()  # Close camera on error
            break

if __name__ == "__main__":
    capture_and_send_frame()