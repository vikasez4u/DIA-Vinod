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
                transaction_id INTEGER,
                result_type TEXT,
                male_count INTEGER,
                female_count INTEGER,
                confidence INTEGER,
                max_skin_key TEXT,
                max_race_key TEXT,
                image_link TEXT,
                create_date TEXT
            )
        ''')
    elif table_name == 'Biased_Words':
        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS Gender_Table (
                gender_id INTEGER PRIMARY KEY AUTOINCREMENT,
                gender_name TEXT NOT NULL UNIQUE,
                create_date TEXT
            )
        ''')
        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS Biased_Words (
                biasedword_id INTEGER PRIMARY KEY AUTOINCREMENT,
                gender_id INTEGER NOT NULL,
                biased_word TEXT NOT NULL UNIQUE,
                create_date TEXT,
                FOREIGN KEY (gender_id)
                    REFERENCES Gender_Table (gender_id)
            )
        ''')
    elif table_name == 'Geo_Race_Ethnicity_Results':
        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS {table_name} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                transaction_id INTEGER,
                result_type TEXT,
                entity_type TEXT,
                entity TEXT,
                sentence TEXT,
                create_date TEXT
            )
        ''')
    else:
        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS {table_name} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                transaction_id INTEGER,
                result_type TEXT,
                sentence TEXT,
                word TEXT,
                image_link TEXT,
                create_date TEXT
            )
        ''')

def save_image_result(table_name, transaction_id, result_type, male_count, female_count,
                      confidence, max_skin_key, max_race_key, image_link):
    db = get_db()
    cursor = db.cursor()
    try:
        create_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute(f'''
            INSERT INTO {table_name} (transaction_id, result_type, male_count, female_count, confidence,
                                       max_skin_key, max_race_key, image_link, create_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (transaction_id, result_type, male_count, female_count, confidence, max_skin_key, max_race_key, image_link, create_date))
        db.commit()
    except Exception as e:
        print(f"Error inserting into the database: {e}")

def insert_result(table_name, transaction_id, result_type, sentence, word, image_link=None):
    db = get_db()
    cursor = db.cursor()
    try:
        create_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cleaned_sentence = bleach.clean(sentence, tags=[], strip=True)
        cursor.execute(f'''
            INSERT INTO {table_name} (transaction_id, result_type, sentence, word, image_link, create_date)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (transaction_id, result_type, cleaned_sentence, word, image_link, create_date))
        db.commit()
    except Exception as e:
        print(f"Error inserting into the database: {e}")

def insert_geo_race_ethnicity_result(transaction_id, result_type, entity_type, entity, sentence):
    db = get_db()
    cursor = db.cursor()
    try:
        create_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute(f'''
            INSERT INTO Geo_Race_Ethnicity_Results (transaction_id, result_type, entity_type, entity, sentence, create_date)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (transaction_id, result_type, entity_type, entity, sentence, create_date))
        db.commit()
    except Exception as e:
        print(f"Error inserting into the database: {e}")

def close_db(error):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def native_query(query):
    db = get_db()
    cursor = db.cursor()
    cursor.execute(query)
    return cursor.fetchall()

@db.route('/show_db')
def show_db():
    text_results = native_query('SELECT * FROM biased_Text_results')
    alt_text_results = native_query('SELECT * FROM biased_alt_Text_results')
    img_results = native_query('SELECT * FROM biased_img_results')
    geo_race_ethnicity_results = native_query('SELECT * FROM Geo_Race_Ethnicity_Results')

    # Calculate summary statistics
    total_biased_text = len(text_results)
    total_biased_alt_text = len(alt_text_results)
    total_biased_img_results = len(img_results)
    total_geo_race_ethnicity_results = len(geo_race_ethnicity_results)

    # Extract unique words from biased sentences, alt texts, and image results
    unique_words_text = set(word for _, _, content, _, _, _, _ in text_results if content for word in content.split())
    unique_words_alt_text = set(
        word for _, _, alt_text, _, _, _, _ in alt_text_results if alt_text for word in alt_text.split())
    unique_words_img_results = set(word for _, _, content, _, _, _, _ in img_results if content for word in content.split())
    unique_entities_geo_race_ethnicity = set(entity for _, _, _, entity_type, entity, _, _ in geo_race_ethnicity_results if entity)

    # Calculate unique word counts
    unique_word_count_text = len(unique_words_text)
    unique_word_count_alt_text = len(unique_words_alt_text)
    unique_word_count_img_results = len(unique_words_img_results)
    unique_entity_count_geo_race_ethnicity = len(unique_entities_geo_race_ethnicity)

    return render_template('show_db.html', text_results=text_results, alt_text_results=alt_text_results,
                           img_results=img_results, geo_race_ethnicity_results=geo_race_ethnicity_results,
                           total_biased_text=total_biased_text, total_biased_alt_text=total_biased_alt_text,
                           total_biased_img_results=total_biased_img_results,
                           total_geo_race_ethnicity_results=total_geo_race_ethnicity_results,
                           unique_word_count_text=unique_word_count_text,
                           unique_word_count_alt_text=unique_word_count_alt_text,
                           unique_word_count_img_results=unique_word_count_img_results,
                           unique_entity_count_geo_race_ethnicity=unique_entity_count_geo_race_ethnicity)

def text_summary_result(transaction_id):
    text_results_tr = native_query(f'SELECT * FROM biased_Text_results WHERE transaction_id ={transaction_id}')
    alt_text_results = native_query(f'SELECT * FROM biased_alt_Text_results WHERE transaction_id ={transaction_id}')
    img_results = native_query(f'SELECT * FROM biased_img_results WHERE transaction_id ={transaction_id}')
    geo_race_ethnicity_results = native_query(f'SELECT * FROM Geo_Race_Ethnicity_Results WHERE transaction_id ={transaction_id}')

    text_results_tr_Gender_Count = native_query(
        f'SELECT DISTINCT(WORD), count(*) FROM BIASED_TEXT_RESULTS WHERE TRANSACTION_ID ={transaction_id} group by word')
    alt_text_results_tr_Gender_Count = native_query(
        f'SELECT DISTINCT(WORD), count(*) FROM biased_alt_Text_results WHERE TRANSACTION_ID ={transaction_id} group by word')
    img_text_results_tr_Gender_Count = native_query(
        f'SELECT DISTINCT(WORD), count(*) FROM biased_img_results WHERE TRANSACTION_ID ={transaction_id} group by word')

    total_biased_text = len(text_results_tr)
    total_biased_alt_text = len(alt_text_results)
    total_biased_img_results = len(img_results)

    return total_biased_text, total_biased_alt_text, total_biased_img_results, text_results_tr_Gender_Count, alt_text_results_tr_Gender_Count, img_text_results_tr_Gender_Count

def image_summary_result(transaction_id):
    image_results_tr = native_query(f'SELECT COUNT(MALE_COUNT),COUNT(FEMALE_COUNT) FROM Image_Txt_Results WHERE transaction_id ={transaction_id}')
    return image_results_tr

def gender_result():
    return native_query('SELECT GENDER_ID,GENDER_NAME FROM Gender_Table')

def gender_save(name):
    db = get_db()
    cursor = db.cursor()
    try:
        create_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute(f'INSERT INTO Gender_Table (gender_name, create_date) VALUES (?, ?)', (name, create_date))
        db.commit()
        return 'Successfully Saved'
    except Exception as e:
        print(f"Error inserting into the database: {e}")
        return 'Failed to Save'

def gender_update(Id, name):
    db = get_db()
    cursor = db.cursor()
    try:
        create_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute(f"UPDATE Gender_Table SET gender_name ='{name}' WHERE gender_id ='{Id}'")
        db.commit()
        return 'Successfully Updated'
    except Exception as e:
        print(f"Error inserting into the database: {e}")
        return 'Failed to update'

def gender_delete(id):
    db = get_db()
    cursor = db.cursor()
    try:
        gender_results = native_query(f"SELECT * FROM Gender_Table WHERE gender_id ='{id}'")
        if len(gender_results) > 0:
            cursor.execute(f"DELETE FROM Biased_Words WHERE gender_id ='{id}'")
            cursor.execute(f"DELETE FROM Gender_Table WHERE gender_id ='{id}'")
            db.commit()
            return 'Successfully Deleted'
        else:
            return 'No Data Found'
    except Exception as e:
        print(f"Error inserting into the database: {e}")
        return 'Failed to Delete'

def biased_word_result():
    return native_query('SELECT G.Gender_Name, B.Biased_Word, B.Biasedword_id FROM Biased_Words B, Gender_Table G where G.Gender_ID = B.Gender_Id')

def biased_word_save(gender_id, word):
    db = get_db()
    cursor = db.cursor()
    try:
        create_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute(f'INSERT INTO Biased_Words (gender_id, biased_word, create_date) VALUES (?, ?, ?)', (gender_id, word, create_date))
        db.commit()
        return 'Successfully Saved'
    except Exception as e:
        print(f"Error inserting into the database: {e}")
        return 'Failed to Save'

def biased_word_update(id, word):
    db = get_db()
    cursor = db.cursor()
    try:
        create_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute(f"UPDATE Biased_Words SET biased_word ='{word}' WHERE Biasedword_id ='{id}'")
        db.commit()
        return 'Successfully Updated'
    except Exception as e:
        print(f"Error inserting into the database: {e}")
        return 'Failed to update'

def biased_word_delete(id):
    db = get_db()
    cursor = db.cursor()
    try:
        gender_results = native_query(f"SELECT * FROM Biased_Words WHERE Biasedword_id ='{id}'")
        if len(gender_results) > 0:
            cursor.execute(f"DELETE FROM Biased_Words WHERE Biasedword_id ='{id}'")
            db.commit()
            return 'Successfully Deleted'
        else:
            return 'No Data Found'
    except Exception as e:
        print(f"Error inserting into the database: {e}")
        return 'Failed to Delete'

if __name__ == "__main__":
    db.run(debug=True, port=3000)
