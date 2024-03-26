import cv2
import numpy as np
import time

# define the lower and upper boundaries of the color we want to detect
# in this example, we'll use the color blue
lower_blue = np.array([100, 50, 50])
upper_blue = np.array([130, 255, 255])

# initialize the camera
cap = cv2.VideoCapture(0)

# initialize the list of tracked points
pts = []

# set the initial position of the ball
x, y = None, None

# Define the color and thickness of the circle around the ball
circle_color = (0, 0, 255)  # red color
circle_thickness = 2

while True:
    # capture the frame from the camera
    ret, frame = cap.read()

    # convert the frame to HSV color space
    hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # create a mask for the color blue
    mask = cv2.inRange(hsv_frame, lower_blue, upper_blue)

    # find contours in the mask
    contours = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = contours[0] if len(contours) == 2 else contours[1]

    # if no contours were found, continue to the next iteration
    if not contours:
        continue

    # if multiple contours were found, select the largest one
    if len(contours) > 1:
        contour = max(contours, key=cv2.contourArea)
    else:
        contour = contours[0]

    # compute the center of the contour
    M = cv2.moments(contour)
    center = None
    if M["m00"] != 0:
        center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
    # if the center is not None, update the position of the ball
    if center is not None:
        x, y = center
        pts.append(center)
        # Calculate the radius of the circle
        r = int(cv2.arcLength(contour, True) / (2 * np.pi))


        # draw a green circle around the ball
        cv2.circle(frame, (x, y), r, circle_color, circle_thickness)

    # show the frame
    cv2.imshow("frame", frame)
    cv2.imshow("mask", mask)

    # exit the loop if the 'q' key is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# release the camera and destroy all windows
cap.release()
cv2.destroyAllWindows()