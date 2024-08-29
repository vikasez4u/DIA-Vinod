import cv2
import requests
import numpy as np
from retinaface import RetinaFace
from deepface import DeepFace


# Function to download the image
def download_image(url):
  response = requests.get(url)
  if response.status_code == 200:
    img_data = response.content
    img_array = np.array(bytearray(img_data), dtype=np.uint8)
    image = cv2.imdecode(img_array, -1)
    return image
  else:
    print(f"Failed to download image: {response.status_code}")
    return None


# Function to detect faces using RetinaFace
def detect_and_crop_faces(image):
  faces = RetinaFace.detect_faces(image)
  face_boxes = []
  for face_info in faces.values():
    x, y, w, h = face_info['facial_area']
    face = image[y:y + h, x:x + w]
    face_boxes.append(face)
  return face_boxes


# Function to analyze the gender of detected faces and count women
def analyze_faces(faces):
  women_count = 0
  for i, face in enumerate(faces):
    # Analyze the gender using DeepFace
    result = DeepFace.analyze(face, actions=['gender'], enforce_detection=False)
    if isinstance(result, list):
      result = result[0]  # Get the first result in the list
    gender = result['gender']
    print(f"Face {i + 1}: Gender - {gender}")
    if gender['Woman'] > 50:  # Threshold of 50% to classify as Woman
      women_count += 1
  return women_count


# Main function to process the image
def main():
  url = "https://cdn.prod.website-files.com/5f6cc9cd16d59d990c8fca33/6328a93e3defd981448f5252_milestones-women-history-1.jpg"

  # Download the image
  image = download_image(url)
  if image is None:
    return

  # Detect and crop faces
  faces = detect_and_crop_faces(image)

  if not faces:
    print("No faces detected.")
    return

  # Analyze each face and count women
  women_count = analyze_faces(faces)

  print(f"Total number of women detected: {women_count}")


if __name__ == "__main__":
  main()
