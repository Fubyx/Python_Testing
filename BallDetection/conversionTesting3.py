import cv2
import numpy as np

def convert_to_red_mask(image, threshold=10):
  """
  Converts pixels with high blue value (> red & green by threshold) to black, rest to white.

  Args:
      image: A BGR image loaded with OpenCV (cv2.imread).
      threshold: Minimum difference between blue and red/green (default 10).

  Returns:
      A new image with converted pixels (black or white).
  """
  # Convert image to BGR channels
  b, g, r = cv2.split(image)

  # Create a mask using casting (convert bool to uint8)
  mask = cv2.bitwise_and(b.astype(np.uint8) - r.astype(np.uint8) > threshold, 
                         b.astype(np.uint8) - g.astype(np.uint8) > threshold)


  # Invert the mask (high blue becomes black)
  mask = cv2.bitwise_not(mask)

  # Combine the mask with a white image to create the final result
  return cv2.bitwise_and(image, image, mask=mask)

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
  
  # Display the original and adjusted frame
  cv2.imshow('Original Frame', frame)
  cv2.imshow('Adjusted Frame', convert_to_red_mask(frame))

  # Exit on 'q' key press
  if cv2.waitKey(1) == ord('q'):
    break

# Release capture and close windows
cap.release()
cv2.destroyAllWindows()
