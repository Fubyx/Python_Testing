import cv2

# Capture video from webcam
cap = cv2.VideoCapture(0)

# Define saturation adjustment factor (positive value increases saturation)
saturation_factor = 2
# Define brightness adjustment value (positive value increases brightness)
brightness = -30

while True:
  # Read a frame from the webcam
  ret, frame = cap.read()

  # Check if frame is read correctly
  if not ret:
    print("Error! Unable to capture frame")
    break

  # Convert frame to HSV color space
  hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

  # Split the channels
  h, s, v = cv2.split(hsv_frame)

  # Adjust saturation
  s = cv2.multiply(s, saturation_factor)

  # Merge the channels back
  hsv_adjusted = cv2.merge((h, s, v))

  # Convert back to BGR for display
  adjusted_frame = cv2.cvtColor(hsv_adjusted, cv2.COLOR_HSV2BGR)

  # Increase brightness of the frame
  adjusted_frame = cv2.convertScaleAbs(adjusted_frame, alpha=1.0, beta=brightness)


  # Display the original and adjusted frame
  cv2.imshow('Original Frame', cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY))
  cv2.imshow('Adjusted Frame', cv2.cvtColor(adjusted_frame, cv2.COLOR_BGR2GRAY))

  # Exit on 'q' key press
  if cv2.waitKey(1) == ord('q'):
    break

# Release capture and close windows
cap.release()
cv2.destroyAllWindows()
