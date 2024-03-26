import cv2
import numpy as np

# Load the video capture device (i.e., the webcam)
cap = cv2.VideoCapture(0)

# Define the color and thickness of the circle around the ball
circle_color = (0, 0, 255)  # red color
circle_thickness = 2

# Define the minimum and maximum area thresholds for contours (adjust as needed)
min_contour_area = 1000
max_contour_area = 10000  # set a maximum area threshold

while True:  # Capture a frame from the webcam
    ret, frame = cap.read()

    # Convert the frame to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Apply Gaussian blur to the grayscale frame to reduce noise
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    # Detect contours in the blurred frame
    contours, _ = cv2.findContours(blurred, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # If contours are detected, draw a red circle around the largest one
    if contours:
        # Find the largest contour by area
        largest_contour = max(contours, key=cv2.contourArea)

        # Check if the largest contour is within the maximum area threshold
        if cv2.contourArea(largest_contour) > min_contour_area and cv2.contourArea(largest_contour) < max_contour_area:
            # Calculate the center of the largest contour
            moments = cv2.moments(largest_contour)
            center_x = int(moments['m10'] / moments['m00'])
            center_y = int(moments['m01'] / moments['m00'])

            # Calculate the radius of the largest contour
            radius = int(np.max(largest_contour.reshape(-1, 2)) / 2)

            # Draw a circle around the largest contour
            cv2.circle(frame, (center_x, center_y), radius, circle_color, circle_thickness)

    # Display the resulting frame
    cv2.imshow("Frame", frame)

    # Exit the loop if the user presses the 'q' key
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the video capture device and destroy all windows
cap.release()
cv2.destroyAllWindows()