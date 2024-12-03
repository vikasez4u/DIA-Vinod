import os
import re
import requests
from bs4 import BeautifulSoup
from PIL import Image, UnidentifiedImageError
import pytesseract
from io import BytesIO
from urllib.parse import urljoin
import cairosvg  # To convert SVGs to PNGs for OCR processing
from requests import RequestException
import Geographical_Entity_Extractor as geoExtractor
import db as diadb
from app import app
import spacy
# Load spaCy's language model (you can replace 'en_core_web_sm' with a larger model if needed)
nlp = spacy.load('en_core_web_sm')
def extract_text_from_url(url):
    """
    Fetches content from a URL and extracts text from the HTML if available.

    Parameters:
        url (str): The URL of the page to retrieve content from.

    Returns:
        str or None: Extracted text from HTML content, or None if fetching fails.
    """
    content = fetch_url_content(url)
    if content:
        return extract_text_from_html(content)
    return None

def fetch_url_content(url):
    """
    Retrieves the raw content from a URL, handling authentication and errors.

    Parameters:
        url (str): The URL to retrieve content from.

    Returns:
        bytes or None: Raw content if successful, or None if an error occurs.
    """
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.content
    except RequestException as e:
        print(f"Error occurred while retrieving the web page: {e}")
        return None

def extract_text_from_html(content):
    """
    Parses HTML content to extract and return plain text.

    Parameters:
        content (bytes): The HTML content as bytes.

    Returns:
        str or None: Extracted text, or None if parsing fails.
    """
    try:
        soup = BeautifulSoup(content, 'html.parser')
        return soup.get_text()
    except Exception as e:
        print(f"Error occurred while parsing the HTML content: {e}")
        return None

def detect_biased_sentences(text, keyword_list, table_name, transaction_id, image_link=None):
    """
    Identifies biased words in text based on a list of keywords, highlights them,
    and inserts into a database table.

    Parameters:
        text (str): Text to search for biased words.
        keyword_list (list): List of keywords to detect bias.
        table_name (str): Database table name for storing results.
        transaction_id (int): Unique identifier for the database transaction.
        image_link (str, optional): URL of the associated image, if applicable.

    Returns:
        tuple: Lists of biased sentences and words found in the text.
    """
    if not isinstance(text, str) or not text.strip():
        print(f"Invalid text input: {type(text)}")
        return [], []

    sentences = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s', text)
    biased_sentences = []
    biased_words = []

    for sentence in sentences:
        sentence = sentence.lower().strip()
        words = re.findall(r'\b\w+\b', sentence)
        for i, word in enumerate(words):
            if word in keyword_list:
                trimmed_sentence = ' '.join(words[max(0, i - 5):min(i + 6, len(words))])
                highlighted_sentence = re.sub(r'\b' + re.escape(word) + r'\b', r'<span class="wordcolor">\g<0></span>', trimmed_sentence, flags=re.IGNORECASE)
                biased_sentences.append(highlighted_sentence)
                biased_words.append(word)

                print(f"Found biased word '{word}' in sentence '{sentence}'.")

                #Uncomment the following lines to enable database insertion
                try:
                  with app.app_context():
                    diadb.insert_biased_result(table_name, transaction_id, 'Text', highlighted_sentence, word, image_link)
                    print(f"Insert into {table_name} successful for word '{word}' and sentence '{highlighted_sentence}'.")
                except Exception as e:
                    print(f"Failed to insert into {table_name}: {e}")

    return biased_sentences, biased_words

import re


def detect_geo_ethnicity_bias(text, transaction_id, source, ethnicity_list=None, image_urls=None):
  """
  Detects geographical and ethnicity-related bias in text, and returns unique entities.

  Parameters:
      text (str): Text to analyze.
      transaction_id (int): Unique identifier for the transaction.
      source (str): Source identifier for the data.
      ethnicity_list (list, optional): List of ethnicity keywords to detect.
      image_urls (list, optional): List of image URLs associated with text or alt text.

  Returns:
      list: Combined list of detected entities with snippets, types, and associated image URLs.
  """
  if not isinstance(text, str):
    print(f"Expected a string for text, but got {type(text)}")
    return []

  detected_entities = []
  entity_image_map = {}

  # Map image URLs to entities if provided
  if image_urls:
    for i, url in enumerate(image_urls):
      entity_image_map[i] = url

  # Process text with spaCy
  doc = nlp(text)

  # Extract geographical entities
  for ent in doc.ents:
    if ent.label_ in {"GPE", "LOC", "NORP"}:  # NORP includes Nationalities, Religious, Political groups
      snippet = re.search(r'([^.]?\b{}\b[^.]\.)'.format(re.escape(ent.text)), text, re.IGNORECASE)
      snippet_text = snippet.group(0) if snippet else ent.text
      detected_entities.append({
        "entity": ent.text,
        "type": "Country" if ent.label_ == "GPE" else "City" if ent.label_ == "LOC" else "ethnicity",
        "snippet": snippet_text,
        "image_url": entity_image_map.get(len(detected_entities))
      })

  # Detect ethnicities from the custom list
  if ethnicity_list:
    lower_text = text.lower()
    for ethnicity in ethnicity_list:
      if ethnicity.lower() in lower_text:
        snippet = re.search(r'([^.]?\b{}\b[^.]\.)'.format(re.escape(ethnicity)), text, re.IGNORECASE)
        snippet_text = snippet.group(0) if snippet else ethnicity
        detected_entities.append({
          "entity": ethnicity,
          "type": "ethnicity",
          "snippet": snippet_text,
          "image_url": entity_image_map.get(len(detected_entities))
        })

  # Remove duplicates
  unique_entities = {f"{e['entity'].lower()}_{e['type']}": e for e in detected_entities}.values()

  try:
    with app.app_context():
      for entity in list(unique_entities):
        diadb.insert_geo_bias_result(
          transaction_id=transaction_id,
          source=source,
          city=entity['entity'] if entity['type'] == 'ethnicity' else None,
          country=entity['entity'] if entity['type'] == 'Country' else None
        )
      print("Inserted text eth geo")
  except Exception as e:
    (
      print(f"Failed to insert into geographical table: {e}"))

  return list(unique_entities)

def detect_geo_ethnicity_bias_orignal(text, transaction_id, source, ethnicity_list=None, image_urls=None):
    """
    Detects geographical entities and ethnicity-related bias in text, combining results from spaCy NER
    and a custom ethnicity list while removing duplicates.

    Parameters:
        text (str): Text to analyze.
        transaction_id (int): Unique identifier for the transaction.
        source (str): Source identifier for the data.
        ethnicity_list (list, optional): List of ethnicity keywords to detect.
        image_urls (list, optional): List of image URLs associated with text or alt text.

    Returns:
        list: Combined list of detected entities with snippets, types, and associated image URLs.
    """
    if not isinstance(text, str):
        print(f"Expected a string for text, but got {type(text)}")
        return []

    detected_entities = []
    entity_image_map = {}

    # Map image URLs to entities if provided
    if image_urls:
        for i, url in enumerate(image_urls):
            entity_image_map[i] = url

    # Process text with spaCy
    doc = nlp(text)

    # Extract geographical entities (countries, cities, geopolitical entities)
    for ent in doc.ents:
        if ent.label_ in {"GPE", "LOC", "NORP"}:  # GPE: Geopolitical Entity, LOC: Location, NORP: Nationalities/Religious/Political Groups
            match = re.search(r'([^.]*?\b{}\b[^.]*\.)'.format(re.escape(ent.text)), text, re.IGNORECASE)
            snippet = match.group(0) if match else ent.text
            detected_entities.append({
                "entity": ent.text,
                "type": ent.label_,
                "snippet": snippet,
                "image_url": entity_image_map.get(len(detected_entities))
            })

    # Detect ethnicities from the custom list
    if ethnicity_list:
        lower_text = text.lower()
        for ethnicity in ethnicity_list:
            if ethnicity.lower() in lower_text:
                match = re.search(r'([^.]*?\b{}\b[^.]*\.)'.format(re.escape(ethnicity)), text, re.IGNORECASE)
                snippet = match.group(0) if match else ethnicity
                detected_entities.append({
                    "entity": ethnicity,
                    "type": "ethnicity",
                    "snippet": snippet,
                    "image_url": entity_image_map.get(len(detected_entities))
                })

    # Remove duplicates (combine entities with similar snippets and names)
    unique_entities = {f"{e['entity'].lower()}_{e['type']}": e for e in detected_entities}.values()

    return list(unique_entities)

def detect_geo_ethnicity_bias_1(text, transaction_id, source, ethnicity_list=None, image_urls=None):
    if not isinstance(text, str):
        print(f"Expected a string for text, but got {type(text)}")
        return []

    detected_entities = []

    # Detect geographical entities
    countries, valid_cities = geoExtractor.process_geographical_entities(text)

    # Create a mapping of detected entities to image URLs
    entity_image_map = {}
    if image_urls:
        for i, url in enumerate(image_urls):
            entity_image_map[i] = url  # Simplified; make sure this is correctly indexed with your entities

    # Detect ethnicities based on provided list
    if ethnicity_list:
        lower_text = text.lower()
        for ethnicity in ethnicity_list:
            if ethnicity.lower() in lower_text:
                match = re.search(r'([^.]*?\b{}\b[^.]*\.)'.format(re.escape(ethnicity)), text, re.IGNORECASE)
                snippet = match.group(0) if match else ethnicity
                detected_entities.append({
                    "entity": ethnicity,
                    "type": "ethnicity",
                    "snippet": snippet,
                    "image_url": entity_image_map.get(len(detected_entities))  # Use the current length
                })

    # Add countries with surrounding sentence snippets
    for country in countries:
        match = re.search(r'([^.]*?\b{}\b[^.]*\.)'.format(re.escape(country)), text, re.IGNORECASE)
        snippet = match.group(0) if match else country
        detected_entities.append({
            "entity": country,
            "type": "country",
            "snippet": snippet,
            "image_url": entity_image_map.get(len(detected_entities))  # Use the current length
        })

    # Add cities with surrounding sentence snippets
    for city in valid_cities:
        match = re.search(r'([^.]*?\b{}\b[^.]*\.)'.format(re.escape(city)), text, re.IGNORECASE)
        snippet = match.group(0) if match else city
        detected_entities.append({
            "entity": city,
            "type": "city",
            "snippet": snippet,
            "image_url": entity_image_map.get(len(detected_entities))  # Use the current length
        })

    return detected_entities

def detect_geo_ethnicity_bias_1(text, transaction_id, source, ethnicity_list=None, image_urls=None):
    """
    Detects geographical and ethnicity-related bias in text, combining detected countries,
    cities, and ethnicities into a single list along with full sentence snippets.

    Parameters:
        text (str): Text to search for geographical entities and ethnicities.
        transaction_id (int): Unique identifier for the transaction.
        source (str): Source identifier for the data.
        ethnicity_list (list, optional): List of ethnicity keywords to detect.
        image_urls (list, optional): List of image URLs associated with alt texts.

    Returns:
        list: List of dictionaries with detected entities (countries, cities, ethnicities)
              and associated sentence snippets, along with their image URLs.
    """
    if not isinstance(text, str):
        print(f"Expected a string for text, but got {type(text)}")
        return []

    detected_entities = []

    # Detect geographical entities
    countries, valid_cities = geoExtractor.process_geographical_entities(text)

    # Create a mapping of detected entities to image URLs if available
    entity_image_map = {}
    if image_urls:
        # Assuming each URL corresponds to an entity, you may want to adjust this logic
        for i, url in enumerate(image_urls):
            # This is a placeholder for the logic of mapping
            # You might want to link URLs with their respective snippets or indices
            entity_image_map[i] = url

    # Detect ethnicities based on provided list
    if ethnicity_list:
        lower_text = text.lower()
        for ethnicity in ethnicity_list:
            if ethnicity.lower() in lower_text:
                match = re.search(r'([^.]*?\b{}\b[^.]*\.)'.format(re.escape(ethnicity)), text, re.IGNORECASE)
                snippet = match.group(0) if match else ethnicity
                detected_entities.append({
                    "entity": ethnicity,
                    "type": "ethnicity",
                    "snippet": snippet,
                    "image_url": entity_image_map.get(len(detected_entities) - 1)  # Try to associate URL
                })

    # Add countries with surrounding sentence snippets
    for country in countries:
        match = re.search(r'([^.]*?\b{}\b[^.]*\.)'.format(re.escape(country)), text, re.IGNORECASE)
        snippet = match.group(0) if match else country
        detected_entities.append({
            "entity": country,
            "type": "country",
            "snippet": snippet,
            "image_url": entity_image_map.get(len(detected_entities) - 1)  # Try to associate URL
        })

    # Add cities with surrounding sentence snippets
    for city in valid_cities:
        match = re.search(r'([^.]*?\b{}\b[^.]*\.)'.format(re.escape(city)), text, re.IGNORECASE)
        snippet = match.group(0) if match else city
        detected_entities.append({
            "entity": city,
            "type": "city",
            "snippet": snippet,
            "image_url": entity_image_map.get(len(detected_entities) - 1)  # Try to associate URL
        })

    return detected_entities

def extract_alt_text_from_url(url):
    """
    Extracts alt text and image sources from images on a webpage.

    Parameters:
        url (str): URL of the page to retrieve images from.

    Returns:
        list of tuples: Pairs of alt text and image source URL.
    """
    content = fetch_url_content(url)
    if not content:
        return []

    soup = BeautifulSoup(content, 'html.parser')
    alt_texts = [(img.get('alt'), img.get('src')) for img in soup.find_all('img') if img.get('alt')]
    return alt_texts

def detect_biased_sentences_in_alt_text(alt_texts, keyword_list, transaction_id):
    """
    Identifies biased words in alt text descriptions of images, highlighting and logging them.

    Parameters:
        alt_texts (list): List of (alt text, image source) pairs.
        keyword_list (list): Keywords to detect bias.
        transaction_id (int): Unique transaction identifier for the database.

    Returns:
        dict: Dictionary containing lists of biased alt text sentences, words, and associated image links.
    """
    alt_results = {
        'biased_sentences': [],
        'biased_words': [],
        'image_links': []
    }

    for alt_text, image_link in alt_texts:
        print(f"Processing alt text '{alt_text}' from image '{image_link}'.")
        sentences, words = detect_biased_sentences(alt_text, keyword_list, 'biased_alt_Text_results', transaction_id, image_link)
        if sentences and words:
            alt_results['biased_sentences'].extend(sentences)
            alt_results['biased_words'].extend(words)
            alt_results['image_links'].append(image_link)
            print(f"Insert into biased_alt_Text_results successful for alt text '{alt_text}' and image '{image_link}'.")

    return alt_results
def extract_text_from_images(url, transaction_id, keyword_list, ethnicity_list=None):
    """
    Extracts text from images on a webpage, detects bias, and returns results similar to alt text logic.

    Parameters:
        url (str): URL of the page containing images.
        transaction_id (int): Unique transaction identifier for the database.
        keyword_list (list): Keywords to detect bias.
        ethnicity_list (list, optional): List of ethnicity keywords to detect.

    Returns:
        dict: Contains lists of biased sentences, words, image links, and geographical bias results.
    """
    content = fetch_url_content(url)
    if not content:
        return {
            'biased_sentences': [],
            'biased_words': [],
            'image_links': [],
            'geo_bias_results': []
        }

    soup = BeautifulSoup(content, 'html.parser')
    image_urls = [img['src'] for img in soup.find_all('img')]

    img_results = {
        'biased_sentences': [],
        'biased_words': [],
        'image_links': [],
        'geo_bias_results': []
    }

    for image_url in image_urls:
        text = process_image(image_url, url, transaction_id)
        if text:
            # Detect biased sentences and words
            sentences, words = detect_biased_sentences(text, keyword_list, 'biased_img_results', transaction_id, image_url)
            img_results['biased_sentences'].extend(sentences)
            img_results['biased_words'].extend(words)
            img_results['image_links'].append(image_url)

            # Detect geographical and ethnicity bias
            geo_entities = detect_geo_ethnicity_bias(
                text, transaction_id, source='image', ethnicity_list=ethnicity_list, image_urls=[image_url]
            )

            # Store detected geographical entities
            img_results['geo_bias_results'].extend(geo_entities)

    return img_results

def process_image(image_url, page_url, transaction_id):
    """
    Fetches an image and extracts text using OCR.

    Parameters:
        image_url (str): URL of the image.
        page_url (str): URL of the page where the image is located.
        transaction_id (int): Unique identifier for the transaction.

    Returns:
        str or None: Extracted text from the image, or None if extraction fails.
    """
    try:
        response = requests.get(image_url)
        response.raise_for_status()

        # Determine if the image is an SVG and convert it to PNG if necessary
        if image_url.lower().endswith('.svg'):
            png_image = cairosvg.svg2png(bytestring=response.content)
            image = Image.open(BytesIO(png_image))
        else:
            image = Image.open(BytesIO(response.content))

        # Extract text using OCR
        text = pytesseract.image_to_string(image)
        print(f"Extracted text from image '{image_url}': {text}")
        return text
    except UnidentifiedImageError:
        print(f"Error: Could not identify image format for '{image_url}'.")
    except Exception as e:
        print(f"Error occurred while processing the image '{image_url}': {e}")
    return None
