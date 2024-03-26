import cv2
import numpy as np

# Define circle detection parameters
circle_color = (0, 0, 255)
circle_thickness = 2
min_radius = 10
max_radius = 75

cap = cv2.VideoCapture(0)

while True:
    # Capture a frame from the webcam
    ret, frame = cap.read()

    # Convert the frame to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Apply Otsu's thresholding to separate foreground (ball) from background
    thresh, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # Detect circles using Hough transform
    circles = cv2.HoughCircles(binary, cv2.HOUGH_GRADIENT, 1, 50,
                               param1=90, param2=30, minRadius=min_radius, maxRadius=max_radius)

    # Draw detected circles
    if circles is not None:
        circles = np.round(circles[0, :]).astype("int")
        for (x, y, r) in circles:
            cv2.circle(frame, (x, y), r, circle_color, circle_thickness)

    # Display the resulting frame
    cv2.imshow("Frame", frame)

    # Exit the loop if the user presses 'q' key
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the video capture device and destroy all windows
cap.release()
cv2.destroyAllWindows()
