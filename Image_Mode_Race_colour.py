from collections import Counter
import imghdr
import numpy as np
import cv2
import requests
from bs4 import BeautifulSoup
from deepface import DeepFace
from webcolors import CSS3_HEX_TO_NAMES, hex_to_rgb, rgb_to_name
from mtcnn import MTCNN
import db as diadb
from app import app
from datetime import datetime

# Download the image
def download_image(url):
    # Set the user-agent header
    headers = {"User-Agent": "Chrome/51.0.2704.103"}

    # Send GET request
    response = requests.get(url, headers=headers)

    # Save the image
    if response.status_code == 200:
        img_data = response.content
    else:
        print(f"Failed to download image: {response.status_code}")
        return None

    # Check the image format
    img_format = imghdr.what(None, img_data)

    # If the image format is not supported, exit
    if img_format not in ["jpeg", "png", "jpg"]:
        print(f"Unsupported image format: {img_format}")
        return None

    # Convert the image data to a numpy array
    img_array = np.array(bytearray(img_data), dtype=np.uint8)

    # Read the image using OpenCV
    image = cv2.imdecode(img_array, -1)

    # If the image has 4 channels (RGBA), convert it to RGB
    if image.shape[-1] == 4:
        image = cv2.cvtColor(image, cv2.COLOR_RGBA2RGB)

    return image

# Detect faces and crop them
def detect_and_crop_faces(image, face_net, confidence_threshold=0.5):
    detector = MTCNN()
    results = detector.detect_faces(image)

    faces = []
    face_boxes = []

    for result in results:
        if result['confidence'] > confidence_threshold:
            x, y, width, height = result['box']
            x1, y1 = abs(x), abs(y)
            x2, y2 = x1 + width, y1 + height
            face = image[y1:y2, x1:x2]

            faces.append(face)
            face_boxes.append(result['box'])

    return faces, face_boxes

def get_gender_count(image, gender_net, confidence_threshold=0.5):
    # Detect faces and genders in the image using MTCNN
    faces, _ = detect_and_crop_faces(image, confidence_threshold)

    # Initialize gender counts
    male_count = 0
    female_count = 0
    Skin = []
    Races = []

    # Process each detected face
    for face_image in faces:
        # Preprocess the face image for gender classification
        face_blob = cv2.dnn.blobFromImage(cv2.resize(face_image, (227, 227)), 1.0, (227, 227), (78.4263377603, 87.7689143744, 114.895847746), swapRB=False)

        # Pass the face blob through the gender classification model
        gender_net.setInput(face_blob)
        predictions = gender_net.forward()
        Skin.append(extract_skin_regions(face_image))
        Races.append(get_race_detail(face_image))

        # Get the predicted gender
        gender = "Male" if predictions[0][0] < 0.5 else "Female"

        # Update the gender counts
        if gender == "Male":
            male_count += 1
        else:
            female_count += 1

    # Calculate gender bias confidence
    total_count = male_count + female_count
    confidence = max(male_count, female_count) / total_count if total_count > 0 else 0

    # Return the gender counts and confidence
    return male_count, female_count, confidence, Skin, Races

# Extract skin color
def closest_color(requested_color):
    min_colors = {}
    for key, name in CSS3_HEX_TO_NAMES.items():
        r_c, g_c, b_c = hex_to_rgb(key)
        rd = (r_c - requested_color[0]) ** 2
        gd = (g_c - requested_color[1]) ** 2
        bd = (b_c - requested_color[2]) ** 2
        min_colors[(rd + gd + bd)] = name
    return min_colors[min(min_colors.keys())]

def extract_skin_regions(image):
    # Convert the image to the HSV color space
    hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # Define the lower and upper bounds for skin color in HSV space
    lower_bound = np.array([0, 20, 70], dtype=np.uint8)
    upper_bound = np.array([20, 255, 255], dtype=np.uint8)

    # Create a mask to identify skin regions based on the color range
    skin_mask = cv2.inRange(hsv_image, lower_bound, upper_bound)

    # Find the average color of the skin regions
    skin_color = cv2.mean(image, mask=skin_mask)[:3]

    # Convert the BGR color to RGB format
    skin_color_rgb = (int(skin_color[2]), int(skin_color[1]), int(skin_color[0]))

    # Find the closest predefined CSS3 color name for the RGB value
    closest_name = closest_color(skin_color_rgb)

    return closest_name

# Get additional image details (gender, race, etc.)
def get_race_detail(image):
    # Use DeepFace to predict the race of the face
    result = DeepFace.analyze(img_path=image, actions=["race"], enforce_detection=False)
    print(result)
    for entry in result:
        dominant_race = entry['dominant_race']
    return dominant_race

# Extract image links from a webpage
def extract_image_links(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    img_tags = soup.find_all("img")
    img_links = []
    for img in img_tags:
        img_link = img.get("src")
        if img_link and (img_link.endswith(".jpg") or img_link.endswith(".jpeg") or img_link.endswith(".png")):
            img_links.append(img_link)
    return img_links

# Main function
def main(url):
    transaction_id = datetime.now().strftime("%Y%m%d%H%M%S")
    # Load the gender model
    GENDER_MODEL = 'weights/gender_net.caffemodel'
    GENDER_PROTO = 'weights/deploy_gender.prototxt'


    # Load the gender Caffe model
    gender_net = cv2.dnn.readNetFromCaffe(GENDER_PROTO, GENDER_MODEL)

    # Get the URL from the user
    #url = input("Enter the URL of the webpage containing the images: ")

    # Extract image links from the webpage
    img_links = extract_image_links(url)

    biased_alt_results = []
    # Process each image
    for i, img_link in enumerate(img_links):
        print(f"Processing image {i+1}/{len(img_links)}")
        # Download the image
        image = download_image(img_link)

        # If the image download fails, skip to the next image
        if image is None:
            continue

        # Get gender, skin color, and race details only if faces are present
        male_count, female_count, confidence, skin_colors, races = get_gender_count(image, gender_net)

        # Check if any faces were detected
        total_count = male_count + female_count
        if total_count > 0:
            with app.app_context():
              diadb.create_table('Image_Txt_Results')
            # Display the results for each face
            print(f"Image URL: {img_link}")
            print("Gender Count:")
            print(f"Male: {male_count}")
            print(f"Female: {female_count}")
            print(f"Gender Bias Confidence: {confidence}")

            # Check if there are skin color regions detected
            counted_values_skin = Counter(skin_colors)
            if len(counted_values_skin) > 0:
                max_skin_key = max(counted_values_skin, key=counted_values_skin.get)
                print(f"Skin Color: {max_skin_key}")
            else:
                print("No skin color regions detected in the image.")

            # Check if there are race details detected
            counted_values_race = Counter(races)
            if len(counted_values_race) > 0:
                max_race_key = max(counted_values_race, key=counted_values_race.get)
                print(f"Dominant Race: {max_race_key}")
            else:
                print("No race detected in the image.")

            with app.app_context():
              diadb.saveImage('Image_Txt_Results', transaction_id, 'Image', male_count, female_count, confidence, max_skin_key, max_race_key, img_link)
            biased_alt_results.append((img_link,male_count,female_count,confidence,max_skin_key,max_race_key))
        else:
            print("No faces detected in the image.")

    return biased_alt_results

if __name__ == "__main__":
    main()


# In[ ]:
