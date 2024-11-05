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
        if response.status_code == 401:
            print(f"Skipping page {url}: Authentication required.")
            return None
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
        if content:
            soup = BeautifulSoup(content, 'html.parser')
            return soup.get_text()
        else:
            print("Received empty content, skipping processing.")
            return None
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
    if not isinstance(text, str):
        print(f"Expected a string for text, but got {type(text)}")
        return [], []

    if not text.strip():
        print("No text found to process.")
        return [], []

    sentences = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s', text)
    biased_sentences = []
    biased_words = []

    diadb.create_table(table_name)

    for sentence in sentences:
        sentence = sentence.lower().strip()
        words = re.findall(r'\b\w+\b', sentence)
        for i, word in enumerate(words):
            if word in keyword_list:
                trimmed_sentence = ' '.join(words[max(0, i - 5):min(i + 6, len(words))])
                highlighted_sentence = re.sub(r'\b' + re.escape(word) + r'\b', r'<span class="wordcolor">\g<0></span>', trimmed_sentence, flags=re.IGNORECASE)
                biased_sentences.append(highlighted_sentence)
                biased_words.append(word)

                print(f"Found biased word '{word}' in sentence '{sentence}'. Inserting into {table_name}.")

                try:
                    diadb.insert_biased_result(table_name, transaction_id, 'Text', highlighted_sentence, word, image_link)
                    print(f"Insert into {table_name} successful for word '{word}' and sentence '{highlighted_sentence}'.")
                except Exception as e:
                    print(f"Failed to insert into {table_name}: {e}")
                break
    return biased_sentences, biased_words

def detect_geo_bias(text, transaction_id, source):
    """
    Detects geographical bias by finding country and city names in text, 
    then logs results to a database.
    
    Parameters:
        text (str): Text to search for geographical entities.
        transaction_id (int): Unique identifier for the transaction.
        source (str): Source identifier for the data.
        
    Returns:
        list: List of detected geographic entities (countries and cities).
    """
    if not isinstance(text, str):
        print(f"Expected a string for text, but got {type(text)}")
        return []

    countries, valid_cities = geoExtractor.process_geographical_entities(text)
    return countries, valid_cities

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
        tuple: Lists of biased alt text sentences, words, and associated image links.
    """
    alt_sentences, alt_words, alt_link = [], [], []
    for alt_text, image_link in alt_texts:
        print(f"Processing alt text '{alt_text}' from image '{image_link}'.")
        try:
            sentence, word = detect_biased_sentences(alt_text, keyword_list, 'biased_alt_Text_results', transaction_id, image_link)
            if sentence and word:
                alt_sentences.append(sentence)
                alt_words.append(word)
                alt_link.append(image_link)
            print(f"Insert into biased_alt_Text_results successful for alt text '{alt_text}' and image '{image_link}'.")
        except Exception as e:
            print(f"Failed to insert alt text into biased_alt_Text_results: {e}")
    return alt_sentences, alt_words, alt_link

def extract_text_from_images(url, transaction_id, keyword_list):
    """
    Extracts text from images on a webpage and detects bias in extracted text.
    
    Parameters:
        url (str): URL of the page containing images.
        transaction_id (int): Unique transaction identifier for the database.
        keyword_list (list): Keywords to detect bias.
        
    Returns:
        tuple: Lists of biased sentences, biased words, and image links.
    """
    content = fetch_url_content(url)
    if not content:
        return [], [], []

    soup = BeautifulSoup(content, 'html.parser')
    image_urls = [img['src'] for img in soup.find_all('img')]

    biased_sentences = []
    biased_words = []
    image_links = []

    for image_url in image_urls:
        text = process_image(image_url, url, transaction_id)
        if text:
            sentences, words = detect_biased_sentences(text, keyword_list, 'biased_img_results', transaction_id, image_link=image_url)
            biased_sentences.extend(sentences)
            biased_words.extend(words)
            image_links.append(image_url)

            detect_geo_bias(text, transaction_id, source='image')

    return biased_sentences, biased_words, image_links

def process_svg_image(svg_content):
    """
    Converts SVG image content to PNG, then extracts text using OCR.
    
    Parameters:
        svg_content (bytes): SVG image content as bytes.
        
    Returns:
        str or None: Extracted text, or None if processing fails.
    """
    try:
        png_image = cairosvg.svg2png(bytestring=svg_content)
        image = Image.open(BytesIO(png_image))
        text = pytesseract.image_to_string(image)
        return text
    except Exception as e:
        print(f"Error processing SVG image: {str(e)}")
        return None

def process_raster_image(image_content):
    """
    Extracts text from raster images using OCR.
    
    Parameters:
        image_content (bytes): Raster image content as bytes.
        
    Returns:
        str or None: Extracted text, or None if the image format is unrecognized.
    """
    try:
        image = Image.open(BytesIO(image_content))
        text = pytesseract.image_to_string(image)
        return text
    except UnidentifiedImageError as e:
        print(f"Unidentified image error: {str(e)}")
        return None


def process_image(image_url, base_url, transaction_id):
    """
    Processes an image by retrieving it from a URL, determining its format, and extracting text using OCR.
    
    This function handles both SVG and raster images. If the image is in SVG format, it is converted to PNG 
    before applying OCR to extract any text present. The function returns the extracted text or an empty 
    string if no text is found or an error occurs.
    
    Parameters:
        image_url (str): The partial or full URL of the image to process.
        base_url (str): The base URL of the website, used to resolve relative image URLs.
        transaction_id (int): A unique identifier for the transaction, used in logging and debugging.

    Returns:
        str: Extracted text from the image, or an empty string if no text was found or an error occurred.
    """
    try:
        # Combine base URL with image URL to form a full URL if necessary
        image_url = urljoin(base_url, image_url)
        
        # Request the image content
        response = requests.get(image_url)
        response.raise_for_status()  # Raise an error if the request failed

        # Determine the file extension to identify image format
        _, ext = os.path.splitext(image_url)
        ext = ext.lower()

        # Process SVG images by converting to PNG before extracting text
        if ext == '.svg':
            text = process_svg_image(response.content)
        else:
            # Process raster images directly
            text = process_raster_image(response.content)

        # Return an empty string if no text was extracted
        if text is None:
            text = ""

        return text

    except (requests.exceptions.RequestException, OSError, UnidentifiedImageError) as e:
        print(f"Error processing image {image_url}: {str(e)}")
        return ""  # Return an empty string if there's an error
