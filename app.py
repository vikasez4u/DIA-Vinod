
import requests
from bs4 import BeautifulSoup
import re
from PIL import Image, UnidentifiedImageError
import pytesseract
from io import BytesIO
import os
from urllib.parse import urlparse
import pandas as pd
from flask import Flask, render_template, request
import pandas as pd
import bleach

app = Flask(__name__)

def extract_text_from_url(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        text = soup.get_text()
        return text
    except requests.exceptions.RequestException as e:
        print("Error occurred while retrieving the web page:", e)
        return None
    except Exception as e:
        print("An error occurred:", e)
        return None

def extract_alt_text_from_url(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        alt_texts = []
        images = soup.find_all('img')
        for image in images:
            alt = image.get('alt')
            src = image.get('src')
            if alt:
                alt_texts.append((alt, src))
        return alt_texts
    except requests.exceptions.RequestException as e:
        print("Error occurred while retrieving the web page:", e)
        return None
    except Exception as e:
        print("An error occurred:", e)
        return None

def process_image(image_url):
    ALLOWED_FORMATS = ['jpeg', 'jpg', 'png']
    try:
        parsed_url = urlparse(image_url)
        if not parsed_url.scheme:
            image_url = f'http:/{image_url}'

        # Check the file extension of the image URL
        _, ext = os.path.splitext(image_url)
        ext = ext[1:].lower()  # Remove the leading dot and convert to lowercase

        # Skip processing if the file extension is not in the allowed formats
        if ext not in ALLOWED_FORMATS:
            #print(f'Skipping image {image_url}: Unsupported format')
            return None

        # Load the image from URL
        response = requests.get(image_url)
        print(response)
        #print(response.content)
        image = Image.open(BytesIO(response.content))

        # Perform OCR using pytesseract
        text = pytesseract.image_to_string(image)

        return text 
    except (requests.exceptions.RequestException, OSError, UnidentifiedImageError) as e:
        print(f'Error processing image {image_url}: {str(e)}')
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
                #trimmed_sentence = re.sub(r'\b' + re.escape(words[i]) + r'\b', '\033[91m' + words[i] + '\033[0m', trimmed_sentence)
                trimmed_sentence = re.sub(r'\b' + re.escape(words[i]) + r'\b', r'<span style="color:red">\g<0></span>', trimmed_sentence, flags=re.IGNORECASE)
                biased_sentences.append(trimmed_sentence)
                biased_words.append(words[i])
                break  # Move to the next sentence
    return biased_sentences, biased_words

def detect_gender_biased_sentences_img(text):
    df = pd.read_excel('gender_biased_words.xlsx', sheet_name='word')
    gender_keywords = df['word'].tolist()
    sentences = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s', text)  # Split text into sentences
    biased_sentences = []
    biased_words = []
    for sentence in sentences:
        sentence = sentence.lower().strip()
        words = re.findall(r'\b\w+\b', sentence)  # Split sentence into words
        sentence_biased_words = []  # Store the biased words found in the sentence
        for word in words:
            if word in gender_keywords:
                sentence_biased_words.append(word)

        if sentence_biased_words:
            start = max(0, words.index(sentence_biased_words[0]) - 5)
            end = min(words.index(sentence_biased_words[-1]) + 6, len(words))
            trimmed_sentence = ' '.join(words[start:end])
            trimmed_sentence = re.sub(r'\b' + '|'.join(re.escape(word) for word in sentence_biased_words) + r'\b',
                                      r'<span style="color:red">\g<0></span>', trimmed_sentence, flags=re.IGNORECASE)
            biased_sentences.append(trimmed_sentence)
            biased_words.extend(sentence_biased_words)

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
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    img_tags = soup.find_all('img')
    image_urls = [img['src'] for img in img_tags]

    biased_sentences = []
    biased_words = []
    image_links = []

    for image_url in image_urls:
        text = process_image(image_url)
        if text:
            sentences, words = detect_gender_biased_sentences_img(text)
            if sentences:
                biased_sentences.extend(sentences)
                biased_words.extend(words)
                image_links.append(image_url)

    return biased_sentences, biased_words, image_links


def highlight_biased_word(sentence, word):
    highlighted_sentence = re.sub(r'\b' + word + r'\b', '<span style="color:red">{}</span>'.format(word), sentence, flags=re.IGNORECASE)
    return highlighted_sentence


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/result', methods=['POST', 'GET'])
def result():
    url = request.form['url']
    text = extract_text_from_url(url)
    text_results, biased_words = detect_gender_biased_sentences(text)
    # Remove HTML tags from text_results
    text_results = [bleach.clean(sentence, tags=[], strip=True) for sentence in text_results]
    # Combine biased word and sentence side by side
    biased_results = [(word, highlight_biased_word(sentence, word)) for word, sentence in zip(biased_words, text_results)]
    
    #Extract Alt text from the URL 
    alt_text = extract_alt_text_from_url(url)
    #alt_text = extract_alt_text_from_url('https://www.goodgoodgood.co/articles/quotes-to-empower-women')
    #Find the biased terms from the Alt text 
    alt_texts, alt_words = detect_gender_biased_alt_texts(alt_text)
    #Higlight the biased word in the sentence 
    biased_alt_results = []
    for (alt_text, image_link), word in zip(alt_texts, alt_words):
        highlighted_text = highlight_biased_word(alt_text, word)
        biased_alt_results.append((word, highlighted_text, image_link))
    
    #Extract the text from the image 
    biased_img_results = []
    img_texts, img_words, img_link=extract_text_from_images(url)
    for text, link, words in zip(img_texts, img_link, img_words):
        highlighted_text = highlight_biased_word(text, words)
        biased_img_results.append((words, highlighted_text, link))

    return render_template('text_results.html', biased_results=biased_results, biased_alt_results=biased_alt_results, biased_img_results=biased_img_results)


if __name__ == '__main__':
    app.run() 
