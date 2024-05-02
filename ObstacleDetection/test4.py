import cv2
import numpy as np

def distance(point1, point2):
  """
  Calculates the Euclidean distance between two points.

  Args:
      point1: A tuple representing a point (x, y).
      point2: A tuple representing another point (x, y).

  Returns:
      The Euclidean distance between the two points.
  """
  x1, y1 = point1
  x2, y2 = point2
  return np.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

def is_parallel(line1, line2, tolerance=5):
  """
  Checks if two lines are approximately parallel.

  Args:
      line1: A tuple representing a line (x1, y1, x2, y2).
      line2: A tuple representing another line (x1, y1, x2, y2).
      tolerance: The maximum allowed angle difference for considering lines parallel (in degrees).

  Returns:
      True if the lines are approximately parallel, False otherwise.
  """
  x11, y11, x12, y12 = line1
  x21, y21, x22, y22 = line2
  slope1 = (y12 - y11) / (x12 - x11) if x12 != x11 else float('inf')
  slope2 = (y22 - y21) / (x22 - x21) if x22 != x21 else float('inf')
  angle_diff = abs(np.arctan2(slope2, slope1) - np.arctan2(slope1, slope2)) * 180 / np.pi
  return angle_diff <= tolerance

def merge_lines(line1, line2):
  """
  Merges two parallel and close lines into a single line.

  Args:
      line1: A tuple representing a line (x1, y1, x2, y2).
      line2: A tuple representing another line (x1, y2).

  Returns:
      A tuple representing the merged line (x1, y1, x2, y2).
  """
  x11, y11, x12, y12 = line1
  x21, y21, x22, y22 = line2
  x_mid = (x11 + x12 + x21 + x22) / 4
  y_mid = (y11 + y12 + y21 + y22) / 4
  length = np.sqrt((x12 - x11) ** 2 + (y12 - y11) ** 2)
  return (int(x_mid), int(y_mid), int(x_mid + length * np.cos(np.arctan2(y12 - y11, x12 - x11))), int(y_mid + length * np.sin(np.arctan2(y12 - y11, x12 - x11))))

def detect_lines(frame, min_distance=10, max_angle_diff=5):
  """
  Detects lines in a given image frame using the Hough Transform and merges parallel lines.

  Args:
      frame: The input image frame (BGR).
      min_distance: The minimum allowed distance between two lines (default 10 pixels).
      max_angle_diff: The maximum allowed angle difference for considering lines parallel (in degrees).

  Returns:
      A list of tuples, where each tuple represents a line with its starting
      and ending points (x1, y1, x2, y2).
  """

  # Convert the frame to grayscale for better edge detection
  gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

  # Apply edge detection using the Canny edge detector
  edges = cv2.Canny(gray, 50, 150, apertureSize=3)
  cv2.imshow("Canny", edges)

  # Apply the Hough Transform to detect lines
  lines = cv2.HoughLinesP(edges, rho=1, theta=np.pi/180, threshold=100,
                         minLineLength=50, maxLineGap=30)

  # Extract starting and end points of detected lines
  merged_lines = []
  if lines is not None:
    for i in range(len(lines)):
      line1 = lines[i]
      is_merged = False
      for j in range(i + 1, len(lines)):
        line2 = lines[j]
        # Check distance and parallelism
        if distance(line1[0], line2[0]) < min_distance and is_parallel(line1, line2, max_angle_diff):
          # Merge lines if close and parallel
          merged_line = merge_lines(line1, line2)
          merged_lines.append(merged_line)
          is_merged = True
          # Remove line2 from original list to avoid processing it again
          lines.pop(j)
          break
      # If not merged, add the line to the merged list
      if not is_merged:
        merged_lines.append(line1[0])

  return merged_lines

# ... rest of the code for capturing video and drawing lines ...^

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

