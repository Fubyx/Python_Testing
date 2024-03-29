

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

    # Extrahiere die Linienparameter der Peaks
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


    # Extrahiere die Eckpunkte der Rechtecke aus den Linien
    rectangles = []
    for i in range(len(lines)):
        for j in range(i + 1, len(lines)):
            x1 = lines[i][0]
            y1 = lines[i][1]
            x2 = lines[i][2]
            y2 = lines[i][3]
            
            x3 = lines[j][0]
            y3 = lines[j][1]
            x4 = lines[j][2]
            y4 = lines[j][3]
            
            area = abs((x1 - x2) * (y3 - y4)) - abs((x3 - x4) * (y1 - y2))
            
            # Überprüfen, ob die Linien ein Rechteck bilden
            if area < 1000:
                rectangles.append((x1, y1, x2, y2, x3, y3, x4, y4))
    valid_rectangles = []
    #"""
    # Filterung der Rechtecke basierend auf der Konsistenz
    for line1 in lines:
        for line2 in lines:
            if line1 == line2:
                continue

            #schnittpunkte Suchen und dann theoretisch nur Linien, zu denen Zeichnen
            intersection_point = find_intersection(line1, line2)
            if intersection_point is not None:
                x1, y1, x2, y2 = line1
                x3, y3, x4, y4 = line2
                rectangle = (x1, y1, x2, y2, x3, y3, x4, y4)
                if rectangle not in tracked_rectangles:
                    tracked_rectangles.add(rectangle)
                    consecutive_frames[rectangle] = 0  # Set consecutive frames count to 0
                else:
                    consecutive_frames[rectangle] += 1
                    if consecutive_frames[rectangle] >= min_consecutive_frames:
                        valid_rectangles.append(rectangle)
                        break
                

    
    # Zeichnen der konsistenten Rechtecke auf das Bild
    for rectangle in rectangles:
        x1, y1, x2, y2, x3, y3, x4, y4 = rectangle
        intersection_points = []
        for line1 in lines:
            for line2 in lines:
                if line1 == line2:
                    continue
                intersection_point = find_intersection(line1, line2)
                if intersection_point is not None:
                    intersection_points.append(intersection_point)
        
        # Draw lines to intersection points
        for point in intersection_points:
            cv2.line(frame, (x1, y1), point, (0, 255, 0), 2)
            cv2.line(frame, (x2, y2), point, (0, 255, 0), 2)
            cv2.line(frame, (x3, y3), point, (0, 255, 0), 2)
            cv2.line(frame, (x4, y4), point, (0, 255, 0), 2)



    cv2.imshow("Frame", frame)
    
    # Exit the loop if the user presses 'q' key
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the video capture device and destroy all windows
cap.release()
cv2.destroyAllWindows()

