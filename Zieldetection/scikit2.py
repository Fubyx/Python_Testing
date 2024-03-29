#Rechteck kann erkannt werden, aber linien gehen über den Rand

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

# Define thresholds
min_consecutive_frames = 3  # Minimum frames to consider a rectangle initially
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
    for rectangle in rectangles:
        # Überprüfen, ob das Rechteck konsistent ist
        if rectangle not in tracked_rectangles:
            # Wenn das Rechteck noch nicht verfolgt wird, fügen Sie es der Verfolgungsliste hinzu
            tracked_rectangles.add(rectangle)
            consecutive_frames[rectangle] = 0  # Setze die Anzahl der aufeinanderfolgenden Frames auf 0
        else:
            # Wenn das Rechteck bereits verfolgt wird, erhöhe die Anzahl der aufeinanderfolgenden Frames
            consecutive_frames[rectangle] += 1
            if consecutive_frames[rectangle] >= min_consecutive_frames:
                # Wenn das Rechteck als konsistent betrachtet wird, speichern Sie es und brechen Sie die Schleife ab
                valid_rectangles.append(rectangle)
                break
                

    
    # Zeichnen der konsistenten Rechtecke auf das Bild
    for rectangle in rectangles:
        if rectangle not in valid_rectangles:
            # Wenn das Rechteck nicht konsistent ist, fahre mit dem nächsten Rechteck fort
            print("Not COnsistent")
            continue
        print("Consistent!!!!!!!!!!!!!!!!!")
        #paint rectangle
        
        x1, y1, x2, y2, x3, y3, x4, y4 = rectangle
        cv2.line(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.line(frame, (x2, y2), (x3, y3), (0, 255, 0), 2)
        cv2.line(frame, (x3, y3), (x4, y4), (0, 255, 0), 2)
        cv2.line(frame, (x4, y4), (x1, y1), (0, 255, 0), 2)
        #for i in range(0, len(rectangle), 2):
        #    cv2.line(frame, (rectangle[i], rectangle[i+1]), (rectangle[(i+2)%8], rectangle[(i+3)%8]), (0, 255, 0), 2)



    cv2.imshow("Frame", frame)
    
    # Exit the loop if the user presses 'q' key
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the video capture device and destroy all windows
cap.release()
cv2.destroyAllWindows()
