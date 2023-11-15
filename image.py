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
def get_faces(frame,face_net,confidence_threshold=0.5):
    # convert the frame into a blob to be ready for NN input
    blob = cv2.dnn.blobFromImage(frame, 1.0, (300, 300), (104, 177.0, 123.0))
    # set the image as input to the NN
    face_net.setInput(blob)
    # perform inference and get predictions
    output = np.squeeze(face_net.forward())
    # initialize the result list
    faces = []
    # Loop over the faces detected
    for i in range(output.shape[0]):
        confidence = output[i, 2]
        if confidence > confidence_threshold:
            box = output[i, 3:7] * \
                np.array([frame.shape[1], frame.shape[0],
                         frame.shape[1], frame.shape[0]])
            # convert to integers
            start_x, start_y, end_x, end_y = box.astype(np.int)
            # widen the box a little
            start_x, start_y, end_x, end_y = start_x - \
                10, start_y - 10, end_x + 10, end_y + 10
            start_x = 0 if start_x < 0 else start_x
            start_y = 0 if start_y < 0 else start_y
            end_x = 0 if end_x < 0 else end_x
            end_y = 0 if end_y < 0 else end_y
            # append to our list
            faces.append((start_x, start_y, end_x, end_y))
    return faces

def get_optimal_font_scale(text, width):
    """Determine the optimal font scale based on the hosting frame width"""
    for scale in reversed(range(0, 60, 1)):
        textSize = cv2.getTextSize(text, fontFace=cv2.FONT_HERSHEY_DUPLEX, fontScale=scale/10, thickness=1)
        new_width = textSize[0][0]
        if (new_width <= width):
            return scale/10
    return 1

def predict_gender(image, face_net, gender_net,GENDER_LIST,MODEL_MEAN_VALUES):
    frame_width = 300
    frame_height = 300
    # Convert image to RGB
    img_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    img = cv2.resize(img_rgb, (frame_width, frame_height))
    blob = cv2.dnn.blobFromImage(img, 1, (227, 227), MODEL_MEAN_VALUES, swapRB=False)
    gender_net.setInput(blob)
    gender_preds = gender_net.forward()
    gender = GENDER_LIST[gender_preds[0].argmax()]
    male_count = int(gender == 'Male')
    female_count = int(gender == 'Female')
    return male_count, female_count

def get_gender_count(image, face_net, gender_net,GENDER_LIST,MODEL_MEAN_VALUES,confidence_threshold=0.5):
    # Initialize gender counts
    male_count = 0
    female_count = 0
    # Detect faces in the image
    male_count, female_count = predict_gender(image, face_net, gender_net,GENDER_LIST,MODEL_MEAN_VALUES)
    # Calculate gender bias confidence
    total_count = male_count + female_count
    confidence = max(male_count, female_count) / total_count if total_count > 0 else 0

    # Return the gender counts and confidence
    return male_count, female_count, confidence

# from: https://stackoverflow.com/questions/44650888/resize-an-image-without-distortion-opencv
def image_resize(image, width = None, height = None, inter = cv2.INTER_AREA):
    # initialize the dimensions of the image to be resized and
    # grab the image size
    dim = None
    (h, w) = image.shape[:2]
    # if both the width and height are None, then return the
    # original image
    if width is None and height is None:
        return image
    # check to see if the width is None
    if width is None:
        # calculate the ratio of the height and construct the
        # dimensions
        r = height / float(h)
        dim = (int(w * r), height)
    # otherwise, the height is None
    else:
        # calculate the ratio of the width and construct the
        # dimensions
        r = width / float(w)
        dim = (width, int(h * r))
    # resize the image
    return cv2.resize(image, dim, interpolation = inter)


# Main function
def main(url):

    # The gender model architecture
    # https://drive.google.com/open?id=1W_moLzMlGiELyPxWiYQJ9KFaXroQ_NFQ
    GENDER_PROTO = 'weights/deploy_gender.prototxt'
    # The gender model pre-trained weights
    # https://drive.google.com/open?id=1AW3WduLk1haTVAxHOkVS_BEzel1WXQHP
    GENDER_MODEL = 'weights/gender_net.caffemodel'
    # Each Caffe Model impose the shape of the input image also image preprocessing is required like mean
    # substraction to eliminate the effect of illunination changes
    MODEL_MEAN_VALUES = (78.4263377603, 87.7689143744, 114.895847746)
    # Represent the gender classes
    GENDER_LIST = ['Male', 'Female']
    # https://raw.githubusercontent.com/opencv/opencv/master/samples/dnn/face_detector/deploy.prototxt
    FACE_PROTO = "weights/deploy.prototxt"
    # https://raw.githubusercontent.com/opencv/opencv_3rdparty/dnn_samples_face_detector_20180205_fp16/res10_300x300_ssd_iter_140000_fp16.caffemodel
    FACE_MODEL = "weights/res10_300x300_ssd_iter_140000_fp16.caffemodel"
    # Load the Haar cascade for face detection
    #face_cascade = cv2.CascadeClassifier(cascade_file)

    # load face detection Caffe model
    face_net_main = cv2.dnn.readNetFromCaffe(FACE_PROTO, FACE_MODEL)

    # load gender Caffe model
    gender_net_main = cv2.dnn.readNetFromCaffe(GENDER_PROTO, GENDER_MODEL)

    # Get the URL from the user
   # url = input("Enter the URL of the webpage containing the images: ")

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
        male_count, female_count, confidence = get_gender_count(image, face_net_main, gender_net_main,GENDER_LIST,MODEL_MEAN_VALUES)

        # Display the results
        #print("Image URL:{}")
        print("Gender Count:")
        print(f"Male: {male_count}")
        print(f"Female: {female_count}")
        print(f"Gender Bias Confidence: {confidence}")

    return male_count, female_count, confidence


# Run the program
if __name__ == "__main__":
    main()

