import sqlite3
from datetime import datetime
from flask import g

DATABASE = 'DIA.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
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

def insert_result(table_name, transaction_id, result_type, sentence, word, image_link):
    db = get_db()
    cursor = db.cursor()
    create_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute(f'''
        INSERT INTO {table_name} (transaction_id, result_type, sentence, word, image_link, create_date)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (transaction_id, result_type, sentence, word, image_link, create_date))
    db.commit()

def close_db(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def native_query(query):
    db = get_db()
    cursor = db.cursor()
    cursor.execute(query)
    return cursor.fetchall()

def text_summary_result(transaction_id):
    text_results_tr = native_query(f'SELECT * FROM biased_Text_results WHERE transaction_id = {transaction_id}')
    alt_text_results = native_query(f'SELECT * FROM biased_alt_Text_results WHERE transaction_id = {transaction_id}')
    img_results = native_query(f'SELECT * FROM biased_img_results WHERE transaction_id = {transaction_id}')
    total_biased_text = len(text_results_tr)
    total_biased_alt_text = len(alt_text_results)
    total_biased_img_results = len(img_results)
    return total_biased_text, total_biased_alt_text, total_biased_img_results

def image_summary_result(transaction_id):
    image_results_tr = native_query(f'SELECT COUNT(MALE_COUNT),COUNT(FEMALE_COUNT) FROM Image_Txt_Results WHERE transaction_id ={transaction_id}')
    return image_results_tr

def gender_result():
    return native_query('SELECT GENDER_ID,GENDER_NAME FROM Gender_Table')

def gender_save(name):
    db = get_db()
    cursor = db.cursor()
    create_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute(f'INSERT INTO Gender_Table (gender_name, create_date) VALUES (?, ?)', (name, create_date))
    db.commit()
    return 'Successfully Saved'

def gender_update(Id, name):
    db = get_db()
    cursor = db.cursor()
    cursor.execute(f"UPDATE Gender_Table SET gender_name ='{name}' WHERE gender_id ='{Id}'")
    db.commit()
    return 'Successfully Updated'

def gender_delete(id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute(f"DELETE FROM Gender_Table WHERE gender_id ='{id}'")
    db.commit()
    return 'Successfully Deleted'

def biased_word_result():
    return native_query('SELECT G.Gender_Name, B.Biased_Word, B.Biasedword_id FROM Biased_Words B, Gender_Table G where G.Gender_ID = B.Gender_Id')

def biased_word_save(gender_id, word):
    db = get_db()
    cursor = db.cursor()
    create_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute(f'INSERT INTO Biased_Words (gender_id, biased_word, create_date) VALUES (?, ?, ?)', (gender_id, word, create_date))
    db.commit()
    return 'Successfully Saved'

def biased_word_update(id, word):
    db = get_db()
    cursor = db.cursor()
    cursor.execute(f"UPDATE Biased_Words SET biased_word ='{word}' WHERE Biasedword_id ='{id}'")
    db.commit()
    return 'Successfully Updated'

def biased_word_delete(id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute(f"DELETE FROM Biased_Words WHERE Biasedword_id ='{id}'")
    db.commit()
    return 'Successfully Deleted'
