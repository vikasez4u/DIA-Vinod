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
import Image_Mode_Race_colour as imageMode
import Geographical_Entity_Extractor as geoExtractor
from flask import Flask, render_template, request, session
import pandas as pd
import bleach
from pexecute.thread import ThreadLoom
import db as diadb
from datetime import datetime

# Set up Tesseract OCR executable path
pytesseract.pytesseract_cmd = "C:\\Program Files\\Tesseract-OCR\\tesseract.exe"

# Initialize Flask app
app = Flask(__name__)
app.secret_key = 'Digital Inclusivity Auditor'


def fetch_url_content(url):
  try:
    response = requests.get(url)
    if response.status_code == 401:
      print(f"Skipping page {url}: Authentication required.")
      return None
    response.raise_for_status()  # Raises an HTTPError for bad responses (4xx and 5xx)
    return response.content
  except RequestException as e:
    print(f"Error occurred while retrieving the web page: {e}")
    return None


def extract_text_from_html(content):
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


def extract_text_from_url(url):
  content = fetch_url_content(url)
  if content:
    return extract_text_from_html(content)
  return None


def extract_alt_text_from_url(url):
  content = fetch_url_content(url)
  if not content:
    return []

  soup = BeautifulSoup(content, 'html.parser')
  alt_texts = [(img.get('alt'), img.get('src')) for img in soup.find_all('img') if img.get('alt')]
  return alt_texts


def process_image(image_url, base_url, transaction_id):
  try:
    image_url = urljoin(base_url, image_url)
    response = requests.get(image_url)
    response.raise_for_status()

    # Determine the image format
    _, ext = os.path.splitext(image_url)
    ext = ext.lower()

    if ext == '.svg':
      # Handle SVG by converting it to PNG
      text = process_svg_image(response.content)
    else:
      text = process_raster_image(response.content)

    if text is None:
      text = ""  # Set to empty string if no text was extracted

    return text

  except (requests.exceptions.RequestException, OSError, UnidentifiedImageError) as e:
    print(f"Error processing image {image_url}: {str(e)}")
    return ""  # Return an empty string if there's an error


def process_raster_image(image_content):
  try:
    image = Image.open(BytesIO(image_content))
    text = pytesseract.image_to_string(image)
    return text
  except UnidentifiedImageError as e:
    print(f"Unidentified image error: {str(e)}")
    return None


def process_svg_image(svg_content):
  try:
    # Convert SVG to PNG using cairosvg
    png_image = cairosvg.svg2png(bytestring=svg_content)
    image = Image.open(BytesIO(png_image))
    text = pytesseract.image_to_string(image)
    return text
  except Exception as e:
    print(f"Error processing SVG image: {str(e)}")
    return None


def load_gender_biased_words():
  try:
    df = pd.read_excel('./uploads/gender_biased_words.xlsx', sheet_name='Words', usecols="A:B")
  except FileNotFoundError as e:
    print(f"Error: {e}. Ensure that the file exists at the specified path.")
    return []

  gender_keywords = df['Words'].tolist()
  gender_list = df['Gender'].tolist()
  mapGB = [f"{word}:{gender_list[i]}" for i, word in enumerate(gender_keywords)]

  with app.app_context():
    diadb.create_table('Biased_Words')
    baisedword_results = diadb.baisedwordresult()

  for baisedword_result in baisedword_results:
    word = baisedword_result[1]
    mapGB.append(f"{word}:{baisedword_result[0]}")
    gender_keywords.append(word)

  return list(dict.fromkeys(gender_keywords)), list(dict.fromkeys(mapGB))


def detect_biased_sentences(text, keyword_list, table_name, transaction_id, source, image_link=None):
  if not isinstance(text, str):  # Ensure the input is a string
    print(f"Expected a string for text, but got {type(text)}")
    return [], []

  if not text.strip():
    print("No text found to process.")
    return [], []

  sentences = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s', text)
  biased_sentences = []
  biased_words = []

  with app.app_context():
    diadb.create_table(table_name)

  for sentence in sentences:
    sentence = sentence.lower().strip()
    words = re.findall(r'\b\w+\b', sentence)
    for i, word in enumerate(words):
      if word in keyword_list:
        trimmed_sentence = ' '.join(words[max(0, i - 5):min(i + 6, len(words))])
        highlighted_sentence = re.sub(r'\b' + re.escape(word) + r'\b', r'<span class="wordcolor">\g<0></span>',
                                      trimmed_sentence, flags=re.IGNORECASE)
        biased_sentences.append(highlighted_sentence)
        biased_words.append(word)

        # Debugging: Print before insertion
        print(f"Found biased word '{word}' in sentence '{sentence}'. Inserting into {table_name}.")

        try:
          if image_link:
            diadb.insert_biased_img_result(transaction_id, source, 'Image', highlighted_sentence, word, image_link)
          else:
            diadb.insert_biased_result(transaction_id, source, 'Text', highlighted_sentence, word, image_link)
          print(f"Insert into {table_name} successful for word '{word}' and sentence '{highlighted_sentence}'.")
        except Exception as e:
          print(f"Failed to insert into {table_name}: {e}")
        break

  return biased_sentences, biased_words


def detect_biased_sentences_in_alt_text(alt_texts, keyword_list, transaction_id):
  for alt_text, image_link in alt_texts:
    print(f"Processing alt text '{alt_text}' from image '{image_link}'.")
    try:
      detect_biased_sentences(alt_text, keyword_list, 'biased_alt_Text_results', transaction_id, 'alt_text', image_link)
      print(f"Insert into biased_alt_Text_results successful for alt text '{alt_text}' and image '{image_link}'.")
    except Exception as e:
      print(f"Failed to insert alt text into biased_alt_Text_results: {e}")


def detect_geo_bias(text, transaction_id, source):
  if not isinstance(text, str):
    print(f"Expected a string for text, but got {type(text)}")
    return []

  countries, valid_cities = geoExtractor.process_geographical_entities(text)
  with app.app_context():
    for city in valid_cities:
      diadb.insert_geo_bias_result(transaction_id, source, city, None)
    for country in countries:
      diadb.insert_geo_bias_result(transaction_id, source, None, country)


def extract_text_from_images(url, transaction_id):
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
    if text:  # Ensure text is not None or empty
      # Detect gender-biased sentences from image text
      sentences, words = detect_biased_sentences(text, keyword_list, 'biased_img_results', transaction_id,
                                                 source='image', image_link=image_url)
      biased_sentences.extend(sentences)
      biased_words.extend(words)
      image_links.append(image_url)

      # Detect geographical bias from image text
      detect_geo_bias(text, transaction_id, source='image')

  return biased_sentences, biased_words, image_links


diadb.init_db(app)


@app.route('/')
@app.route('/home')
@app.route('/dia/')
def home():
  # Create tables as needed
  diadb.create_table('biased_results')
  diadb.create_table('Image_Txt_Results')
  diadb.create_table('biased_text_results')
  diadb.create_table('biased_alt_Text_results')
  diadb.create_table('biased_img_results')
  diadb.create_table('geographical_bias')
  diadb.create_table('Biased_Words')
  return render_template('index.html')


@app.route('/output', methods=['POST', 'GET'])
def output():
  # Initialize variables to avoid reference errors
  total_biased_text = total_biased_alt_text = total_biased_img_results = 0
  text_results_tr_Gender_Count = alt_text_results_tr_Gender_Count = img_text_results_tr_Gender_Count = []

  if 'transaction_id' in globals():
    total_biased_text, total_biased_alt_text, total_biased_img_results, text_results_tr_Gender_Count, alt_text_results_tr_Gender_Count, img_text_results_tr_Gender_Count = diadb.textsummaryresult(
      transaction_id)

  # Fetch geographical bias results
  geo_results = diadb.nativeQuery(
    f'SELECT * FROM biased_text_results WHERE result_type="GeoBias" AND transaction_id = "{transaction_id}"')

  return render_template('output.html',
                         total_biased_text=total_biased_text,
                         total_biased_alt_text=total_biased_alt_text,
                         total_biased_img_results=total_biased_img_results,
                         text_results_tr_Gender_Count=text_results_tr_Gender_Count,
                         alt_text_results_tr_Gender_Count=alt_text_results_tr_Gender_Count,
                         img_text_results_tr_Gender_Count=img_text_results_tr_Gender_Count,
                         geo_results=geo_results)


@app.route('/imageOp')
def imageop():
  image_results = image_results_tr = []  # Initialize variables to avoid reference errors
  return render_template('imageOp.html', image_results=image_results, image_results_tr=image_results_tr)


@app.route('/parallelexec')
def parallelexec():
  biased_txt_results = biased_alt_results = biased_img_results = image_biased_results = []  # Initialize variables
  return render_template('parallelexec.html', biased_txt_results=txt_results, biased_alt_results=alt_results,
                         biased_img_results=txt_img_results, image_biased_results=image_results)


@app.route('/result', methods=['POST', 'GET'])
def result():
  global transaction_id
  global txt_results, alt_results, txt_img_results, image_results

  transaction_id = datetime.now().strftime("%Y%m%d%H%M%S")

  # Initialize the results to avoid reference errors
  txt_results = alt_results = txt_img_results = image_results = []

  if request.method == "POST":
    data = request.get_json()
    url = data["updates"][0]["value"]
    text_mode = data["updates"][1].get("value", False)
    image_mode = data["updates"][2].get("value", False)
    geo_mode = data.get("geo_mode", False)

    if text_mode and image_mode:
      loom = ThreadLoom(max_runner_cap=2)
      loom.add_function(run_text_analysis_with_context, [url, transaction_id], {})
      loom.add_function(run_image_analysis_with_context, [url], {})
      parllelexecresult = loom.execute()

      if parllelexecresult and len(parllelexecresult) > 0 and parllelexecresult[0]:
        output = parllelexecresult[0].get('output')
        if output:
          txt_results, alt_results, txt_img_results = output
        image_results = parllelexecresult[1].get('output', []) if parllelexecresult[1] else []
        return {
          "file": "parallelexec",
          "txt_results": txt_results,
          "alt_results": alt_results,
          "txt_img_results": txt_img_results,
          "image_results": image_results
        }
      else:
        print("Parallel execution did not return results or returned None.")

    elif text_mode:
      txt_results, alt_results, txt_img_results = run_text_analysis_with_context(url, transaction_id)
      return {
        "file": "Text",
        "txt_results": txt_results,
        "alt_results": alt_results,
        "txt_img_results": txt_img_results
      }

    elif image_mode:
      image_results = run_image_analysis_with_context(url)
      return {
        "file": "Image",
        "image_results": image_results
      }

    elif geo_mode:
      geo_entities = geoExtractor.process_geographical_entities(url, transaction_id)
      return {"geo_entities": geo_entities}

  return {}


def run_text_analysis_with_context(url, transaction_id):
  return run_with_app_context(text_analysis, url=url, transaction_id=transaction_id)


def run_image_analysis_with_context(url):
  return run_with_app_context(imageMode.main, url=url)


def run_with_app_context(func, **kwargs):
  with app.app_context():
    return func(**kwargs)


@app.route('/text', methods=['POST'])
def text_analysis(url, transaction_id):
  text_content = extract_text_from_url(url)

  # Gender-biased sentences detection
  txt_results, _ = detect_biased_sentences(text_content, keyword_list, 'biased_text_results', transaction_id,
                                           source='text')

  # Geographical bias detection
  detect_geo_bias(text_content, transaction_id, source='text')

  # Alt text analysis
  alt_texts = extract_alt_text_from_url(url)
  alt_results, _ = detect_biased_sentences(' '.join([alt[0] for alt in alt_texts]), keyword_list,
                                           'biased_alt_Text_results', transaction_id, source='alt_text')
  detect_geo_bias(' '.join([alt[0] for alt in alt_texts]), transaction_id, source='alt_text')

  # Image analysis
  img_results = extract_text_from_images(url, transaction_id)

  return txt_results, alt_results, img_results


@app.route("/form", methods=["POST", "GET"])
def form_page():
  return render_template("index.html")


@app.route('/index', methods=["POST", "GET"])
def index():
  return render_template("index.html")


@app.teardown_appcontext
def close_database_connection(exception=None):
  diadb.close_db(exception)


@app.route('/genderresults', methods=["GET"])
def genderresults():
  gender_results = diadb.genderresult()
  return {"genderresults": [{"id": str(result[0]), "GenderName": result[1]} for result in gender_results]}


@app.route('/gendersave', methods=["POST"])
def gendersave():
  data = request.get_json()
  name = data["updates"][0]["value"]
  result = diadb.gendersave(name)
  return {'result': result}


@app.route('/genderupdate', methods=["POST"])
def genderupdate():
  data = request.get_json()
  id = data["updates"][0]["value"]
  name = data["updates"][1]["value"]
  result = diadb.genderupdate(id, name)
  return {'result': result}


@app.route('/genderdelete', methods=["POST"])
def genderdelete():
  data = request.get_json()
  id = data["updates"][0]["value"]
  result = diadb.genderdelete(id)
  return {'result': result}


@app.route('/baisedwordresults', methods=["GET"])
def baisedwordresults():
  baisedword_results = diadb.baisedwordresult()
  return {
    'baisedword_results': [{"GenderName": str(result[0]), "BaisedWord": result[1], "id": str(result[2])} for result in
                           baisedword_results]}


@app.route('/baisedwordsave', methods=["POST"])
def baisedwordsave():
  data = request.get_json()
  name = data["updates"][0]["value"]
  genderId = data["updates"][1]["value"]
  result = diadb.baisedwordsave(genderId, name)
  return {'result': result}


@app.route('/baisedwordupdate', methods=["POST"])
def baisedwordupdate():
  data = request.get_json()
  id = data["updates"][0]["value"]
  word = data["updates"][1]["value"]
  result = diadb.baisedwordupdate(id, word)
  return {'result': result}


@app.route('/baisedworddelete', methods=["POST"])
def baisedworddelete():
  data = request.get_json()
  id = data["updates"][0]["value"]
  result = diadb.baisedworddelete(id)
  return {'result': result}


@app.route('/readExcel', methods=["GET"])
def readExcel():
  df = pd.read_excel('C:/Users/alwin/Documents/DIAWorkspace/DIA/DIA/uploads/gender_biased_words.xlsx',
                     sheet_name='Words', usecols="A:B")
  exceldata = [{"Gender": str(gender), "Words": word} for gender, word in zip(df['Gender'], df['Words'])]
  print(exceldata)
  return {'excel_data': exceldata}


if __name__ == '__main__':
  keyword_list, _ = load_gender_biased_words()
  app.run(debug=True)
