import cv2
import numpy as np

# Load the image
image = cv2.imread('SlopeDetection/ramp2.jpg')

# Convert the image to grayscale
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# Apply Canny edge detection
edges = cv2.Canny(gray, 0, 300)
print(edges)

# Use Hough line transform to detect lines
lines = cv2.HoughLines(edges, 1, np.pi/180, 200)

# Initialize slope variable
slope = None

# Iterate over the lines and calculate slope
for line in lines:
    rho, theta = line[0]
    a = np.cos(theta)
    b = np.sin(theta)
    x0 = a*rho
    y0 = b*rho
    x1 = int(x0 + 1000*(-b))
    y1 = int(y0 + 1000*(a))
    x2 = int(x0 - 1000*(-b))
    y2 = int(y0 - 1000*(a))

    # Calculate slope
    if a != 0:
        slope = (y2 - y1) / (x2 - x1)

    # Check if slope is within a certain range
    if slope is not None and slope > 0.1 and slope < 50:
        print("There is a slope in the image")
        break
else:
    print("There is no slope in the image")