import sqlite3
from datetime import datetime
from flask import Flask, render_template, g
from collections import Counter

DATABASE = 'DIA.db'
db = Flask(__name__)


def get_db():
  try:
    if 'db' not in g:
      print('Hitting DB Connection')
      g.db = sqlite3.connect(DATABASE)
      g.db.row_factory = sqlite3.Row
    return g.db
  except OSError as e:
    print(f"Error connecting to database: {e}")
    raise
def ensure_tables_exist():
    """
    Ensures all required tables exist in the database.
    """
    tables = [
        'biased_text_results',
        'biased_alt_Text_results',
        'biased_img_results',
        'geographical_bias',
        'Gender_Table',
        'Biased_Words'
    ]
    for table_name in tables:
        create_table(table_name)



def close_db(e=None):
  db = g.pop('db', None)
  if db is not None:
    db.close()


def init_db(app):
  app.teardown_appcontext(close_db)


def create_table(table_name):
  db = get_db()
  cursor = db.cursor()

  if table_name == 'biased_results':
    cursor.execute(f'''
          CREATE TABLE IF NOT EXISTS {table_name} (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              transaction_id TEXT,
              result_type TEXT,
              sentence TEXT,
              word TEXT,
              image_link TEXT,
              create_date TEXT
          )
      ''')
  elif table_name == 'Image_Txt_Results':
    cursor.execute(f'''
          CREATE TABLE IF NOT EXISTS {table_name} (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              transaction_id TEXT,
              result_type TEXT,
              male_count INTEGER,
              female_count INTEGER,
              confidence REAL,
              skin_color TEXT,
              race TEXT,
              image_link TEXT,
              create_date TEXT
          )
      ''')
  elif table_name == 'biased_text_results':
    # cursor.execute(f'''
    #               DROP TABLE IF EXISTS {table_name}
    #           ''')
    cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS {table_name} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                transaction_id TEXT,
                result_type TEXT,
                sentence TEXT,
                word TEXT,
                image_link TEXT,
                create_date TEXT
            )
        ''')
  elif table_name == 'biased_alt_Text_results':
    # cursor.execute(f'''
    #           DROP TABLE IF EXISTS {table_name}
    #       ''')
    cursor.execute(f'''
          CREATE TABLE IF NOT EXISTS {table_name} (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              transaction_id TEXT,
              result_type TEXT,
              sentence TEXT,
              word TEXT,
              image_link TEXT,
              create_date TEXT
          )
      ''')
  elif table_name == 'biased_img_results':
    #cursor.execute(f'''
    #               DROP TABLE IF EXISTS {table_name}
    #           ''')
    cursor.execute(f'''
          CREATE TABLE IF NOT EXISTS {table_name} (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              transaction_id TEXT,
              result_type TEXT,
              sentence TEXT,
              word TEXT,
              image_link TEXT,
              create_date TEXT
          )
      ''')
  elif table_name == 'geographical_bias':
    cursor.execute(f'''
          CREATE TABLE IF NOT EXISTS {table_name} (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              transaction_id TEXT,
              source TEXT,
              geo_entity TEXT,
              entity_type TEXT,
              create_date TEXT
          )
      ''')
  elif table_name == 'Gender_Table':
    cursor.execute(f'''
          CREATE TABLE IF NOT EXISTS {table_name} (
              gender_id INTEGER PRIMARY KEY AUTOINCREMENT,
              gender_name TEXT NOT NULL UNIQUE,
              create_date TEXT
          )
      ''')
  elif table_name == 'Biased_Words':
    cursor.execute(f'''
          CREATE TABLE IF NOT EXISTS {table_name} (
              biasedword_id INTEGER PRIMARY KEY AUTOINCREMENT,
              gender_id INTEGER NOT NULL,
              biased_word TEXT NOT NULL UNIQUE,
              create_date TEXT,
              FOREIGN KEY (gender_id)
              REFERENCES Gender_Table (gender_id)
          )
      ''')
  elif table_name == 'Ethnicity_Table':
    cursor.execute(f'''
          CREATE TABLE IF NOT EXISTS {table_name} (
              ethnicity_id INTEGER PRIMARY KEY AUTOINCREMENT,
              ethnicity_name TEXT NOT NULL UNIQUE,
              create_date TEXT
          )
      ''')
  elif table_name == 'Geolocation_Table':
    cursor.execute(f'''
          CREATE TABLE IF NOT EXISTS {table_name} (
              geolocation_id INTEGER PRIMARY KEY AUTOINCREMENT,
              geolocation_name TEXT NOT NULL UNIQUE,
              create_date TEXT
          )
      ''')

  db.commit()


def word_frequency_analysis():
  word_data = nativeQuery(
    "SELECT word FROM biased_text_results UNION ALL SELECT word FROM biased_alt_Text_results UNION ALL SELECT word FROM biased_img_results"
  )
  words = [row[0] for row in word_data]
  word_counts = Counter(words)
  return word_counts.most_common(10)


'''def geographical_bias_frequency():
  geo_data = nativeQuery("SELECT geo_entity FROM geographical_bias")
  geo_entities = [row[0] for row in geo_data]
  geo_counts = Counter(geo_entities)
  return geo_counts.most_common(10)'''


def save_image(table_name, transaction_id, result_type, male_count, female_count, confidence, skin_color, race,
               image_link):
  db = get_db()
  cursor = db.cursor()

  create_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
  cursor.execute(f'''
        INSERT INTO {table_name} (transaction_id, result_type, male_count, female_count, confidence, skin_color, race, image_link, create_date)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (transaction_id, result_type, male_count, female_count, confidence, skin_color, race, image_link, create_date))

  db.commit()


def insert_biased_result(table_name, transaction_id, result_type, sentence, word, image_link=None):
  print(f"Attempting to insert into {table_name}: transaction_id={transaction_id}, "
        f"result_type={result_type}, sentence={sentence}, word={word}, image_link={image_link}")

  db = get_db()
  cursor = db.cursor()

  create_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

  try:
    cursor.execute(f'''
        INSERT INTO {table_name} (transaction_id, result_type, sentence, word, image_link, create_date)
        VALUES (?, ?, ?, ?, ?, ?)
      ''', (transaction_id, result_type, sentence, word, image_link, create_date))
    print("Insert successful!")
  except Exception as e:
    print(f"Error inserting into {table_name}: {e}")

  db.commit()


def insert_biased_img_result(transaction_id, result_type, sentence, word, image_link):
  print(f"Attempting to insert into biased_img_results: transaction_id={transaction_id}, "
        f"result_type={result_type}, sentence={sentence}, word={word}, image_link={image_link}")

  db = get_db()
  cursor = db.cursor()

  create_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

  try:
    cursor.execute('''
            INSERT INTO biased_img_results (transaction_id, result_type, sentence, word, image_link, create_date)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (transaction_id, result_type, sentence, word, image_link, create_date))
    print(f"Insert into biased_img_results successful for word '{word}' and sentence '{sentence}'.")
  except Exception as e:
    print(f"Error inserting into biased_img_results: {e}")
  db.commit()


def insert_geo_bias_result(transaction_id, source, city=None, country=None):
  db = get_db()
  cursor = db.cursor()

  create_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
  try:
    if city:
      cursor.execute('''
              INSERT INTO geographical_bias (transaction_id, source, geo_entity, entity_type, create_date)
              VALUES (?, ?, ?, 'City', ?)
          ''', (transaction_id, source, city, create_date))
      print(f"Insert into geographical_bias successful City '{city}'.")
    if country:
      cursor.execute('''
              INSERT INTO geographical_bias (transaction_id, source, geo_entity, entity_type, create_date)
              VALUES (?, ?, ?, 'Country', ?)
          ''', (transaction_id, source, country, create_date))
      print(f"Insert into geographical_bias successful Country '{country}'.")
  except Exception as e:
    print(f"Error inserting into biased_img_results: {e}")
  db.commit()

@db.route('/show_db')
def show_db():
  db = get_db()
  cursor = db.cursor()
  text_results = nativeQuery('SELECT * FROM biased_text_results')
  alt_text_results = nativeQuery('SELECT * FROM biased_alt_Text_results')
  img_results = nativeQuery('SELECT * FROM biased_img_results')
  biased_results = nativeQuery('SELECT * FROM biased_results')
  image_txt_results = nativeQuery('SELECT * FROM Image_Txt_Results')
  geographical_bias_results = nativeQuery('SELECT * FROM geographical_bias')
  gender_table = nativeQuery('SELECT * FROM Gender_Table')
  biased_words = nativeQuery('SELECT * FROM Biased_Words')

  # Calculate summary statistics
  total_biased_text = len(text_results)
  total_biased_alt_text = len(alt_text_results)
  total_biased_img_results = len(img_results)
  total_biased_results = len(biased_results)
  total_image_txt_results = len(image_txt_results)
  total_geographical_bias = len(geographical_bias_results)
  total_gender_table = len(gender_table)
  total_biased_words = len(biased_words)

  # Extract unique words from biased sentences, alt texts, and image results
  #unique_words_text = set(word for _, _, content, _, _, _, _ in text_results if content for word in content.split())
  #unique_words_alt_text = set(word for _, _, alt_text, _, _, _, _ in alt_text_results if alt_text for word in alt_text.split())
  #unique_words_img_results = set(word for _, _, content, _, _, _, _ in img_results if content for word in content.split())
  #unique_words_biased_results = set(word for _, _, _, content, _, _, _ in biased_results if content for word in content.split())
  #unique_words_image_txt_results = set(word for row in image_txt_results if if content for word in content.split())
  #unique_words_image_txt_results = set(word for row in geographical_bias_results if if content for word in content.split())

  # Extract unique words from biased sentences, alt texts, and image results
  unique_words_text = set(word for row in text_results if row[3] for word in row[3].split())
  unique_words_alt_text = set(word for row in alt_text_results if row[3] for word in row[3].split())
  unique_words_img_results = set(word for row in img_results if row[3] for word in row[3].split())
  unique_words_biased_results = set(word for row in biased_results if row[3] for word in row[3].split())
  unique_words_image_txt_results = set(word for row in image_txt_results if row[7] for word in row[7].split())
  unique_words_geographical_bias = set(row[3] for row in geographical_bias_results if row[3])

  # Calculate unique word counts
  unique_word_count_text = len(unique_words_text)
  unique_word_count_alt_text = len(unique_words_alt_text)
  unique_word_count_img_results = len(unique_words_img_results)
  unique_word_count_biased_results = len(unique_words_biased_results)
  unique_word_count_image_txt_results = len(unique_words_image_txt_results)
  unique_word_count_geographical_bias = len(unique_words_geographical_bias)

  # Analytics
  word_frequency = word_frequency_analysis()
  #top_geo_entities, geo_counts = zip(*geographical_bias_frequency())

  return render_template('show_db.html',
                         text_results=text_results,
                         alt_text_results=alt_text_results,
                         img_results=img_results,
                         biased_results=biased_results,
                         image_txt_results=image_txt_results,
                         geographical_bias_results=geographical_bias_results,
                         gender_table=gender_table,
                         biased_words=biased_words,
                         total_biased_text=total_biased_text,
                         total_biased_alt_text=total_biased_alt_text,
                         total_biased_img_results=total_biased_img_results,
                         total_biased_results=total_biased_results,
                         total_image_txt_results=total_image_txt_results,
                         total_geographical_bias=total_geographical_bias,
                         total_gender_table=total_gender_table,
                         total_biased_words=total_biased_words,
                         unique_word_count_text=unique_word_count_text,
                         unique_word_count_alt_text=unique_word_count_alt_text,
                         unique_word_count_img_results=unique_word_count_img_results,
                         unique_word_count_biased_results=unique_word_count_biased_results,
                         unique_word_count_image_txt_results=unique_word_count_image_txt_results,
                         unique_word_count_geographical_bias=unique_word_count_geographical_bias,
                         word_frequency=word_frequency,
                         #top_geo_entities=top_geo_entities,
                         #geo_counts=geo_counts,
                         zip=zip)

def textsummaryresult(transaction_id):
  db = get_db()
  cursor = db.cursor()

  text_results = cursor.execute('''
        SELECT * FROM biased_text_results WHERE transaction_id = ?
    ''', (transaction_id,)).fetchall()

  alt_text_results = cursor.execute('''
        SELECT * FROM biased_alt_Text_results WHERE transaction_id = ?
    ''', (transaction_id,)).fetchall()

  img_results = cursor.execute('''
        SELECT * FROM biased_img_results WHERE transaction_id = ?
    ''', (transaction_id,)).fetchall()

  text_results_Gender_Count = cursor.execute('''
          SELECT DISTINCT(WORD), count(*) FROM biased_text_results WHERE TRANSACTION_ID =  ? group by word
      ''', (transaction_id,)).fetchall()
  query_results = [dict(row) for row in text_results_Gender_Count]
  text_results_Gender_Count = [(item['word'], item['count(*)']) for item in query_results]

  alt_text_results_Gender_Count = cursor.execute('''
            SELECT DISTINCT(WORD), count(*) FROM biased_alt_Text_results WHERE TRANSACTION_ID =  ? group by word
        ''', (transaction_id,)).fetchall()
  query_results = [dict(row) for row in alt_text_results_Gender_Count]
  alt_text_results_Gender_Count = [(item['word'], item['count(*)']) for item in query_results]

  img_text_results_Gender_Count = cursor.execute('''
            SELECT DISTINCT(WORD), count(*) FROM biased_img_results WHERE TRANSACTION_ID =  ? group by word
        ''', (transaction_id,)).fetchall()
  query_results = [dict(row) for row in img_text_results_Gender_Count]
  img_text_results_Gender_Count = [(item['word'], item['count(*)']) for item in query_results]

  total_Ethnicity_Count = cursor.execute('''
              SELECT DISTINCT(geo_entity), count(*) FROM geographical_bias WHERE TRANSACTION_ID =  ? AND ENTITY_TYPE = 'City' group by geo_entity
          ''', (transaction_id,)).fetchall()
  query_results = [dict(row) for row in total_Ethnicity_Count]
  total_Ethnicity_Count = [(item['geo_entity'], item['count(*)']) for item in query_results]

  total_GeoLocation_Count = cursor.execute('''
              SELECT DISTINCT(geo_entity), count(*) FROM geographical_bias WHERE TRANSACTION_ID =  ? AND ENTITY_TYPE = 'Country' group by geo_entity
          ''', (transaction_id,)).fetchall()
  query_results = [dict(row) for row in total_GeoLocation_Count]
  total_GeoLocation_Count = [(item['geo_entity'], item['count(*)']) for item in query_results]

  text_results_Ethnicity_Count = cursor.execute('''
            SELECT DISTINCT(geo_entity), count(*) FROM geographical_bias WHERE TRANSACTION_ID =  ? AND SOURCE = 'text' AND ENTITY_TYPE = 'City' group by geo_entity
        ''', (transaction_id,)).fetchall()
  query_results = [dict(row) for row in text_results_Ethnicity_Count]
  text_results_Ethnicity_Count = [(item['geo_entity'], item['count(*)']) for item in query_results]

  alt_text_results_Ethnicity_Count = cursor.execute('''
              SELECT DISTINCT(geo_entity), count(*) FROM geographical_bias WHERE TRANSACTION_ID =  ? AND SOURCE = 'alt_text' AND ENTITY_TYPE = 'City' group by geo_entity
          ''', (transaction_id,)).fetchall()
  query_results = [dict(row) for row in alt_text_results_Ethnicity_Count]
  alt_text_results_Ethnicity_Count = [(item['geo_entity'], item['count(*)']) for item in query_results]

  img_text_results_Ethnicity_Count = cursor.execute('''
              SELECT DISTINCT(geo_entity), count(*) FROM geographical_bias WHERE TRANSACTION_ID =  ? AND SOURCE = 'image' AND ENTITY_TYPE = 'City' group by geo_entity
          ''', (transaction_id,)).fetchall()
  query_results = [dict(row) for row in img_text_results_Ethnicity_Count]
  img_text_results_Ethnicity_Count = [(item['geo_entity'], item['count(*)']) for item in query_results]

  text_results_GeoLocation_Count = cursor.execute('''
            SELECT DISTINCT(geo_entity), count(*) FROM geographical_bias WHERE TRANSACTION_ID =  ? AND SOURCE = 'text' AND ENTITY_TYPE = 'Country' group by geo_entity
        ''', (transaction_id,)).fetchall()
  query_results = [dict(row) for row in text_results_GeoLocation_Count]
  text_results_GeoLocation_Count = [(item['geo_entity'], item['count(*)']) for item in query_results]

  alt_text_results_GeoLocation_Count = cursor.execute('''
              SELECT DISTINCT(geo_entity), count(*) FROM geographical_bias WHERE TRANSACTION_ID =  ? AND SOURCE = 'alt_text' AND ENTITY_TYPE = 'Country' group by geo_entity
          ''', (transaction_id,)).fetchall()
  query_results = [dict(row) for row in alt_text_results_GeoLocation_Count]
  alt_text_results_GeoLocation_Count = [(item['geo_entity'], item['count(*)']) for item in query_results]

  img_text_results_GeoLocation_Count = cursor.execute('''
              SELECT DISTINCT(geo_entity), count(*) FROM geographical_bias WHERE TRANSACTION_ID =  ? AND SOURCE = 'image' AND ENTITY_TYPE = 'Country' group by geo_entity
          ''', (transaction_id,)).fetchall()
  query_results = [dict(row) for row in img_text_results_GeoLocation_Count]
  img_text_results_GeoLocation_Count = [(item['geo_entity'], item['count(*)']) for item in query_results]

  #combining all text results counts
  overall_gender_count = text_results_Gender_Count + alt_text_results_Gender_Count + img_text_results_Gender_Count

  total_biased_text = len(text_results)
  total_biased_alt_text = len(alt_text_results)
  total_biased_img_results = len(img_results)
  total_Ethnicity_text = len(text_results_Ethnicity_Count)
  total_Ethnicity_alt_text = len(alt_text_results_Ethnicity_Count)
  total_Ethnicity_img_text = len(img_text_results_Ethnicity_Count)
  total_GeoLocation_text = len(text_results_GeoLocation_Count)
  total_GeoLocation_alt_text = len(alt_text_results_GeoLocation_Count)
  total_GeoLocation_img_text = len(img_text_results_GeoLocation_Count)

  print(f'{text_results_Gender_Count}\n{alt_text_results_Gender_Count}\n{img_text_results_Gender_Count}\n{overall_gender_count}')

  return (total_biased_text, total_biased_alt_text, total_biased_img_results,text_results_Gender_Count,alt_text_results_Gender_Count,
          img_text_results_Gender_Count, overall_gender_count, total_Ethnicity_Count, total_GeoLocation_Count, text_results_Ethnicity_Count,
          alt_text_results_Ethnicity_Count, img_text_results_Ethnicity_Count, text_results_GeoLocation_Count, alt_text_results_GeoLocation_Count,
          img_text_results_GeoLocation_Count, total_Ethnicity_text, total_Ethnicity_alt_text, total_Ethnicity_img_text, total_GeoLocation_text,
          total_GeoLocation_alt_text, total_GeoLocation_img_text)

#Get Image Model Results Summary
def imageSummaryResults(transaction_id):
  db = get_db()
  cursor = db.cursor()

  image_results_Count = len(cursor.execute('''
          SELECT * FROM Image_Txt_Results WHERE transaction_id = ?
      ''', (transaction_id,)).fetchall())

  image_results_Gender_Count = cursor.execute('''
          SELECT SUM(male_count) AS Male, SUM(Female_count) AS Female FROM Image_Txt_Results WHERE TRANSACTION_ID =  ?
      ''', (transaction_id,)).fetchall()
  query_results = [dict(row) for row in image_results_Gender_Count]
  image_results_Gender_Count = [('Male', query_results[0].get('Male', 0)), ('Female', query_results[0].get('Female', 0))]

  image_results_Confidence_Count = cursor.execute('''
            SELECT DISTINCT(confidence), count(*) FROM Image_Txt_Results WHERE TRANSACTION_ID =  ? group by confidence
        ''', (transaction_id,)).fetchall()
  query_results = [dict(row) for row in image_results_Confidence_Count]
  image_results_Confidence_Count = [(item['confidence'], item['count(*)']) for item in query_results]

  image_results_Skin_Color_Count = cursor.execute('''
              SELECT DISTINCT(skin_color), count(*) FROM Image_Txt_Results WHERE TRANSACTION_ID =  ? group by skin_color
          ''', (transaction_id,)).fetchall()
  query_results = [dict(row) for row in image_results_Skin_Color_Count]
  image_results_Skin_Color_Count = [(item['skin_color'], item['count(*)']) for item in query_results]

  image_results_Race_Count = cursor.execute('''
                SELECT DISTINCT(race), count(*) FROM Image_Txt_Results WHERE TRANSACTION_ID =  ? group by race
            ''', (transaction_id,)).fetchall()
  query_results = [dict(row) for row in image_results_Race_Count]
  image_results_Race_Count = [(item['race'], item['count(*)']) for item in query_results]

  print(f'{image_results_Count}\n{image_results_Gender_Count}\n{image_results_Confidence_Count}\n{image_results_Skin_Color_Count}\n{image_results_Race_Count}')

  return image_results_Count, image_results_Gender_Count, image_results_Confidence_Count, image_results_Skin_Color_Count, image_results_Race_Count

def genderresult():
  db = get_db()
  cursor = db.cursor()
  gender_results = cursor.execute('SELECT gender_id, gender_name FROM Gender_Table').fetchall()
  return gender_results


def gendersave(name):
  db = get_db()
  cursor = db.cursor()
  try:
    create_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute('''
          INSERT INTO Gender_Table (gender_name, create_date)
          VALUES (?, ?)
      ''', (name, create_date))
    db.commit()
    return 'Successfully Saved'
  except Exception as e:
    print(f"Error inserting into the database: {e}")
    return 'Failed to Save'

def genderupdate(Id, name):
  db = get_db()
  cursor = db.cursor()
  try:
    create_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("UPDATE Gender_Table SET gender_name ='"+name+"'  WHERE gender_id ='"+Id+"'")
    db.commit()
    return 'Successfully Updated'
  except Exception as e:
    print(f"Error inserting into the database: {e}")
    return 'Failed to update'


def genderdelete(id):
  db = get_db()
  cursor = db.cursor()
  try:
    gender_results = nativeQuery("SELECT * FROM Gender_Table WHERE gender_id ='" + id + "'")
    if len(gender_results) > 0:
      cursor.execute("DELETE FROM Biased_Words WHERE gender_id ='" + id + "'")
      cursor.execute("DELETE FROM Gender_Table WHERE gender_id ='"+id+"'")
      db.commit()
      return 'Successfully Deleted'
    else:
      return 'No Data Found'
  except Exception as e:
    print(f"Error inserting into the database: {e}")
    return 'Failed to Delete'

def nativeQuery(query):
  try:
    db = get_db()
    cursor = db.cursor()
    cursor.execute(query)
    result = cursor.fetchall()
  except sqlite3.Error as e:
    print(f"Database query error: {e}")
    result = []
  finally:
    if cursor:
      cursor.close()
    #close_db()  # Ensure the connection is closed
  return result


def baisedwordresult():
  db = get_db()
  cursor = db.cursor()
  baisedword_results = cursor.execute('''
        SELECT G.gender_name, B.biased_word, B.biasedword_id
        FROM Biased_Words B
        JOIN Gender_Table G ON G.gender_id = B.gender_id
    ''').fetchall()

  for result in baisedword_results:
    gender_name = result[0]
    biased_word = result[1]
    print(f"Biased Words: \nGender: {gender_name}, Biased Word: {biased_word}")

  return baisedword_results


def baisedwordsave(genderId, word):
  db = get_db()
  cursor = db.cursor()
  try:
    create_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute('''
          INSERT INTO Biased_Words (gender_id, biased_word, create_date)
          VALUES (?, ?, ?)
      ''', (genderId, word, create_date))
    db.commit()
    return 'Successfully Saved'
  except Exception as e:
    print(f"Error inserting into the database: {e}")
    return 'Failed to Save'


def baisedwordupdate(Id, word):
  db = get_db()
  cursor = db.cursor()
  try:
    cursor.execute('''
        UPDATE Biased_Words SET biased_word = ? WHERE Biasedword_id = ?
        ''', (word, Id))
    db.commit()
    return 'Successfully Updated'
  except Exception as e:
    print(f"Error inserting into the database: {e}")
    return 'Failed to update'
  # finally:
  # db.close()


def baisedworddelete(id):
  db = get_db()
  cursor = db.cursor()
  try:
    gender_results = cursor.execute('''
        SELECT * FROM Biased_Words WHERE Biasedword_id = ?
        ''', (id,)).fetchall()
    if gender_results:
      cursor.execute('''
            DELETE FROM Biased_Words WHERE Biasedword_id = ?
            ''', (id,))
      db.commit()
      return 'Successfully Deleted'
    else:
      return 'No Data Found'
  except Exception as e:
    print(f"Error inserting into the database: {e}")
    return 'Failed to Delete'
  # finally:
  # db.close()

def ethnicityresult():
  db = get_db()
  cursor = db.cursor()
  ethnicity_results = cursor.execute('SELECT ethnicity_id, ethnicity_name FROM Ethnicity_Table').fetchall()
  return ethnicity_results


def ethnicitysave(name):
  db = get_db()
  cursor = db.cursor()
  try:
    create_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute('''
          INSERT INTO Ethnicity_Table (ethnicity_name, create_date)
          VALUES (?, ?)
      ''', (name, create_date))
    db.commit()
    return 'Successfully Saved'
  except Exception as e:
    print(f"Error inserting into the database: {e}")
    return 'Failed to Save'

def ethnicityupdate(Id, name):
  db = get_db()
  cursor = db.cursor()
  try:
    create_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("UPDATE Ethnicity_Table SET ethnicity_name ='"+name+"'  WHERE ethnicity_id ='"+Id+"'")
    db.commit()
    return 'Successfully Updated'
  except Exception as e:
    print(f"Error inserting into the database: {e}")
    return 'Failed to update'


def ethnicitydelete(id):
  db = get_db()
  cursor = db.cursor()
  try:
    ethnicity_results = nativeQuery("SELECT * FROM Ethnicity_Table WHERE ethnicity_id ='" + id + "'")
    if len(ethnicity_results) > 0:
      cursor.execute("DELETE FROM Ethnicity_Table WHERE ethnicity_id ='"+id+"'")
      db.commit()
      return 'Successfully Deleted'
    else:
      return 'No Data Found'
  except Exception as e:
    print(f"Error inserting into the database: {e}")
    return 'Failed to Delete'

def geolocationresult():
  db = get_db()
  cursor = db.cursor()
  geolocation_results = cursor.execute('SELECT geolocation_id, geolocation_name FROM Geolocation_Table').fetchall()
  return geolocation_results


def geolocationsave(name):
  db = get_db()
  cursor = db.cursor()
  try:
    create_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute('''
          INSERT INTO Geolocation_Table (geolocation_name, create_date)
          VALUES (?, ?)
      ''', (name, create_date))
    db.commit()
    return 'Successfully Saved'
  except Exception as e:
    print(f"Error inserting into the database: {e}")
    return 'Failed to Save'

def geolocationupdate(Id, name):
  db = get_db()
  cursor = db.cursor()
  try:
    create_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("UPDATE Geolocation_Table SET geolocation_name ='"+name+"'  WHERE geolocation_id ='"+Id+"'")
    db.commit()
    return 'Successfully Updated'
  except Exception as e:
    print(f"Error inserting into the database: {e}")
    return 'Failed to update'


def geolocationdelete(id):
  db = get_db()
  cursor = db.cursor()
  try:
    geolocation_results = nativeQuery("SELECT * FROM Geolocation_Table WHERE geolocation_id ='" + id + "'")
    if len(geolocation_results) > 0:
      cursor.execute("DELETE FROM Geolocation_Table WHERE geolocation_id ='"+id+"'")
      db.commit()
      return 'Successfully Deleted'
    else:
      return 'No Data Found'
  except Exception as e:
    print(f"Error inserting into the database: {e}")
    return 'Failed to Delete'


if __name__ == "__main__":
  db.run(debug=True, port=3000)
