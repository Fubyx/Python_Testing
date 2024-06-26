import cv2
import numpy as np

# Load the video capture device (i.e., the webcam)
cap = cv2.VideoCapture(0)

# Define the color and thickness of the circle around the ball
circle_color = (0, 0, 255)  # red color
circle_thickness = 2

# Define thresholds
color_threshold = 15  # Maximum allowable difference in BGR values
min_consecutive_frames = 6  # Minimum frames to consider a circle initially
max_missed_frames = 0  # Maximum allowed missed frames before discarding a circle

# Initialize variables for tracking
consecutive_frames = {}  # Dictionary to store frame counts and missed frames
tracked_circles = set()  # Set to store circles currently being tracked
y_starting_point = cap.get(4)/3 # Starting point to filter circles in the top third of the image
while True:
    # Capture a frame from the webcam
    ret, frame = cap.read()

    # Convert frame to grayscale for adaptive thresholding (temporary)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Apply adaptive thresholding
    thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 51, 2)

    # Apply Gaussian blur on the thresholded image
    blurred = cv2.GaussianBlur(thresh, (5, 5), 0)

    # Detect circles using Hough transform on the blurred thresholded image
    circles = cv2.HoughCircles(blurred, cv2.HOUGH_GRADIENT, 1, 50, param1=90, param2=30, minRadius=0, maxRadius=75)
  
    """
    #If circles are detected, draw a red circle around the largest one 
    if circles is not None:
        circles = np.round(circles[0, :]).astype("int")
        for (x, y, r) in circles:
            if r > 10: # ignore small circles that are not likely to be a ball
                # Draw the circle on the frame
                cv2.circle(frame, (x, y), r, circle_color, circle_thickness)
    """
    # Update tracking information (pre-color check)
    if circles is not None:
        circles = np.round(circles[0, :]).astype("int")
        for (x, y, r) in circles:
            if (r > 10) & (y > y_starting_point):  # Ignore small circles and circles below the starting point
                circle_key = (x, y, r)

                # Check if circle is newly detected or already tracked
                if circle_key not in tracked_circles:
                    consecutive_frames[circle_key] = 1
                    tracked_circles.add(circle_key)
                else:
                    consecutive_frames[circle_key] = min(consecutive_frames[circle_key] + 1, min_consecutive_frames)

    # Filter circles based on consecutive detection and missed frames
    valid_circles = []
    for circle_key in tracked_circles.copy():
        # Check if circle has been consistently detected or missed too many frames
        if consecutive_frames.get(circle_key, 0) >= min_consecutive_frames or \
                consecutive_frames.get(circle_key, 0) <= 0:
            tracked_circles.remove(circle_key)
            consecutive_frames.pop(circle_key, None)
        else:
            consecutive_frames[circle_key] -= 1  # Decrement missed frames counter
            valid_circles.append(circle_key)  # Unpack circle info

    # Apply color consistency check only to valid circles
    if valid_circles:
        for (x, y, r) in valid_circles:
            # Create a mask for the circle area
            mask = np.zeros_like(frame[:, :, 0], dtype="uint8")
            cv2.circle(mask, (x, y), r, 255, -1)

            # Apply the mask to extract color information within the circle
            masked_frame = cv2.bitwise_and(frame, frame, mask=mask)

            # Check color consistency using standard deviation
            color_variance = np.std(masked_frame.reshape(-1, 3), axis=0)
            if np.all(color_variance < color_threshold):
                # Draw the circle if color is consistent
                cv2.circle(frame, (x, y), r, circle_color, circle_thickness)
                #print(y)

    #"""
    frame = thresh
    # Display the resulting frame
    cv2.imshow("Frame", frame)

    # Exit the loop if the user presses 'q' key
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the video capture device and destroy all windows
cap.release()
cv2.destroyAllWindows()
