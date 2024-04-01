#zeichnet die intersectionpunkte auf, aber kein Rechteck

import cv2
import numpy as np
from skimage.transform import hough_line, hough_line_peaks

def find_intersection(line1, line2):
    x1, y1, x2, y2 = line1
    x3, y3, x4, y4 = line2
    
    # Calculate slopes (m) and intercepts (c) of the lines
    m1 = (y2 - y1) / (x2 - x1) if (x2 - x1) != 0 else float('inf')
    c1 = y1 - m1 * x1
    m2 = (y4 - y3) / (x4 - x3) if (x4 - x3) != 0 else float('inf')
    c2 = y3 - m2 * x3
    
    # Check if the lines are parallel
    if m1 == m2:
        return None
    
    # Calculate intersection point
    if m1 == float('inf'):
        x = x1
        y = m2 * x + c2
    elif m2 == float('inf'):
        x = x3
        y = m1 * x + c1
    else:
        x = (c2 - c1) / (m1 - m2)
        y = m1 * x + c1
    
    # Check if intersection point is within line segments
    if (x1 <= x <= x2 or x2 <= x <= x1) and (y1 <= y <= y2 or y2 <= y <= y1) \
            and (x3 <= x <= x4 or x4 <= x <= x3) and (y3 <= y <= y4 or y4 <= y <= y3):
        return (int(x), int(y))
    else:
        return None



# Load the video capture device (i.e., the webcam)
cap = cv2.VideoCapture(0)
while True:
    # Capture a frame from the webcam
    ret, frame = cap.read()
    if not ret:
        break
    
    # Convert the frame to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # Perform edge detection using Canny
    edges = cv2.Canny(gray, 50, 150, apertureSize=3)
    cv2.imshow("canny", edges)

    # Perform Hough line detection
    h, theta, d = hough_line(edges)

    # Find peaks in Hough transform
    peaks = hough_line_peaks(h, theta, d, min_distance=100)

    # Extract lines from peaks
    lines = []
    for _, angle, dist in zip(*peaks):
        a = np.cos(angle)
        b = np.sin(angle)
        x0 = a * dist
        y0 = b * dist
        x1 = int(x0 + 1000 * (-b))
        y1 = int(y0 + 1000 * (a))
        x2 = int(x0 - 1000 * (-b))
        y2 = int(y0 - 1000 * (a))
        lines.append((x1, y1, x2, y2))

    # Find intersection points of all line pairs
    intersection_points = []
    for i, line1 in enumerate(lines):
        for line2 in lines[i+1:]:
            intersection_point = find_intersection(line1, line2)    
            if intersection_point is not None:
                intersection_points.append(intersection_point)
    
    # Convert intersection points to NumPy array
    intersection_points = np.array(intersection_points)

    
    # Draw intersection points
    for point in intersection_points:
        cv2.circle(frame, (point[0], point[1]), 5, (0, 0, 255), -1)
    # Draw lines between each pair of intersection points
    for i in range(len(intersection_points) - 1):
        cv2.line(frame, (intersection_points[i][0], intersection_points[i][1]), 
                 (intersection_points[i+1][0], intersection_points[i+1][1]), (0, 255, 0), 2)


    # Display the frame
    cv2.imshow("Frame", frame)
    
    # Exit the loop if the user presses the 'q' key
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the video capture device and close all windows
cap.release()
cv2.destroyAllWindows()
