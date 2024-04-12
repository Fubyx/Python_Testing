import cv2
import numpy as np

def detect_lines(frame):
  """
  Detects lines in a given image frame using the Hough Transform.

  Args:
      frame: The input image frame (BGR).

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
                         minLineLength=50, maxLineGap=30)

  # Extract starting and end points of detected lines
  detected_lines = []
  if lines is not None:
    for line in lines:
      x1, y1, x2, y2 = line[0]
      detected_lines.append((x1, y1, x2, y2))

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
