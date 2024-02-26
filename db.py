import sqlite3
from datetime import datetime
from flask import Flask, render_template, g
import bleach

DATABASE = 'DIA.db'
db = Flask(__name__)

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        print('Hitting DB Connection')
        db = g._database = sqlite3.connect(DATABASE)
    return db

def create_table(table_name):
    db = get_db()
    cursor = db.cursor()
    if table_name == 'Image_Txt_Results':
      cursor.execute(f'''
                  CREATE TABLE IF NOT EXISTS {table_name} (
                      id INTEGER PRIMARY KEY AUTOINCREMENT,
                      transaction_id Integer,
                      result_type TEXT,
                      male_count Integer,
                      female_count Integer,
                      confidence Integer,
                      max_skin_key TEXT,
                      max_race_key TEXT,
                      image_link TEXT,
                      create_date TEXT
                  )
              ''')
    else:
        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS {table_name} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                transaction_id Integer,
                result_type TEXT,
                sentence TEXT,
                word TEXT,
                image_link TEXT,
                create_date TEXT
            )
        ''')


def saveImage(table_name, transaction_id, result_type, male_count, female_count,
              confidence, max_skin_key, max_race_key, image_link):
  db = get_db()
  cursor = db.cursor()
  try:
    create_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute(f''' INSERT INTO {table_name} (transaction_id,result_type, male_count, female_count, confidence,
     max_skin_key, max_race_key, image_link, create_date)
              VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
          ''', (transaction_id, result_type, male_count, female_count,
                confidence, max_skin_key, max_race_key, image_link, create_date))
    db.commit()
  except Exception as e:
    print(f"Error inserting into the database: {e}")

def insert_result(table_name: any, transaction_id: any, result_type: any, sentence: any,
             word: any, image_link: any):
    db = get_db()
    cursor = db.cursor()
    try:
      create_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
      cleaned_sentence = bleach.clean(sentence, tags=[], strip=True)
      cursor.execute(f'''
                   INSERT INTO {table_name} (transaction_id,result_type, sentence, word, image_link, create_date)
                   VALUES (?, ?, ?, ?, ?, ?)
               ''', (transaction_id,result_type, cleaned_sentence, word, image_link, create_date))
      db.commit()
    except Exception as e:
        print(f"Error inserting into the database: {e}")

def close_db(error):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def nativeQuery(query):
  db = get_db()
  cursor = db.cursor()
  # Fetch data from the biased_Text_results table
  cursor.execute(query)
  text_results = cursor.fetchall()
  return text_results

@db.route('/show_db')
def show_db():

  text_results = nativeQuery('SELECT * FROM biased_Text_results')
  alt_text_results = nativeQuery('SELECT * FROM biased_alt_Text_results')
  img_results = nativeQuery('SELECT * FROM biased_img_results')

  # Calculate summary statistics
  total_biased_text = len(text_results)
  total_biased_alt_text = len(alt_text_results)
  total_biased_img_results = len(img_results)

  # Extract unique words from biased sentences, alt texts, and image results
  unique_words_text = set(word for _, _, content, _, _, _, _ in text_results if content for word in content.split())
  unique_words_alt_text = set(
    word for _, _, alt_text, _, _, _, _ in alt_text_results if alt_text for word in alt_text.split())
  unique_words_img_results = set(word for _, _, content, _, _, _, _ in img_results if content for word in content.split())

  # Calculate unique word counts
  unique_word_count_text = len(unique_words_text)
  unique_word_count_alt_text = len(unique_words_alt_text)
  unique_word_count_img_results = len(unique_words_img_results)

  return render_template('show_db.html', text_results=text_results, alt_text_results=alt_text_results,
                         img_results=img_results, total_biased_text=total_biased_text,
                         total_biased_alt_text=total_biased_alt_text,
                         total_biased_img_results=total_biased_img_results,
                         unique_word_count_text=unique_word_count_text,
                         unique_word_count_alt_text=unique_word_count_alt_text,
                         unique_word_count_img_results=unique_word_count_img_results)

  # return render_template('show_db.html', text_results=text_results, alt_text_results=alt_text_results, img_results=img_results)

def textsummaryresult():

  text_results_tr = nativeQuery('SELECT * FROM biased_Text_results WHERE transaction_id = (SELECT Max(transaction_id) FROM BIASED_TEXT_RESULTS)')
  alt_text_results = nativeQuery('SELECT * FROM biased_alt_Text_results WHERE transaction_id = (SELECT Max(transaction_id) FROM biased_alt_Text_results)')
  img_results = nativeQuery('SELECT * FROM biased_img_results WHERE transaction_id = (SELECT Max(transaction_id) FROM biased_img_results)')

  text_results_tr_Gender_Count = nativeQuery(
    'SELECT DISTINCT(WORD), count(*) FROM BIASED_TEXT_RESULTS WHERE TRANSACTION_ID = (SELECT MAX(TRANSACTION_ID) FROM BIASED_TEXT_RESULTS) group by word')

  alt_text_results_tr_Gender_Count = nativeQuery(
    'SELECT DISTINCT(WORD), count(*) FROM biased_alt_Text_results WHERE TRANSACTION_ID = (SELECT MAX(TRANSACTION_ID) FROM biased_alt_Text_results) group by word')

  img_text_results_tr_Gender_Count = nativeQuery(
    'SELECT DISTINCT(WORD), count(*) FROM biased_img_results WHERE TRANSACTION_ID = (SELECT MAX(TRANSACTION_ID) FROM biased_img_results) group by word')


  total_biased_text = len(text_results_tr)
  total_biased_alt_text = len(alt_text_results)
  total_biased_img_results = len(img_results)

  return total_biased_text, total_biased_alt_text, total_biased_img_results,text_results_tr_Gender_Count,alt_text_results_tr_Gender_Count, img_text_results_tr_Gender_Count

def imagesummaryresult():

  image_results_tr = nativeQuery('SELECT COUNT(MALE_COUNT),COUNT(FEMALE_COUNT) FROM Image_Txt_Results WHERE transaction_id = (SELECT Max(transaction_id) FROM Image_Txt_Results)')
  print(image_results_tr)
  return image_results_tr
if __name__ == "__main__":
    db.run(debug=True, port=3000)
