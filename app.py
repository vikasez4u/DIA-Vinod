import os
import requests
import re
from bs4 import BeautifulSoup
from flask import Flask, render_template, request, session
from datetime import datetime
import pandas as pd
import bleach
from pexecute.thread import ThreadLoom
import db as diadb
from image_mode import main as image_mode_main  # Ensure image_mode_main is correctly imported

from spacy.matcher import Matcher
import spacy
import pytesseract
from PIL import Image, UnidentifiedImageError, ImageOps
from io import BytesIO
from urllib.parse import urljoin
import xml.etree.ElementTree as ET

# Load the spacy model
nlp = spacy.load("en_core_web_sm")

# Initialize Flask app
app = Flask(__name__)
app.secret_key = 'Digital Inclusivity Auditor'
pytesseract.pytesseract.tesseract_cmd = "C:\\Program Files\\Tesseract-OCR\\tesseract.exe"

# Function to read gender-biased words from an Excel file
def read_gender_terms(file_path):
    df = pd.read_excel(file_path)
    gender_terms = df['terms'].tolist()
    return [[{"TEXT": {"REGEX": f"(?i)^{term}$"}}] for term in gender_terms]

# Read gender-biased words from the Excel file in the uploads folder
uploads_folder = "uploads"
gender_terms_file = os.path.join(uploads_folder, "gender_biased_words.xlsx")
gender_terms = read_gender_terms(gender_terms_file)

# Initialize the Matcher
matcher = Matcher(nlp.vocab)
matcher.add("GENDER_TERMS", gender_terms)

# Define geography, race, and ethnicity related terms
geo_race_ethnicity_terms = [
    {"ENT_TYPE": "GPE"},  # Geopolitical entity
    {"ENT_TYPE": "LOC"},  # Location
    {"ENT_TYPE": "NORP"}  # Nationalities or religious or political groups
]

# Initialize the Matcher for geography, race, and ethnicity
geo_race_ethnicity_matcher = Matcher(nlp.vocab)
geo_race_ethnicity_matcher.add("GEO_RACE_ETHNICITY_TERMS", [geo_race_ethnicity_terms])

def extract_entities_from_text(text):
    doc = nlp(text)

    # Initialize containers for entities and their sentences
    gender_bias_entities = {}
    geography_entities = {}
    race_ethnicity_entities = {}

    # Extract sentences with relevant entities
    for sent in doc.sents:
        gender_matches = matcher(nlp(sent.text))
        if gender_matches:
            for match_id, start, end in gender_matches:
                term = sent[start:end].text
                if term not in gender_bias_entities:
                    gender_bias_entities[term] = []
                gender_bias_entities[term].append(sent.text)

        for ent in sent.ents:
            if ent.label_ == "GPE" or ent.label_ == "LOC":
                if ent.text not in geography_entities:
                    geography_entities[ent.text] = []
                geography_entities[ent.text].append(sent.text)
            elif ent.label_ == "NORP":
                if ent.text not in race_ethnicity_entities:
                    race_ethnicity_entities[ent.text] = []
                race_ethnicity_entities[ent.text].append(sent.text)

    total_sentences = len(list(doc.sents))
    mapped_sentences_geography = sum(len(v) for v in geography_entities.values())
    mapped_sentences_race_ethnicity = sum(len(v) for v in race_ethnicity_entities.values())
    mapped_sentences_gender_bias = sum(len(v) for v in gender_bias_entities.values())

    return {
        "gender_bias_entities": gender_bias_entities,
        "race_ethnicity_entities": race_ethnicity_entities,
        "total_sentences": total_sentences,
        "geography_entities": geography_entities,
        "mapped_sentences_geography": mapped_sentences_geography,
        "mapped_sentences_race_ethnicity": mapped_sentences_race_ethnicity,
        "mapped_sentences_gender_bias": mapped_sentences_gender_bias
    }

def is_image(url):
    image_extensions = ('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.webp')
    return url.lower().endswith(image_extensions)

def preprocess_image_for_ocr(image):
    gray_image = ImageOps.grayscale(image)
    inverted_image = ImageOps.invert(gray_image)
    return inverted_image

def extract_text_from_image(base_url, image_url):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
    try:
        if not image_url.startswith(('http://', 'https://')):
            image_url = urljoin(base_url, image_url)
        if not is_image(image_url):
            print(f"Skipping non-image file: {image_url}")
            return ""
        response = requests.get(image_url, headers=headers)
        if response.status_code == 200:
            try:
                img = Image.open(BytesIO(response.content))
                preprocessed_img = preprocess_image_for_ocr(img)
                text = pytesseract.image_to_string(preprocessed_img)
                if not text.strip():
                    print(f"No text extracted from image at URL: {image_url}")
                else:
                    print(f"Extracted text from image: '{text}' from URL: {image_url}")
                return text
            except UnidentifiedImageError:
                print(f"Error extracting text from image: cannot identify image file {image_url}")
                return ""
            except Exception as e:
                print(f"Error processing image file: {image_url}, error: {e}")
                return ""
        else:
            print(f"Error fetching image: {response.status_code} for URL: {image_url}")
            return ""
    except Exception as e:
        print(f"Error extracting text from image: {e}")
        return ""

def extract_text_from_svg(base_url, svg_url):
    try:
        if not svg_url.startswith(('http://', 'https://')):
            svg_url = urljoin(base_url, svg_url)
        response = requests.get(svg_url)
        if response.status_code == 200:
            try:
                root = ET.fromstring(response.content)
                text_elements = root.findall('.//{http://www.w3.org/2000/svg}text')
                text = ' '.join([elem.text for elem in text_elements if elem.text])
                print(f"Extracted text from SVG: '{text}' from URL: {svg_url}")
                return text
            except ET.ParseError as e:
                print(f"Error parsing SVG file: {e}")
                return ""
        else:
            print(f"Error fetching SVG: {response.status_code} for URL: {svg_url}")
            return ""
    except Exception as e:
        print(f"Error extracting text from SVG: {e}")
        return ""

def extract_text_from_url(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        textfromurl = soup.get_text()
        return textfromurl
    except requests.exceptions.RequestException as e:
        print("Error occurred while retrieving the web page:", e)
        return None
    except Exception as e:
        print("An error occurred:", e)
        return None

def detect_gender_biased_sentences(text):
    gender_keywords = [term for sublist in gender_terms for term in sublist]
    sentences = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s', text)  # Split text into sentences
    biased_sentences = []
    biased_words = []
    for sentence in sentences:
        sentence_lower = sentence.lower().strip()
        words = re.findall(r'\b\w+\b', sentence_lower)  # Split sentence into words
        for word in words:
            if any(re.match(gk[0]['TEXT']['REGEX'], word) for gk in gender_keywords):
                biased_sentences.append(sentence)
                biased_words.append(word)
                break  # Move to the next sentence
    return biased_sentences, biased_words

def highlight_biased_word(sentence, word):
    highlighted_sentence = re.sub(r'\b' + word + r'\b', '<span class="wordcolor">{}</span>'.format(word), sentence,
                                  flags=re.IGNORECASE)
    return highlighted_sentence

def extract_alt_text_from_url(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        alt_texts = [(img.get('alt'), img.get('src')) for img in soup.find_all('img') if img.get('alt')]
        return alt_texts
    except requests.exceptions.RequestException as e:
        print("Error occurred while retrieving the web page:", e)
        return None
    except Exception as e:
        print("An error occurred:", e)
        return None

def detect_gender_biased_alt_texts(alt_texts):
    gender_keywords = [term for sublist in gender_terms for term in sublist]
    biased_alt_texts = []
    biased_words = []
    for alt_text, image_link in alt_texts:
        alt_text_lower = alt_text.lower().strip()
        words = re.findall(r'\b\w+\b', alt_text_lower)
        for word in words:
            if any(re.match(gk[0]['TEXT']['REGEX'], word) for gk in gender_keywords):
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
        textimg = extract_text_from_image(url, image_url)
        if textimg:
            sentences, words = detect_gender_biased_sentences(textimg)
            if sentences:
                biased_sentences.extend(sentences)
                biased_words.extend(words)
                image_links.append(image_url)

    return biased_sentences, biased_words, image_links

def web_scrape_and_extract_entities(url):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')

        # Extract text content from paragraphs
        main_text = " ".join([p.text for p in soup.find_all('p')])

        # Extract alt text from images
        alt_texts_with_src = [(img.get('alt'), img.get('src')) for img in soup.find_all('img') if img.get('alt')]
        alt_texts = " ".join([alt for alt, src in alt_texts_with_src])

        # Extract OCR text from images
        ocr_texts_with_src = [(extract_text_from_image(url, img.get('src')), img.get('src')) for img in soup.find_all('img') if img.get('src')]
        ocr_texts = " ".join([ocr for ocr, src in ocr_texts_with_src if ocr])
        print(f"OCR texts extracted: {ocr_texts}")

        # Extract text from SVG images
        svg_texts_with_src = [(extract_text_from_svg(url, img.get('src')), img.get('src')) for img in soup.find_all('img') if img.get('src') and img.get('src').lower().endswith('.svg')]
        svg_texts = " ".join([svg for svg, src in svg_texts_with_src if svg])
        print(f"SVG texts extracted: {svg_texts}")

        main_text_entities = extract_entities_from_text(main_text)
        alt_text_entities = extract_entities_from_text(alt_texts)
        ocr_text_entities = [extract_entities_from_text(ocr) for ocr, src in ocr_texts_with_src if ocr]
        svg_text_entities = [extract_entities_from_text(svg) for svg, src in svg_texts_with_src if svg]

        data = {
            "main_text_entities": main_text_entities,
            "alt_text_entities": alt_text_entities,
            "ocr_text_entities": ocr_text_entities,
            "svg_text_entities": svg_text_entities,
            "alt_texts_with_src": alt_texts_with_src,
            "ocr_texts_with_src": ocr_texts_with_src,
            "svg_texts_with_src": svg_texts_with_src
        }
        return data
    else:
        print(f"Failed to fetch the webpage: {response.status_code}")
        return None

def print_entities(entities, entity_type):
    if any(entities.values()):  # Check if there's at least one non-empty entity list
        print(f"{entity_type} Entities and Associated Sentences:")
        for entity, sentences in entities.items():
            if sentences:  # Only print non-empty entity lists
                print(f"\nEntity: {entity}")
                for sentence in sentences:
                    print(f"- {sentence}")

def print_text_entities(text_entities, texts_with_src, text_type):
    for entities, (text, src) in zip(text_entities, texts_with_src):
        if any(entities.values()):  # Check if there's at least one non-empty entity list
            print(f"\nImage src: {src}")
            print(f"{text_type} Text: {text}")
            print_entities(entities["geography_entities"], "Geography")
            print_entities(entities["race_ethnicity_entities"], "Race and Ethnicity")
            print_entities(entities["gender_bias_entities"], "Gender Bias")

@app.route('/')
@app.route('/home')
@app.route('/dia/')
def hello_world():
    diadb.create_table("Biased_Words")
    return render_template('index.html')

@app.route('/output', methods=['POST', 'GET'])
def output():
    biased_txt_results = session.get('biased_txt_results')
    biased_alt_results = session.get('biased_alt_results')
    biased_img_results = session.get('biased_img_results')
    total_biased_text, total_biased_alt_text, total_biased_img_results, text_results_tr_Gender_Count, alt_text_results_tr_Gender_Count, img_text_results_tr_Gender_Count = diadb.text_summary_result(transaction_id)
    if request.method == "GET":
        return {
            'total_biased_text': total_biased_text,
            'total_biased_alt_text': total_biased_alt_text,
            'total_biased_img_results': total_biased_img_results,
            'text_results_tr_Gender_Count': text_results_tr_Gender_Count,
            'alt_text_results_tr_Gender_Count': alt_text_results_tr_Gender_Count,
            'img_text_results_tr_Gender_Count': img_text_results_tr_Gender_Count
        }

@app.route('/imageOp')
def imageop():
    image_biased_results = session.get('image_results')
    image_results_tr = diadb.image_summary_result(transaction_id)
    return render_template('imageOp.html', **locals())

@app.route('/parallelexec')
def parallelexec():
    biased_txt_results = session.get('biased_txt_results')
    biased_alt_results = session.get('biased_alt_results')
    biased_img_results = session.get('biased_img_results')
    image_biased_results = session.get('image_results')
    total_biased_text, total_biased_alt_text, total_biased_img_results, text_results_tr_Gender_Count, alt_text_results_tr_Gender_Count, img_text_results_tr_Gender_Count = diadb.text_summary_result(transaction_id)
    image_results_tr = diadb.image_summary_result(transaction_id)
    return render_template('parallelexec.html', **locals())

@app.route('/result', methods=['POST', 'GET'])
def result():
    global transaction_id
    global txt_results
    global alt_results
    global txt_img_results
    global image_results

    transaction_id = datetime.now().strftime("%Y%m%d%H%M%S")
    if request.method == "POST":
        data = request.get_json()
        url = data["updates"][0]["value"]
        modeltypetextcontent = ''
        modeltypeimagecontent = ''
        try:
            if data["updates"][1]["value"]:
                modeltypetextcontent = True
        except:
            print('Text option not selected')

        try:
            if data["updates"][2]["value"]:
                modeltypeimagecontent = True
        except:
            print('Image option not selected')

        if modeltypetextcontent and modeltypeimagecontent != '':
            # Parallel execution
            loom = ThreadLoom(max_runner_cap=2)
            loom.add_function(text, [url], {})
            loom.add_function(image_mode_main, [url], {})
            parllelexecresult = loom.execute()

            # using session to access the variables globally
            txt_results = parllelexecresult[0]['output'][0]
            alt_results = parllelexecresult[0]['output'][1]
            txt_img_results = parllelexecresult[0]['output'][2]
            image_results = parllelexecresult[1]['output']

            total_biased_text, total_biased_alt_text, total_biased_img_results, text_results_tr_Gender_Count, alt_text_results_tr_Gender_Count, img_text_results_tr_Gender_Count = diadb.text_summary_result(transaction_id)
            image_results_tr = diadb.image_summary_result(transaction_id)

            return {
                "file": "parallelexec",
                "txt_results": txt_results,
                "alt_results": alt_results,
                "txt_img_results": txt_img_results,
                "total_biased_text": total_biased_text,
                "total_biased_alt_text": total_biased_alt_text,
                "total_biased_img_results": total_biased_img_results,
                "text_results_tr_Gender_Count": text_results_tr_Gender_Count,
                "alt_text_results_tr_Gender_Count": alt_text_results_tr_Gender_Count,
                "img_text_results_tr_Gender_Count": img_text_results_tr_Gender_Count,
                "image_results": image_results,
                "image_results_tr": image_results_tr
            }

        elif modeltypetextcontent:
            txt_results, alt_results, txt_img_results = text(url)
            total_biased_text, total_biased_alt_text, total_biased_img_results, text_results_tr_Gender_Count, alt_text_results_tr_Gender_Count, img_text_results_tr_Gender_Count = diadb.text_summary_result(transaction_id)
            return {
                "file": "Text",
                "txt_results": txt_results,
                "alt_results": alt_results,
                "txt_img_results": txt_img_results,
                "total_biased_text": total_biased_text,
                "total_biased_alt_text": total_biased_alt_text,
                "total_biased_img_results": total_biased_img_results,
                "text_results_tr_Gender_Count": text_results_tr_Gender_Count,
                "alt_text_results_tr_Gender_Count": alt_text_results_tr_Gender_Count,
                "img_text_results_tr_Gender_Count": img_text_results_tr_Gender_Count
            }

        elif modeltypeimagecontent:
            image_results = image_mode_main(url)
            image_results_tr = diadb.image_summary_result(transaction_id)
            return {
                "file": "Image",
                "image_results": image_results,
                "image_results_tr": image_results_tr
            }
        else:
            pass

@app.route('/text', methods=['POST'])
def text(url):
    print('Text File Entered URL : ' + url)
    textip = extract_text_from_url(url)
    text_results, biased_words = detect_gender_biased_sentences(textip)
    text_results = [bleach.clean(sentence, tags=[], strip=True) for sentence in text_results]
    biased_results = [(word, highlight_biased_word(sentence, word)) for word, sentence in zip(biased_words, text_results)]

    alt_text = extract_alt_text_from_url(url)
    alt_texts, alt_words = detect_gender_biased_alt_texts(alt_text)
    biased_alt_results = []
    for (alt_text, image_link), word in zip(alt_texts, alt_words):
        highlighted_text = highlight_biased_word(alt_text, word)
        biased_alt_results.append((word, highlighted_text, image_link))

    biased_img_results = []
    img_texts, img_words, img_link = extract_text_from_images(url)
    for textres, link, words in zip(img_texts, img_link, img_words):
        highlighted_text = highlight_biased_word(textres, words)
        biased_img_results.append((words, highlighted_text, link))
    print(biased_results)
    print(biased_alt_results)
    print(biased_img_results)
    return biased_results, biased_alt_results, biased_img_results

@app.route("/form", methods=["POST", "GET"])
def page():
    return render_template("index.html")

@app.route('/index', methods=["POST", "GET"])
def index():
    return render_template("index.html")

@app.teardown_appcontext
def close_database_connection(exception=None):
    diadb.close_db(exception)

@app.route('/genderresults', methods=["GET"])
def genderresults():
    gender_results = diadb.gender_result()
    gen_res = []
    for gender_result in gender_results:
        dict = {"id": str(gender_result[0]), "GenderName": gender_result[1]}
        gen_res.append(dict)
    return {"genderresults": gen_res}

@app.route('/gendersave', methods=["POST"])
def gendersave():
    data = request.get_json()
    name = data["updates"][0]["value"]
    result = diadb.gender_save(name)
    return {'result': result}

@app.route('/genderupdate', methods=["POST"])
def genderupdate():
    data = request.get_json()
    id = int(data["updates"][0]["value"])  # Ensure ID is passed as integer
    name = data["updates"][1]["value"]
    result = diadb.gender_update(id, name)
    return {'result': result}

@app.route('/genderdelete', methods=["POST"])
def genderdelete():
    data = request.get_json()
    id = int(data["updates"][0]["value"])  # Ensure ID is passed as integer
    result = diadb.gender_delete(id)
    return {'result': result}

@app.route('/baisedwordresults', methods=["GET"])
def baisedwordresults():
    baisedword_results = diadb.biased_word_result()
    gen_res = []
    for baisedword_result in baisedword_results:
        dict = {"GenderName": str(baisedword_result[0]), "BaisedWord": baisedword_result[1], "id": str(baisedword_result[2])}
        gen_res.append(dict)
    return {'baisedword_results': gen_res}

@app.route('/baisedwordsave', methods=["POST"])
def baisedwordsave():
    data = request.get_json()
    name = data["updates"][0]["value"]
    genderId = int(data["updates"][1]["value"])  # Ensure ID is passed as integer
    result = diadb.biased_word_save(genderId, name)
    return {'result': result}

@app.route('/baisedwordupdate', methods=["POST"])
def baisedwordupdate():
    data = request.get_json()
    id = int(data["updates"][0]["value"])  # Ensure ID is passed as integer
    word = data["updates"][1]["value"]
    result = diadb.biased_word_update(id, word)
    return {'result': result}

@app.route('/baisedworddelete', methods=["POST"])
def baisedworddelete():
    data = request.get_json()
    id = int(data["updates"][0]["value"])  # Ensure ID is passed as integer
    result = diadb.biased_word_delete(id)
    return {'result': result}

@app.route('/readExcel', methods=["GET"])
def readExcel():
    df = pd.read_excel('E:/Projects/DIAWorkspace/DIA/uploads/gender_biased_words.xlsx', sheet_name='Words', usecols="A:B")
    gender_keywords = df['Words'].tolist()
    gender_list = df['Gender'].tolist()
    count = 0
    exceldata = []
    for baisedword_result in gender_keywords:
        dict = {"Gender": str(gender_list[count]), "Words": gender_keywords[count]}
        count += 1
        exceldata.append(dict)
    return {'excel_data': exceldata}

if __name__ == '__main__':
    app.run(debug=True)
