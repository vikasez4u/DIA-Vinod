import os
import requests
from bs4 import BeautifulSoup
import spacy
from spacy.matcher import Matcher
import pytesseract
from PIL import Image, UnidentifiedImageError, ImageOps
from io import BytesIO
from urllib.parse import urljoin
import pandas as pd
import xml.etree.ElementTree as ET

# Load the spacy model
nlp = spacy.load("en_core_web_sm")

# Function to read gender-biased words from an Excel file
def read_gender_terms(file_path):
    df = pd.read_excel(file_path)
    gender_terms = df['terms'].tolist()
    return [[{"TEXT": {"REGEX": f"(?i)^{term}$"}}] for term in gender_terms]  # Case-insensitive terms

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
    # Convert the image to grayscale
    gray_image = ImageOps.grayscale(image)
    # Invert the image
    inverted_image = ImageOps.invert(gray_image)
    return inverted_image

def extract_text_from_image(base_url, image_url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
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

def web_scrape_and_extract_entities(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
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

# Example usage
#url = 'https://en.wikipedia.org/wiki/Demographics_of_the_United_States'

url = 'https://www.goodgoodgood.co/articles/quotes-to-empower-women'
data = web_scrape_and_extract_entities(url)

if data:
    print("Main Text Analysis:")
    print_entities(data["main_text_entities"]["geography_entities"], "Geography")
    print_entities(data["main_text_entities"]["race_ethnicity_entities"], "Race and Ethnicity")
    print_entities(data["main_text_entities"]["gender_bias_entities"], "Gender Bias")

    print("\nAlt Text Analysis:")
    print_text_entities([data["alt_text_entities"]], data["alt_texts_with_src"], "Alt")

    print("\nOCR Text Analysis:")
    print_text_entities(data["ocr_text_entities"], data["ocr_texts_with_src"], "OCR")

    print("\nSVG Text Analysis:")
    print_text_entities(data["svg_text_entities"], data["svg_texts_with_src"], "SVG")

    print("\nSummary:")
    main_total_sentences = data["main_text_entities"]["total_sentences"]
    main_mapped_sentences_geography = data["main_text_entities"]["mapped_sentences_geography"]
    main_mapped_sentences_race_ethnicity = data["main_text_entities"]["mapped_sentences_race_ethnicity"]
    main_mapped_sentences_gender_bias = data["main_text_entities"]["mapped_sentences_gender_bias"]

    print(f"Main Text: {main_total_sentences} total sentences")
    print(f"Geography: {main_mapped_sentences_geography} mapped sentences")
    print(f"Race and Ethnicity: {main_mapped_sentences_race_ethnicity} mapped sentences")
    print(f"Gender Bias: {main_mapped_sentences_gender_bias} mapped sentences")

    alt_total_sentences = data["alt_text_entities"]["total_sentences"]
    alt_mapped_sentences_geography = data["alt_text_entities"]["mapped_sentences_geography"]
    alt_mapped_sentences_race_ethnicity = data["alt_text_entities"]["mapped_sentences_race_ethnicity"]
    alt_mapped_sentences_gender_bias = data["alt_text_entities"]["mapped_sentences_gender_bias"]

    print(f"\nAlt Text: {alt_total_sentences} total sentences")
    print(f"Geography: {alt_mapped_sentences_geography} mapped sentences")
    print(f"Race and Ethnicity: {alt_mapped_sentences_race_ethnicity} mapped sentences")
    print(f"Gender Bias: {alt_mapped_sentences_gender_bias} mapped sentences")

    ocr_total_sentences = sum(ent["total_sentences"] for ent in data["ocr_text_entities"])
    ocr_mapped_sentences_geography = sum(ent["mapped_sentences_geography"] for ent in data["ocr_text_entities"])
    ocr_mapped_sentences_race_ethnicity = sum(ent["mapped_sentences_race_ethnicity"] for ent in data["ocr_text_entities"])
    ocr_mapped_sentences_gender_bias = sum(ent["mapped_sentences_gender_bias"] for ent in data["ocr_text_entities"])

    print(f"\nOCR Text: {ocr_total_sentences} total sentences")
    print(f"Geography: {ocr_mapped_sentences_geography} mapped sentences")
    print(f"Race and Ethnicity: {ocr_mapped_sentences_race_ethnicity} mapped sentences")
    print(f"Gender Bias: {ocr_mapped_sentences_gender_bias} mapped sentences")
