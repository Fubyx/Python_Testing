import cv2
import numpy as np

cap = cv2.VideoCapture(0)

circle_color = (0, 0, 255)  # red color
circle_thickness = 2

min_area = 1  # Adjust the minimum area for the ball
min_circularity = 0.4  # Adjust the minimum circularity for the ball

while True:
    ret, frame = cap.read()

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    # Find contours in the blurred frame
    contours, _ = cv2.findContours(blurred, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if contours:
        # Find the ball among the contours
        ball_contours = [cnt for cnt in contours if cv2.contourArea(cnt) >= min_area]

        for contour in ball_contours:
            if(cv2.contourArea(contour) > 1000):
                continue
            print(cv2.contourArea(contour))
            # Calculate circularity
            (x, y), radius = cv2.minEnclosingCircle(contour)
            circle_circularity = (4 * np.pi * np.power(radius, 2)) / (np.power(cv2.arcLength(contour, True), 2))
            if circle_circularity >= min_circularity:
                cv2.circle(frame, (int(x), int(y)), int(radius), circle_color, circle_thickness)

    cv2.imshow("Frame", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()