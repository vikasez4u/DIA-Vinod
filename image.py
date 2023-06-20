
import imghdr
import urllib.request
import numpy as np
import cv2
import requests
from bs4 import BeautifulSoup
from deepface import DeepFace


# In[5]:


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
        print(response.status_code)

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
    image = cv2.resize(image, (720, 640))

    return image


# In[6]:


def detect_and_crop_faces(image, net, confidence_threshold):
    # Set the confidence threshold for face detection
    net.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)
    net.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA_FP16)
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


# In[7]:


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
        face_blob = cv2.dnn.blobFromImage(face_image, 1.0, (227, 227), (78.4263377603, 87.7689143744, 114.895847746),
                                          swapRB=False)

        # Pass the face blob through the model to get the predicted gender
        model.setInput(face_blob)
        predictions = model.forward()
        gender = "Male" if predictions[0][0] < 0.5 else "Female"
        genders.append(gender)
    # Return the list of predicted genders
    return genders


# In[8]:


def get_gender_count(image, face_net, gender_net, confidence_threshold=0.5):
    # Detect the faces in the image

    faces, face_box = detect_and_crop_faces(image, face_net, confidence_threshold)

    # Pass the face through the gender classification network to get the gender prediction
    gender_label = classify_gender_vgg(image, face_box, gender_net)

    # Use DeepFace to predict the gender of the face
    result = DeepFace.analyze(img_path=face_img)

    # Initialize variables to count the number of male and female faces
    male_count = 0
    female_count = 0

    # Classify the gender of each face and count the number of male and female faces
    for gender in gender_label:

        # Update the male and female count based on the gender prediction
        if gender == "Male":
            male_count += 1
        else:
            female_count += 1

    # Check if the image is gender-biased or not
    total_faces = len(faces)
    if total_faces == 0:
        gender_bias_confidence = 0.0
    else:
        gender_bias_confidence = abs(male_count - female_count) / total_faces

    # Return the male and female count and the gender bias confidence score
    return male_count, female_count, gender_bias_confidence


# In[9]:


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


# In[ ]:


###Combained Code


# In[12]:


# Main function to run the program
def main():
    # The gender model architecture
    GENDER_MODEL = 'weights/deploy_gender.prototxt'
    # The gender model pre-trained weights
    GENDER_PROTO = 'weights/gender_net.caffemodel'
    # Each Caffe Model impose the shape of the input image also image preprocessing is required like mean
    # substraction to eliminate the effect of illunination changes
    MODEL_MEAN_VALUES = (78.4263377603, 87.7689143744, 114.895847746)
    # Represent the gender classes
    GENDER_LIST = ['Male', 'Female']
    # face detection model files
    FACE_PROTO = "weights/deploy.prototxt.txt"
    FACE_MODEL = "weights/res10_300x300_ssd_iter_140000_fp16.caffemodel"

    # load face detection Caffe model
    face_net_main = cv2.dnn.readNetFromCaffe(FACE_PROTO, FACE_MODEL)
    # Load gender prediction model
    gender_net_main = cv2.dnn.readNetFromCaffe(GENDER_MODEL, GENDER_PROTO)

    # Enter the webpage URL to extract image links
    url = input("Enter the URL of the webpage: ")
    # Get all the image links
    extracted_links, soup = extract_image_links(url)
    for image_url in extracted_links:
        # Download the image
        image = download_image(image_url)

        # If the image could not be downloaded, move on to the next image
        if image is None:
            continue

        # Detect faces and genders in the image
        male_count, female_count, confidence = get_gender_count(image, face_net_main, gender_net_main,
                                                                confidence_threshold=0.5)

        # Print the results for the current image
        print("Image URL:", image_url)
        print("Male count:", male_count)
        print("Female count:", female_count)
        print("Confidence:", confidence)


if __name__ == '__main__':
    main()
