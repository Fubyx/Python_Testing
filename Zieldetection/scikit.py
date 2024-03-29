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


# Load the video capture device (i.e., the webcam)
cap = cv2.VideoCapture(0)
while True:
    # Capture a frame from the webcam
    ret, frame = cap.read()
    if frame is not None:
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        cv2.imshow("Gray", gray)
    
    edges = cv2.Canny(gray, 50, 150, apertureSize=3)


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
        x1 = int(x0 + 100 * (-b))
        y1 = int(y0 + 100 * (a))
        x2 = int(x0 - 100 * (-b))
        y2 = int(y0 - 100 * (a))
        lines.append((x1, y1, x2, y2))

    # Extrahiere die Eckpunkte des Rechtecks aus den Linien
    if lines:
        min_x = min(line[0] for line in lines)
        max_x = max(line[0] for line in lines)
        min_y = min(line[1] for line in lines)
        max_y = max(line[1] for line in lines)

    # Zeige das Originalbild und das detektierte Rechteck
    #fig, ax = plt.subplots()
    #ax.imshow(image, cmap=plt.cm.gray)
    for line in lines:
        #ax.plot((line[0], line[2]), (line[1], line[3]), '-r')
        cv2.rectangle(frame, (line[0], line[2]), (line[1], line[3]), (0, 255, 0), 2)
    #ax.plot((min_x, max_x), (min_y, max_y), '-g')
    #ax.set_title('Detected rectangle')
    #ax.axis((0, 100, 100, 0))


    cv2.imshow("Frame", frame)
    
    # Exit the loop if the user presses 'q' key
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the video capture device and destroy all windows
cap.release()
cv2.destroyAllWindows()