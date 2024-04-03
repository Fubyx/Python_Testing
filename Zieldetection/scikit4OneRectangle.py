#findet ein rectangle -> zeichnet diese auf Basis der Schnittpunkte
#also relativ gut, das Rechteck wird aber nur das Größte gezeichnet
#wenn mehrere sind, kann dies zu Probleme führen
#daher besser auf die Intersectionpunkte schauen

import cv2
import numpy as np
import matplotlib.pyplot as plt
from skimage.draw import rectangle_perimeter
from skimage.transform import hough_line, hough_line_peaks

# Generiere ein Testbild mit einem Rechteck
"""image = np.zeros((100, 100), dtype=np.uint8)
top_left = (5, 25)
bottom_right = (75, 75)
rr, cc = rectangle_perimeter(top_left, bottom_right)
image[rr, cc] = 100
"""

#find Intersection between lines
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


# Define thresholds
min_consecutive_frames = 6  # Minimum frames to consider a rectangle initially
max_missed_frames = 0  # Maximum allowed missed frames before discarding a circle

# Initialize variables for tracking
consecutive_frames = {}  # Dictionary to store frame counts and missed frames
tracked_rectangles = set()  # Set to store lines currently being tracked

# Load the video capture device (i.e., the webcam)
cap = cv2.VideoCapture(0)
while True:
    # Capture a frame from the webcam
    ret, frame = cap.read()
    if frame is not None:
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    """
    ksize = 3
    gX = cv2.Sobel(gray, ddepth=cv2.CV_32F, dx=1, dy=0, ksize=ksize)
    gY = cv2.Sobel(gray, ddepth=cv2.CV_32F, dx=0, dy=1, ksize=ksize)
    # the gradient magnitude images are now of the floating point data
    # type, so we need to take care to convert them back a to unsigned
    # 8-bit integer representation so other OpenCV functions can operate
    # on them and visualize them
    gX = cv2.convertScaleAbs(gX)
    gY = cv2.convertScaleAbs(gY)
    # combine the gradient representations into a single image
    edges = cv2.addWeighted(gX, 0.5, gY, 0.5, 0)
    """

    # Kantenerkennung mit Canny
    edges = cv2.Canny(gray, 50, 150, apertureSize=3)
    
    #"""
    cv2.imshow("Edges", edges)


    # Führe die Hough-Transformation für Linien durch
    h, theta, d = hough_line(edges)

    # Finde die Peaks in der Hough-Transformierten
    peaks = hough_line_peaks(h, theta, d, min_distance = 100)

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
    
    # Find the minimum and maximum coordinates to determine the bounding rectangle
    if len(intersection_points) > 0:
        # Filter intersection points outside the frame
        intersection_points = intersection_points[(intersection_points[:, 0] >= 0) & (intersection_points[:, 0] < frame.shape[1]) &
                                                  (intersection_points[:, 1] >= 0) & (intersection_points[:, 1] < frame.shape[0])]
        
        if len(intersection_points) > 0:
            min_x = np.min(intersection_points[:, 0])
            max_x = np.max(intersection_points[:, 0])
            min_y = np.min(intersection_points[:, 1])
            max_y = np.max(intersection_points[:, 1])

            # Draw the rectangle
            cv2.rectangle(frame, (min_x, min_y), (max_x, max_y), (0, 255, 0), 2)



    cv2.imshow("Frame", frame)
    
    # Exit the loop if the user presses 'q' key
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the video capture device and destroy all windows
cap.release()
cv2.destroyAllWindows()

