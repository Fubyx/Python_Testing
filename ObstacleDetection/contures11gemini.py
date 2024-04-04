import cv2
import numpy as np


def is_overlapping(rect1, rect2):
  """
  Checks if two rectangles overlap (including partial overlap).

  Args:
      rect1: Tuple representing rectangle 1 (x, y, width, height).
      rect2: Tuple representing rectangle 2 (x, y, width, height).

  Returns:
      True if rectangles overlap, False otherwise.
  """
  x1, y1, w1, h1 = rect1
  x2, y2, w2, h2 = rect2
  return (
      x1 < x2 + w2 and
      x2 < x1 + w1 and
      y1 < y2 + h2 and
      y2 < y1 + h1
  )

def get_larger_rectangle(rect1, rect2):
  """
  Returns the rectangle with larger area.

  Args:
      rect1: Tuple representing rectangle 1 (x, y, width, height).
      rect2: Tuple representing rectangle 2 (x, y, width, height).

  Returns:
      Tuple representing the rectangle with larger area.
  """
  x1, y1, w1, h1 = rect1
  x2, y2, w2, h2 = rect2
  area1 = w1 * h1
  area2 = w2 * h2


  """
  area1 = cv2.contourArea(((rect1[0], rect1[1]), (rect1[0] + rect1[2], rect1[1]),
                           (rect1[0] + rect1[2], rect1[1] + rect1[3]), (rect1[0], rect1[1] + rect1[3])))
  area2 = cv2.contourArea(((rect2[0], rect2[1]), (rect2[0] + rect2[2], rect2[1]),
                           (rect2[0] + rect2[2], rect2[1] + rect2[3]), (rect2[0], rect2[1] + rect2[3])))
  """
  #return rect1 if area1 > area2 else rect2      #use this line to get the bigger Rectangle of the two

  return rect2 if area1 > area2 else rect1      #use this line to get the smaller Rectangle of the two

def is_line(contour):
    """
    Checks if the contour is a line by comparing its perimeter and area.

    Args:
        contour: NumPy array representing the contour.

    Returns:
        True if the contour is a line, False otherwise.
    """
    perimeter = cv2.arcLength(contour, True)
    area = cv2.contourArea(contour)
    print("Linie:" + str(perimeter) + " " + str(area))
    return perimeter > 1000 and area < 1000  # Adjust thresholds as needed


def main():
  # Webcam capture and initialization
  cap = cv2.VideoCapture(0)
  previous_rectangles = []

  while True:
    ret, frame = cap.read()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150)
    cv2.imshow("Canny", edges)
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    valid_rectangles = []
    for contour in contours:
        contour = np.array(contour, dtype=np.int32)
        # Check if contour is empty (has no points)
        if cv2.contourArea(contour) < 0:
            print("Empty contour encountered!")
            continue
        x, y, w, h = cv2.boundingRect(contour)
        
        area = w*h
        if not is_line(contour) and area > 5000 and w > 80 and h > 80:
            print(str(area) + " " + str(w) + " " + str(h) + "\n")
            is_larger = True
            for prev_rect in previous_rectangles:
                if is_overlapping(rect1=(x, y, w, h), rect2=prev_rect):
                    is_larger = get_larger_rectangle(rect1=(x, y, w, h), rect2=prev_rect) == (x, y, w, h)
                    break
            if is_larger:
                valid_rectangles.append((x, y, w, h))

    previous_rectangles = valid_rectangles.copy()

    for rect in valid_rectangles:
      x, y, w, h = rect
      cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

    cv2.imshow('Webcam', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
      break

  cap.release()
  cv2.destroyAllWindows()

if __name__ == '__main__':
  main()
