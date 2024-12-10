import os
import imghdr
import cv2
import requests
from bs4 import BeautifulSoup
from deepface import DeepFace
from mtcnn import MTCNN
import webcolors
from collections import Counter
import db as diadb
from app import app
from datetime import datetime
from urllib.parse import urljoin
import numpy as np
from PIL import Image, UnidentifiedImageError
import pytesseract
import cairosvg
from io import BytesIO
import logging

# Map CSS colors
CSS3_HEX_TO_NAMES = webcolors.CSS3_HEX_TO_NAMES
logging.basicConfig(level=logging.INFO)

def download_image(url):
    headers = {"User-Agent": "Chrome/51.0.2704.103"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        img_data = response.content
    else:
        print(f"Failed to download image: {response.status_code}")
        return None
    img_format = imghdr.what(None, img_data)
    if img_format not in ["jpeg", "png", "jpg", "gif", "svg"]:
        print(f"Unsupported image format: {img_format}")
        return None
    img_array = np.array(bytearray(img_data), dtype=np.uint8)
    image = cv2.imdecode(img_array, -1)
    if image.shape[-1] == 4:
        image = cv2.cvtColor(image, cv2.COLOR_RGBA2RGB)
    return image

def process_image(image_url, base_url, transaction_id):
    try:
        image_url = urljoin(base_url, image_url)
        response = requests.get(image_url)
        response.raise_for_status()

        # Determine the image format
        _, ext = os.path.splitext(image_url)
        ext = ext.lower()

        if ext == '.svg':
            # Handle SVG by converting it to PNG
            return process_svg_image(response.content, transaction_id, image_url)
        else:
            return process_raster_image(response.content, transaction_id, image_url)
    except (requests.exceptions.RequestException, OSError, UnidentifiedImageError) as e:
        logging.error(f"Error processing image {image_url}: {str(e)}")
        return None

def process_raster_image(image_content, transaction_id, image_url):
    try:
        image = Image.open(BytesIO(image_content))
        text = pytesseract.image_to_string(image)
        return text
    except UnidentifiedImageError as e:
        print(f"Unidentified image error: {str(e)}")
        return None

def process_svg_image(svg_content, transaction_id, image_url):
    try:
        # Convert SVG to PNG using cairosvg
        png_image = cairosvg.svg2png(bytestring=svg_content)
        image = Image.open(BytesIO(png_image))
        text = pytesseract.image_to_string(image)
        return text
    except Exception as e:
        print(f"Error processing SVG image: {str(e)}")
        return None

def detect_and_crop_faces(image):
    detector = MTCNN()
    faces = detector.detect_faces(image)
    face_boxes = []
    for face_info in faces:
        x, y, w, h = face_info['box']
        face = image[y:y + h, x:x + w]
        face_boxes.append(face)
    return face_boxes

def get_gender_count(image, face_net, gender_net, confidence_threshold=0.5):
    faces = detect_and_crop_faces(image)
    male_count = 0
    female_count = 0
    Skin = []
    Races = []
    for face_image in faces:
        face_blob = cv2.dnn.blobFromImage(cv2.resize(face_image, (227, 227)), 1.0, (227, 227),
                                          (78.4263377603, 87.7689143744, 114.895847746), swapRB=False)
        gender_net.setInput(face_blob)
        predictions = gender_net.forward()
        Skin.append(extract_skin_regions(face_image))
        Races.append(get_race_detail(face_image))
        gender = "Male" if predictions[0][0] < 0.5 else "Female"
        if gender == "Male":
            male_count += 1
        else:
            female_count += 1
    total_count = male_count + female_count
    confidence = max(male_count, female_count) / total_count if total_count > 0 else 0
    return male_count, female_count, confidence, Skin, Races

def closest_color(requested_color):
    min_colors = {}
    for key, name in CSS3_HEX_TO_NAMES.items():
        r_c, g_c, b_c = webcolors.hex_to_rgb(key)
        rd = (r_c - requested_color[0]) ** 2
        gd = (g_c - requested_color[1]) ** 2
        bd = (b_c - requested_color[2]) ** 2
        min_colors[(rd + gd + bd)] = name
    return min_colors[min(min_colors.keys())]

def extract_skin_regions(image):
    hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    lower_bound = np.array([0, 20, 70], dtype=np.uint8)
    upper_bound = np.array([20, 255, 255], dtype=np.uint8)
    skin_mask = cv2.inRange(hsv_image, lower_bound, upper_bound)
    skin_color = cv2.mean(image, mask=skin_mask)[:3]
    skin_color_rgb = (int(skin_color[2]), int(skin_color[1]), int(skin_color[0]))
    closest_name = closest_color(skin_color_rgb)
    return closest_name

def get_race_detail(image):
    result = DeepFace.analyze(img_path=image, actions=["race"], enforce_detection=False)
    dominant_race = result[0]['dominant_race']
    return dominant_race

def extract_image_links(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    img_tags = soup.find_all("img")
    img_links = [urljoin(url, img.get("src")) if img.get("src").endswith((".jpg", ".jpeg", ".png", ".gif", ".svg")) else None for img in img_tags]
    return [link for link in img_links if link]

def main(url, transaction_id):
    #transaction_id = datetime.now().strftime("%Y%m%d%H%M%S")
    GENDER_MODEL = os.path.join(os.path.dirname(__file__), 'weights', 'gender_net.caffemodel')
    GENDER_PROTO = os.path.join(os.path.dirname(__file__), 'weights', 'deploy_gender.prototxt')
    FACE_PROTO = os.path.join(os.path.dirname(__file__), 'weights', 'deploy.prototxt')
    FACE_MODEL = os.path.join(os.path.dirname(__file__), 'weights', 'res10_300x300_ssd_iter_140000_fp16.caffemodel')

    gender_net = cv2.dnn.readNetFromCaffe(GENDER_PROTO, GENDER_MODEL)
    face_net = cv2.dnn.readNetFromCaffe(FACE_PROTO, FACE_MODEL)

    img_links = extract_image_links(url)
    biased_alt_results = []

    for i, img_link in enumerate(img_links):
        print(f"Processing image {i + 1}/{len(img_links)}: {img_link}")
        image = download_image(img_link)
        if image is None:
            continue

        male_count, female_count, confidence, skin_colors, races = get_gender_count(image, face_net, gender_net)
        total_count = male_count + female_count
        if total_count > 0:
            print(f"Image URL: {img_link}")
            print("Gender Count:")
            print(f"Male: {male_count}")
            print(f"Female: {female_count}")
            print(f"Gender Bias Confidence: {confidence}")

            counted_values_skin = Counter(skin_colors)
            max_skin_key = max(counted_values_skin, key=counted_values_skin.get) if counted_values_skin else "N/A"
            print(f"Skin Color: {max_skin_key}")

            counted_values_race = Counter(races)
            max_race_key = max(counted_values_race, key=counted_values_race.get) if counted_values_race else "N/A"
            print(f"Dominant Race: {max_race_key}")

            with app.app_context():
                diadb.save_image('Image_Txt_Results', transaction_id, 'Image', male_count, female_count, confidence, max_skin_key, max_race_key, img_link)
            biased_alt_results.append((img_link, male_count, female_count, confidence, max_skin_key, max_race_key))
        else:
            print("No faces detected in the image.")

    return biased_alt_results

if __name__ == "__main__":
    main()
