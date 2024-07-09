import requests
from bs4 import BeautifulSoup
import re
import spacy
from spacy.matcher import Matcher
from io import BytesIO
from PIL import Image, ImageOps, UnidentifiedImageError
import pytesseract
import xml.etree.ElementTree as ET
import pandas as pd
import os
from urllib.parse import urljoin

# Initialize spacy model and matcher
nlp = spacy.load("en_core_web_sm")
matcher = Matcher(nlp.vocab)

# Load gender-biased terms
def read_gender_terms(file_path):
    df = pd.read_excel(file_path)
    gender_terms = df['terms'].tolist()
    return [[{"TEXT": {"REGEX": f"(?i)^{term}$"}}] for term in gender_terms]

uploads_folder = "uploads"
gender_terms_file = os.path.join(uploads_folder, "gender_biased_words.xlsx")
gender_terms = read_gender_terms(gender_terms_file)
matcher.add("GENDER_TERMS", gender_terms)

# Define geo, race, and ethnicity terms
geo_race_ethnicity_terms = [{"ENT_TYPE": "GPE"}, {"ENT_TYPE": "LOC"}, {"ENT_TYPE": "NORP"}]
geo_race_ethnicity_matcher = Matcher(nlp.vocab)
geo_race_ethnicity_matcher.add("GEO_RACE_ETHNICITY_TERMS", [geo_race_ethnicity_terms])

def extract_entities_from_text(text):
    doc = nlp(text)
    gender_bias_entities = {}
    geography_entities = {}
    race_ethnicity_entities = {}

    for sent in doc.sents:
        gender_matches = matcher(nlp(sent.text))
        if gender_matches:
            for match_id, start, end in gender_matches:
                term = sent[start:end].text
                if term not in gender_bias_entities:
                    gender_bias_entities[term] = []
                gender_bias_entities[term].append(sent.text)
        for ent in sent.ents:
            if ent.label_ in ["GPE", "LOC"]:
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
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        if not image_url.startswith(('http://', 'https://')):
            image_url = urljoin(base_url, image_url)
        if not is_image(image_url):
            return ""
        response = requests.get(image_url, headers=headers)
        if response.status_code == 200:
            img = Image.open(BytesIO(response.content))
            preprocessed_img = preprocess_image_for_ocr(img)
            text = pytesseract.image_to_string(preprocessed_img)
            return text.strip()
        return ""
    except Exception as e:
        return ""

def extract_text_from_svg(base_url, svg_url):
    try:
        if not svg_url.startswith(('http://', 'https://')):
            svg_url = urljoin(base_url, svg_url)
        response = requests.get(svg_url)
        if response.status_code == 200:
            root = ET.fromstring(response.content)
            text_elements = root.findall('.//{http://www.w3.org/2000/svg}text')
            text = ' '.join([elem.text for elem in text_elements if elem.text])
            return text.strip()
        return ""
    except Exception as e:
        return ""

def web_scrape_and_extract_entities(url):
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        main_text = " ".join([p.text for p in soup.find_all('p')])
        alt_texts_with_src = [(img.get('alt'), img.get('src')) for img in soup.find_all('img') if img.get('alt')]
        alt_texts = " ".join([alt for alt, src in alt_texts_with_src])
        ocr_texts_with_src = [(extract_text_from_image(url, img.get('src')), img.get('src')) for img in soup.find_all('img') if img.get('src')]
        ocr_texts = " ".join([ocr for ocr, src in ocr_texts_with_src if ocr])
        svg_texts_with_src = [(extract_text_from_svg(url, img.get('src')), img.get('src')) for img in soup.find_all('img') if img.get('src') and img.get('src').lower().endswith('.svg')]
        svg_texts = " ".join([svg for svg, src in svg_texts_with_src if svg])

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
    return None
