import flask
import requests
import urllib

from bs4 import BeautifulSoup
import re
from PIL import Image, UnidentifiedImageError
import pytesseract
from io import BytesIO, StringIO
import os
from urllib.parse import urlparse
import pandas as pd
from flask import Flask, render_template, request, redirect, url_for

import image

app = Flask(__name__)

@app.route('/')
@app.route('/static/')
def hello_world():
    return render_template('index.html')

@app.route('/result', methods=['POST', 'GET'])
def result():
        url = request.form['urlName']
        #print('URL : ' + url)
        #print(request.values)
        modelType = request.form['selectedElement'].split(':')[1].strip()
        print(modelType)
        if modelType == 'Text':
         # print(modelType)
          return redirect(url_for('text'), code=307)
        if modelType == 'Image':
         # print(modelType)
          image.imageexecution(url)
        return None

@app.route('/text',methods=['POST'])
def text():
      url = request.form['urlName']
      print('Text File Entered URL : ' + url)
      text = extract_text_from_url(url)
      #print('text:')
      #print(text)
      alt_texts = extract_alt_text_from_url(url)
      #print('alt_texts:')
      #print(alt_texts)
      if text is not None:
          biased_sentences, biased_words = detect_gender_biased_sentences(text)
          if biased_sentences:
              print('Biased sentences:')
              biased_sentences = [*set(biased_sentences)]
              for sentence in biased_sentences:
                  print(sentence)

              print('Biased words:')
              biased_words = [*set(biased_words)]
              for word in biased_words:
                  print(word)
          else:
              print('No Biased Text')

      if alt_texts is not None:
          biased_alt_texts, biased_alt_words = detect_gender_biased_alt_texts(alt_texts)
          print('Biased alt texts:')
          #  i=input(0)
          alt_textary = []
          image_linkary = []
          biased_alt_texts = [*set(biased_alt_texts)]
          for alt_text, image_link in biased_alt_texts:
              # i=int(i) + 1
              # S  print(i)
              print('Alt text:', alt_text)
              alt_textary.append(alt_text)
              print('Image link:', image_link)
              image_linkary.append(image_link)
              print('---')
          print('Biased alt words:')
          biased_alt_words = [*set(biased_alt_words)]
          for alt_word in biased_alt_words:
              print(alt_word)
          # print(alt_textary)
          # print(image_linkary)
      else:
          print('No Biased Alt Text')

      biased_sentences_img, biased_words_img, link_img = extract_text_from_images(url)
      if biased_sentences_img:
          print('Biased sentences from images:')
          for sentences in biased_sentences_img:
              for sentence in sentences:
                  print(sentence)

          print('Biased words from images:')
          for words in biased_words_img:
              for word in words:
                  print(word)

          print('Image links:')
          for img_link in link_img:
              print(img_link)

      else:
          print('No Biased Text in image')
      return render_template('output.html', **locals())


def extract_text_from_url(url):
    try:
        with urllib.request.urlopen(url) as response:
            html = response.read()
        text = str(html)
        soup = BeautifulSoup(text, 'html.parser')
        # response.raise_for_status()
        # soup = BeautifulSoup(response, 'html.parser')
        text = soup.get_text()
        return text
    except request.exceptions.RequestException as e:
        print("Error occurred while retrieving the web page:", e)
        return None
    except Exception as e:
        print("An error occurred:", e)
        return None


def extract_alt_text_from_url(url):
    try:
        with urllib.request.urlopen(url) as response:
            html = response.read()
        text = str(html)
        soup = BeautifulSoup(text, 'html.parser')
        # response.raise_for_status()
        # soup = BeautifulSoup(response, 'html.parser')
        alt_texts = []
        images = soup.find_all('img')
        for image in images:
            alt = image.get('alt')
            src = image.get('src')
            if alt:
                alt_texts.append((alt, src))
        return alt_texts
    except request.exceptions.RequestException as e:
        print("Error occurred while retrieving the web page:", e)
        return None
    except Exception as e:
        print("An error occurred:", e)
        return None


def process_image(image_url):
    ALLOWED_FORMATS = ['jpeg', 'jpg', 'png']
    try:
        parsed_url = urlparse(image_url)
        #print('parsed_url:')
        #print(parsed_url)
        #print(image_url)
        if not parsed_url.scheme:
            image_url = f'http:/{image_url}'

        # Check the file extension of the image URL
        _, ext = os.path.splitext(image_url)
        ext = ext[1:].lower()  # Remove  the leading dot and convert to lowercase
        #print('ext')
        #print(ext)
        # Skip processing if the file extension is not in the allowed formats
        if ext not in ALLOWED_FORMATS:
            # print(f'Skipping image {image_url}: Unsupported format')
            return None
        #print(image_url)
        # Load the image from URL
        with urllib.request.urlopen(image_url) as response:
            html = response.read()
        text = str(html)
        text = 'No Biased'

        return text
        ## print(text)
        image = Image.open(BytesIO(response.read()))
        print(image_url)
        print(image)
        # Perform OCR using pytesseract
        text = pytesseract.image_to_string(image)

        return text
    except (request.exceptions.RequestException, OSError, UnidentifiedImageError) as e:
       ## print(f'Error processing image {image_url}: {str(e)}')
        return None


def detect_gender_biased_sentences(text):
    df = pd.read_excel('gender_biased_words.xlsx', sheet_name='word')
    gender_keywords = df['word'].tolist()
    sentences = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s', text)  # Split text into sentences
    biased_sentences = []
    biased_words = []
    for sentence in sentences:
        sentence = sentence.lower().strip()
        words = re.findall(r'\b\w+\b', sentence)  # Split sentence into words
        for i in range(len(words)):
            if words[i] in gender_keywords:
                start = max(0, i - 5)
                end = min(i + 6, len(words))
                trimmed_sentence = ' '.join(words[start:end])
                trimmed_sentence = re.sub(r'\b' + words[i] + r'\b', '\033[91m' + words[i] + '\033[0m', trimmed_sentence)
                biased_sentences.append(trimmed_sentence)
                biased_words.append(words[i])
                break  # Move to the next sentence
    return biased_sentences, biased_words


def detect_gender_biased_alt_texts(alt_texts):
    df = pd.read_excel('gender_biased_words.xlsx', sheet_name='word')
    gender_keywords = df['word'].tolist()
    biased_alt_texts = []
    biased_words = []
    for alt_text, image_link in alt_texts:
        alt_text = alt_text.lower().strip()
        words = re.findall(r'\b\w+\b', alt_text)
        for word in words:
            if word in gender_keywords:
                biased_alt_texts.append((alt_text, image_link))
                biased_words.append(word)
                break
    return biased_alt_texts, biased_words


def extract_text_from_images(url):
    # Send an HTTP GET request to the URL and retrieve the HTML content
    # response = request.args.get(url)
    # soup = BeautifulSoup(response.content, 'html.parser')
    with urllib.request.urlopen(url) as response:
        html = response.read()
    text = str(html)
    soup = BeautifulSoup(text, 'html.parser')
    # Find all <img> tags and extract the source (src) attribute
    img_tags = soup.find_all('img')
    image_urls = [img['src'] for img in img_tags]
    biased_sentences = []
    biased_words = []
    link = []

    # Process each image and extract the text
    for image_url in image_urls:
        text = process_image(image_url)
        if text:
            sentences, words = detect_gender_biased_sentences(text)
            if sentences:
                biased_sentences.append(sentences)
                biased_words.append(words)
                link.append(image_url)
    return biased_sentences, biased_words, link


@app.route("/form", methods=["POST", "GET"])
def page():
    return render_template("index.html")

@app.route('/index', methods=["POST", "GET"])
def index():
    msg1 = "back"
    return render_template("index.html")

app.run()
