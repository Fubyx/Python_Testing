import cv2
import numpy as np

def enhance_blue(image):
  # Convert image to HSV color space
  hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

  # Define lower and upper bounds for blue color in HSV (adjust if needed)
  lower_blue = np.array([90, 50, 50])
  upper_blue = np.array([140, 255, 255])

  # Create a mask to identify blue pixels
  mask = cv2.inRange(hsv, lower_blue, upper_blue)

  # Increase the 'Value' channel for blue pixels
  hsv[:,:,2] = cv2.addWeighted(hsv[:,:,2], 0.7, mask, 0.3, 0)  # Adjust weights for intensity increase

  # Convert back to BGR color space
  enhanced_image = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)

  return enhanced_image

# Capture video from webcam
cap = cv2.VideoCapture(0)

# Define saturation adjustment factor
saturation_factor = 1.5

while True:
  # Read a frame from the webcam
  ret, frame = cap.read()

  # Check if frame is read correctly
  if not ret:
    print("Error! Unable to capture frame")
    break
  #frame2 = enhance_blue(frame)
  b, g, r = cv2.split(frame)
  r = np.where(True, 255, r)
  g = np.where(True, 0, g)
  b = np.where(True, 125, b)
  red = cv2.merge((b,g,r))

  adjusted_frame = cv2.add(frame, red)
  # Display the original and adjusted frame
  cv2.imshow('Original Frame', frame)
  cv2.imshow('Adjusted Frame', adjusted_frame)
  gray = cv2.cvtColor(adjusted_frame, cv2.COLOR_BGR2GRAY)
  cv2.imshow('Gray from adjusted', gray)
  gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
  #gray = cv2.convertScaleAbs(gray, alpha=1.0, beta=-30)
  cv2.imshow('Gray from frame', gray)

  # Exit on 'q' key press
  if cv2.waitKey(1) == ord('q'):
    break

# Release capture and close windows
cap.release()
cv2.destroyAllWindows()
