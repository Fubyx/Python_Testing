import cv2
import numpy as np

# Define the lower and upper boundaries of the ball in the HSV color space
lower_ball = np.array([0, 0, 0])
upper_ball = np.array([100, 100, 100])

# Load the video capture device (i.e., the webcam)
cap = cv2.VideoCapture(0)

# Define the color and thickness of the circle around the ball
circle_color = (0, 0, 255) # red color
circle_thickness = 2

while True: # Capture a frame from the webcam
    ret, frame = cap.read()

    # Convert the frame to HSV color space
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Threshold the HSV image to get a binary image of the ball
    mask = cv2.inRange(hsv, lower_ball, upper_ball)

    # Apply opening and closing operations to remove noise and small objects
    opening = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
    closing = cv2.morphologyEx(opening, cv2.MORPH_CLOSE, np.ones((10, 10), np.uint8))

    # Find circles in the binary image
    circles = cv2.HoughCircles(closing, cv2.HOUGH_GRADIENT, 1, 20, param1=100, param2=50, minRadius=10, maxRadius=75)

    # If circles are detected, draw a red circle around the largest one
    if circles is not None:
        circles = np.round(circles[0, :]).astype("int")
        centers = circles[:, :2]
        radii = circles[:, 2]
        IDX = np.argsort(centers[:, 0])
        centers = centers[IDX, :]
        radii = radii[IDX]

        # Find the largest circle that is not too close to the edge
        for i, (x, y) in enumerate(centers[:2]):
            if (x - radii[i]) < 0 or (x + radii[i]) > frame.shape[1] or (y - radii[i]) < 0 or (y + radii[i]) > frame.shape[0]:
                continue

            cv2.circle(frame, (x, y), radii[i], circle_color, circle_thickness)

            # Break the loop after finding the first valid circle
            break

    # Display the resulting frame
    cv2.imshow("Frame", frame)

    # Exit the loop if the user presses the 'q' key
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the video capture device and destroy all windows
cap.release()
cv2.destroyAllWindows()