import cv2
import numpy as np

def line_distance(line1, line2):
    """
    Calculates the distance between two lines based on their starting points.

    Args:
        line1: A tuple representing the first line with its starting and ending points (x1, y1, x2, y2).
        line2: A tuple representing the second line with its starting and ending points (x1, y1, x2, y2).

    Returns:
        The distance between the two lines based on their starting points.
    """
    x1_1, y1_1, _, _ = line1
    x1_2, y1_2, _, _ = line2
    return abs(x1_1 - x1_2) + abs(y1_1 - y1_2)

def detect_lines(frame, min_distance=20):
    """
    Detects lines in a given image frame using the Hough Transform.

    Args:
        frame: The input image frame (BGR).
        min_distance: Minimum distance threshold between two parallel lines.

    Returns:
        A list of tuples, where each tuple represents a line with its starting
        and ending points (x1, y1, x2, y2).
    """

    # Convert the frame to grayscale for better edge detection
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Apply edge detection using the Canny edge detector
    edges = cv2.Canny(gray, 50, 150, apertureSize=3)

    # Apply the Hough Transform to detect lines
    lines = cv2.HoughLinesP(edges, rho=1, theta=np.pi/180, threshold=100,
                            minLineLength=0, maxLineGap=30)

    # Extract starting and end points of detected lines
    detected_lines = []
    if lines is not None:
        # Sort the lines based on their slope
        lines = sorted(lines, key=lambda line: np.arctan2(line[0][3] - line[0][1], line[0][2] - line[0][0]))

        prev_line = None
        for line in lines:
            if prev_line is None or line_distance(prev_line, line[0]) > min_distance:
                detected_lines.append((line[0][0], line[0][1], line[0][2], line[0][3]))
                prev_line = line[0]

    return detected_lines

# Capture video from camera (modify index for multiple cameras)
cap = cv2.VideoCapture(0)

while True:
    # Capture frame-by-frame
    ret, frame = cap.read()

    # Detect lines in the frame
    lines = detect_lines(frame)

    # Draw detected lines on the frame (optional)
    if lines:
        for x1, y1, x2, y2 in lines:
            cv2.line(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

    # Display the frame with detected lines (or original frame)
    cv2.imshow('Frame', frame)

    # Exit on 'q' press
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the capture and close all windows
cap.release()
cv2.destroyAllWindows()
