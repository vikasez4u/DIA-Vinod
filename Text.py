#from flask import Flask
#from db import init_db, ensure_tables_exist, insert_biased_result, insert_geo_bias_result

from Text_processing_helper import (
    extract_text_from_url,
    detect_biased_sentences,
    detect_geo_ethnicity_bias,
    extract_alt_text_from_url,
    detect_biased_sentences_in_alt_text,
    extract_text_from_images,
)

def text_analysis_results(url, transaction_id, keyword_list):
    """
    Conducts comprehensive analysis on the text content, alt text, and images from a webpage
    to detect gender and geographical bias, and logs results into the database.
    """
    text_content = extract_text_from_url(url)

    ethnicity_list = [
        "African American", "Asian", "Hispanic", "Latino", "Native American",
        "Indigenous", "Arab", "Jewish", "Caucasian", "White", "Black", "Pacific Islander",
        "Middle Eastern", "Indian", "Pakistani", "Bangladeshi", "Korean", "Chinese",
        "Japanese", "Filipino", "Vietnamese", "Mexican", "Puerto Rican", "Cuban",
        "Colombian", "Brazilian", "Argentinian", "Peruvian", "Egyptian", "Somali",
        "Ethiopian", "Nigerian", "Ghanaian", "Kenyan", "South African", "Aboriginal",
        "Maori", "Inuit", "Aleut", "Hmong", "Romani", "Burmese", "Thai", "Cambodian",
        "Laotian", "Mongolian", "Turkish", "Persian", "Armenian", "Slavic", "Greek",
        "Italian", "French", "German", "Dutch", "Norwegian", "Swedish", "Finnish",
        "Danish", "Scottish", "Irish", "Welsh", "Polish", "Russian", "Ukrainian",
        "Serbian", "Croatian", "Bosnian", "Hungarian", "Jewish", "Afro-Caribbean",
        "Caribbean", "Haitian", "Jamaican", "Trinidadian", "Guyanese"
    ]

    txt_results = detect_biased_sentences(
        text_content, keyword_list, 'biased_text_results', transaction_id
    )

    '''for sentence, word in zip(biased_sentences, biased_words):
        insert_biased_result(
            table_name='biased_text_results',
            transaction_id=transaction_id,
            result_type='Text',
            sentence=sentence,
            word=word
        )'''

    text_geo_ethnicities = detect_geo_ethnicity_bias(
        text_content, transaction_id, source='text', ethnicity_list=ethnicity_list
    )

    '''try:
      for entity in text_geo_ethnicities:
          diadb.insert_geo_bias_result(
              transaction_id=transaction_id,
              source='text',
              city=entity['entity'] if entity['type'] == 'ethnicity' else None,
              country=entity['entity'] if entity['type'] == 'Country' else None
          )
      print("Inserted text eth geo")
    except Exception as e:(
      print(f"Failed to insert into geographical table: {e}"))'''

    alt_texts = extract_alt_text_from_url(url)
    alt_results = detect_biased_sentences_in_alt_text(alt_texts, keyword_list, transaction_id)
    alttext_geo_ethnicities = detect_geo_ethnicity_bias(
        ' '.join([alt[0] for alt in alt_texts]),
        transaction_id,
        source='alt_text',
        ethnicity_list=ethnicity_list,
        image_urls=[url for _, url in alt_texts]
    )

    '''try:
      for entity in alttext_geo_ethnicities:
          diadb.insert_geo_bias_result(
              transaction_id=transaction_id,
              source='alt_text',
              city=entity['entity'] if entity['type'] == 'ethnicity' else None,
              country=entity['entity'] if entity['type'] == 'Country' else None
          )
      print("Inserted text eth geo")
    except Exception as e: (
      print(f"Failed to insert into geographical table: {e}"))'''

    img_results = extract_text_from_images(url, transaction_id, keyword_list, ethnicity_list)

    '''try:
      for entity in img_results['geo_bias_results']:
          diadb.insert_geo_bias_result(
              transaction_id=transaction_id,
              source='image',
              city=entity['entity'] if entity['type'] == 'ethnicity' else None,
              country=entity['entity'] if entity['type'] == 'Country' else None
          )
      print("Inserted text eth geo")
    except Exception as e: (
      print(f"Failed to insert into geographical table: {e}"))'''

    return {
        'text_bias_results': txt_results,
        'alt_text_results': alt_results,
        'text_geo_ethnicities': text_geo_ethnicities,
        'alt_text_geo_ethnicities': alttext_geo_ethnicities,
        'image_results': img_results
    }

# Standalone Testing
# if __name__ == "__main__":
#     app = Flask(__name__)
#     app.config['TESTING'] = True

#     init_db(app)

#     with app.app_context():
#         # Ensure all required tables exist
#         ensure_tables_exist()

#         url = "https://travelmelodies.com/incredible-india-quotes/"
#         transaction_id = 1
#         keyword_list = ["he", "she", "man", "woman", "male", "female", "husband", "wife", "father", "mother"]

#         try:
#             results = text_analysis_results(url, transaction_id, keyword_list)
#             print("Final Analysis Results:", results)
#         except Exception as e:
#             print(f"An error occurred during testing: {e}")
