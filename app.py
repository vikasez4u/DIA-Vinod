from builtins import print

import pytesseract
import Image_Mode_Race_colour as imageMode
import Geographical_Entity_Extractor as geoExtractor
from flask import Flask, render_template, request, session
import pandas as pd
from pexecute.thread import ThreadLoom
import db as diadb
from datetime import datetime
from Text import text_analysis_results


# Set up Tesseract OCR executable path
pytesseract.pytesseract_cmd = "C:\\Program Files\\Tesseract-OCR\\tesseract.exe"

# Initialize Flask app
app = Flask(__name__)
app.secret_key = 'Digital Inclusivity Auditor'

def load_gender_biased_words():
  global mapGB
  try:
    df = pd.read_excel('./uploads/gender_biased_words.xlsx', sheet_name='Words', usecols="A:B")
  except FileNotFoundError as e:
    print(f"Error: {e}. Ensure that the file exists at the specified path.")
    return []

  gender_keywords = df['Words'].tolist()
  gender_list = df['Gender'].tolist()
  print(f'gender_keywords: {gender_keywords}\ngender_list: {gender_list}')
  mapGB = [f"{word}:{gender_list[i]}" for i, word in enumerate(gender_keywords)]
  print(f'mapGB: {mapGB}')

  with app.app_context():
    diadb.create_table('Biased_Words')
    diadb.create_table('Gender_Table')
    baisedword_results = diadb.baisedwordresult()
  print("After getting keywords from DB")
  for baisedword_result in baisedword_results:
    word = baisedword_result[1]
    mapGB.append(f"{word}:{baisedword_result[0]}")
    gender_keywords.append(word)
  gender_keywords = list(dict.fromkeys(gender_keywords))
  mapGB = list(dict.fromkeys(mapGB))
  print(f'gender_keywords: {gender_keywords}')
  print(f'mapGB: {mapGB}')
  return gender_keywords

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
  diadb.create_table('Gender_Table')
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

'''def insertgeoData(results):
  for entity in results:
    diadb.insert_geo_bias_result(
      transaction_id=transaction_id,
      source='image',
      city=entity['entity'] if entity['type'] == 'city' else None,
      country=entity['entity'] if entity['type'] == 'country' else None
    )'''
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
      loom.add_function(text_analysis_results, [url, transaction_id, keyword_list], {})
      loom.add_function(imageMode.main, [url], {})
      parllelexecresult = loom.execute()
      print(parllelexecresult)

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
      text_result = text_analysis_results(url, transaction_id, keyword_list)
      txt_results = text_result["text_bias_results"]
      txt_geo_eth = text_result["text_geo_ethnicities"]
      #insertgeoData(txt_geo_eth)
      alt_results = text_result["alt_text_results"]
      alt_txt_geo_eth = text_result["alt_text_geo_ethnicities"]
      txt_img_results = text_result["image_results"]
      txt_img_geo_eth = text_result["image_text_geo_ethnicities"]
      print(txt_geo_eth)
      print(alt_txt_geo_eth)
      print(txt_img_geo_eth)
      biased_text_results = list(zip(txt_results[1], txt_results[0]))
      biased_alt_results = list(zip(alt_results["biased_words"], alt_results["biased_sentences"], alt_results["image_links"]))
      biased_img_results = list(zip(txt_img_results["biased_words"], txt_img_results["biased_sentences"], txt_img_results["image_links"]))
      (total_biased_text, total_biased_alt_text, total_biased_img_results, text_results_Gender_Count, alt_text_results_Gender_Count,
       img_text_results_Gender_Count, overall_gender_count, total_Ethnicity_Count, total_GeoLocation_Count, text_results_Ethnicity_Count,
          alt_text_results_Ethnicity_Count, img_text_results_Ethnicity_Count, text_results_GeoLocation_Count, alt_text_results_GeoLocation_Count,
          img_text_results_GeoLocation_Count,total_Ethnicity_text, total_Ethnicity_alt_text, total_Ethnicity_img_text, total_GeoLocation_text,
          total_GeoLocation_alt_text, total_GeoLocation_img_text) = diadb.textsummaryresult(transaction_id)

      # Create a dictionary to map words to gender
      word_to_gender = {}
      for entry in mapGB:
        word, gender = entry.split(':')
        word_to_gender[word] = gender

      # Create a dictionary to hold the total counts for each gender
      gender_counts = {'Male': 0, 'Female': 0}

      # Iterate through all the results and sum the counts based on gender
      for word, count in overall_gender_count:
        gender = word_to_gender.get(word)
        if gender:
          gender_counts[gender] += count

      # Final result
      overall_count = list(gender_counts.items())
      #print(overall_count)

      #Create a dictionary to hold the Text Model run counts for each Text type result
      textmodel_counts = [('Text Results', total_biased_text), ('Alt Text Results', total_biased_alt_text),
                          ('Image Text Results', total_biased_img_results)]
      #print(textmodel_counts)

      return {
        "file": "Text",
        "txt_results": biased_text_results,
        "alt_results": biased_alt_results,
        "txt_img_results": biased_img_results,
        "total_biased_text": total_biased_text, "total_biased_alt_text": total_biased_alt_text,
        "total_biased_img_results": total_biased_img_results,
        "text_results_Gender_Count": text_results_Gender_Count,
        "alt_text_results_Gender_Count": alt_text_results_Gender_Count,
        "img_text_results_Gender_Count": img_text_results_Gender_Count,
        "overall_gender_count": overall_count,
        "textmodel_counts": textmodel_counts,
        "total_Ethnicity_Count": total_Ethnicity_Count,
        "total_GeoLocation_Count": total_GeoLocation_Count,
        "text_results_Ethnicity_Count": text_results_Ethnicity_Count,
        "alt_text_results_Ethnicity_Count": alt_text_results_Ethnicity_Count,
        "img_text_results_Ethnicity_Count": img_text_results_Ethnicity_Count,
        "text_results_GeoLocation_Count" : text_results_GeoLocation_Count,
        "alt_text_results_GeoLocation_Count": alt_text_results_GeoLocation_Count,
        "img_text_results_GeoLocation_Count": img_text_results_GeoLocation_Count,
        "total_Ethnicity_text": total_Ethnicity_text,
        "total_Ethnicity_alt_text": total_Ethnicity_alt_text,
        "total_Ethnicity_img_text": total_Ethnicity_img_text,
        "total_GeoLocation_text": total_GeoLocation_text,
        "total_GeoLocation_alt_text": total_GeoLocation_alt_text,
        "total_GeoLocation_img_text": total_GeoLocation_img_text
      }

    elif image_mode:
      image_results = imageMode.main(url)
      image_results_Count, image_results_Gender_Count, image_results_Confidence_Count, image_results_Skin_Color_Count, image_results_Race_Count = diadb.imageSummaryResults(transaction_id)
      return {
        "file": "Image",
        "image_results": image_results,
        "image_results_Count": image_results_Count,
        "image_results_Gender_Count": image_results_Gender_Count,
        "image_results_Confidence_Count": image_results_Confidence_Count,
        "image_results_Skin_Color_Count": image_results_Skin_Color_Count,
        "image_results_Race_Count": image_results_Race_Count
      }

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

  txt_results, alt_results, img_results = text_analysis_results(url, transaction_id,keyword_list)
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


'''@app.route('/readExcel', methods=["GET"])
def readExcel():
  df = pd.read_excel('./uploads/gender_biased_words.xlsx', sheet_name='Words', usecols="A:B")
  exceldata = [{"Gender": str(gender), "Words": word} for gender, word in zip(df['Gender'], df['Words'])]
  print(exceldata)
  return {'excel_data': exceldata}'''


if __name__ == '__main__':
  keyword_list = load_gender_biased_words()
  app.run(debug=True)
