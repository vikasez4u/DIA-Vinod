import imghdr
import urllib.request
import numpy as np
import cv2
import requests
from bs4 import BeautifulSoup
from deepface import DeepFace
from PIL import Image
import tempfile

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

    return image


def detect_and_crop_faces(image, net, confidence_threshold):
    # Set the confidence threshold for face detection
    conf_threshold = confidence_threshold

    if image.shape[-1] == 4:  # check if the image has an alpha channel
        image = cv2.cvtColor(image, cv2.COLOR_RGBA2RGB)

    # Get the height and width of the image
    (h, w) = image.shape[:2]

    # Create a blob from the image and pass it through the network
    blob = cv2.dnn.blobFromImage(cv2.resize(image, (300, 300)), 1.0,
                                 (300, 300), (104.0, 177.0, 123.0))
    net.setInput(blob)
    detections = net.forward()

    # Loop over the detections and extract the ROI and bounding box of each face
    faces = []
    face_boxes = []
    for i in range(0, detections.shape[2]):
        confidence = detections[0, 0, i, 2]

        # Check if the confidence is above the threshold
        if confidence > conf_threshold:
            # Get the coordinates of the bounding box
            box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
            (startX, startY, endX, endY) = box.astype("int")

            # Crop the face region from the image
            face = image[startY:endY, startX:endX]

            # Add the cropped face and bounding box to the lists
            faces.append(face)
            face_boxes.append(box.astype("int"))

    # Return the list of faces and face bounding boxes
    return faces, face_boxes


def classify_gender_vgg(image, face_boxes, model):
    # Create a list to hold the predicted genders
    genders = []

    # Loop over all the detected face boxes
    for face_box in face_boxes:
        # Convert face_box to integer values
        face_box = [int(x) for x in face_box]

        # Preprocess the face image
        face_image = image[face_box[1]:face_box[3], face_box[0]:face_box[2]]
        face_image = cv2.cvtColor(face_image, cv2.COLOR_RGBA2RGB)
        face_blob = cv2.dnn.blobFromImage(face_image, 1.0, (227, 227), (78.4263377603, 87.7689143744, 114.895847746), swapRB=False)

        # Pass the face blob through the model to get the predicted gender
        model.setInput(face_blob)
        predictions = model.forward()
        gender = "Male" if predictions[0][0] < 0.5 else "Female"
        genders.append(gender)

    # Return the list of predicted genders
    return genders

def get_gender_count(image, face_net, gender_net, confidence_threshold=0.5):
    # Convert the image to RGB format if it has an alpha channel
    if image.shape[-1] == 4:
        image = cv2.cvtColor(image, cv2.COLOR_RGBA2RGB)

    # Convert the image to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)

    # Get the height and width of the image
    (h, w) = image.shape[:2]

    # Create a blob from the image and pass it through the face detection network
    blob = cv2.dnn.blobFromImage(cv2.resize(image, (300, 300)), 1.0, (300, 300), (104.0, 177.0, 123.0))
    face_net.setInput(blob)
    detections = face_net.forward()

    # Initialize gender counts
    male_count = 0
    female_count = 0

    # Process each detected face
    for i in range(0, detections.shape[2]):
        confidence = detections[0, 0, i, 2]

        # Check if the confidence is above the threshold
        if confidence > confidence_threshold:
            # Get the coordinates of the bounding box
            box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
            (startX, startY, endX, endY) = box.astype("int")

            # Crop the face region from the image
            face = image[startY:endY, startX:endX]

            # Classify the gender of the face using DeepFace
            try:
                result = DeepFace.analyze(face, actions=['gender'], enforce_detection=False)
                gender = result[0]['gender']
                if gender == 'Man':
                    male_count += 1
                elif gender == 'Woman':
                    female_count += 1
            except ValueError:
                # Face could not be detected or gender prediction failed
                pass

    # Calculate gender bias confidence
    total_count = male_count + female_count
    confidence = max(male_count, female_count) / total_count if total_count > 0 else 0

    # Return the gender counts and confidence
    return male_count, female_count, confidence 

def extract_image_links(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    img_tags = soup.find_all("img")
    img_links = []
    for img in img_tags:
        img_link = img.get("src")
        if img_link.endswith(".jpg") or img_link.endswith(".jpeg") or img_link.endswith(".png"):
            img_links.append(img_link)
    return img_links, soup


# Main function
def main():
    # The gender model architecture
    GENDER_MODEL = 'weights/gender_net.caffemodel'
    # The gender model pre-trained weights
    GENDER_PROTO = 'weights/deploy_gender.prototxt'
    # face detection model files
    FACE_PROTO = "weights/deploy.prototxt.txt"
    FACE_MODEL = "weights/res10_300x300_ssd_iter_140000_fp16.caffemodel"
    # Download the Haar cascade XML file for face detection
    #cascade_file = "weights/haarcascade_frontalface_default.xml"

    # Load the Haar cascade for face detection
    #face_cascade = cv2.CascadeClassifier(cascade_file)

    # load face detection Caffe model
    face_net_main = cv2.dnn.readNetFromCaffe(FACE_PROTO, FACE_MODEL)

    # load gender Caffe model
    gender_net_main = cv2.dnn.readNetFromCaffe(GENDER_PROTO, GENDER_MODEL)

    # Get the URL from the user
    url = input("Enter the URL of the webpage containing the images: ")

    # Extract image links from the webpage
    img_links, soup = extract_image_links(url)

    # Process each image
    for i, img_link in enumerate(img_links):
        print(f"Processing image {i+1}/{len(img_links)}")

        # Download the image
        image = download_image(img_link)

        # If the image download fails, skip to the next image
        if image is None:
            continue

        # Detect faces and genders in the image
        male_count, female_count, confidence = get_gender_count(image, face_net_main, gender_net_main)

        # Display the results
        print("Gender Count:")
        print(f"Male: {male_count}")
        print(f"Female: {female_count}")
        print(f"Gender Bias Confidence: {confidence}")


# Run the program
if __name__ == "__main__":
    main()
