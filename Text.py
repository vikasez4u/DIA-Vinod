#from flask import Flask
from db import init_db, ensure_tables_exist, insert_biased_result, insert_geo_bias_result
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
    to detect gender and geographical bias.
    
    Parameters:
        url (str): URL of the page to analyze.
        transaction_id (int): Unique identifier for the database transaction.
        keyword_list (list): List of
          keywords to detect gender-biased terms.
        
    Returns:
        dict: Contains results of biased text, biased alt text, and biased image text analysis.
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

    # Detects biased sentences within the main text content using specified keywords
    txt_results = detect_biased_sentences(text_content, keyword_list, 'biased_text_results', transaction_id)

    # Identifies geographical and ethnicity bias within the main text content
    text_geo_ethnicities = detect_geo_ethnicity_bias(text_content, transaction_id, source='text', ethnicity_list=ethnicity_list)
    
    # Alt text extraction and analysis
    alt_texts = extract_alt_text_from_url(url)  # Retrieves alt text and image source pairs from images on the page
    
    # Detects gender-biased words within alt text descriptions and logs to the database
    alt_results = detect_biased_sentences_in_alt_text(alt_texts, keyword_list, transaction_id)
    # Detects geographical bias within alt text descriptions
    alttext_geo_ethnicities = detect_geo_ethnicity_bias(' '.join([alt[0] for alt in alt_texts]), transaction_id, source='alt_text', ethnicity_list=ethnicity_list,image_urls=[url for _, url in alt_texts])
    
    # Image text extraction and analysis
    img_results = extract_text_from_images(url, transaction_id, keyword_list)  # Extracts and analyzes text from images for bias

    # Returns results of text, alt text, and image bias analyses
    return {
        'text_bias_results': biased_sentences,
        'alt_text_results': alt_results,
        'alt_text_geo_ethnicities': alttext_geo_ethnicities,
        'image_results': img_results
    }

# Example test run
url = "https://travelmelodies.com/incredible-india-quotes/"
transaction_id = 1
keyword_list = ["he", "she", "man", "woman", "male", "female", "husband", "wife", "father", "mother"]

# Run the analysis function and print results
results = text_analysis_results(url, transaction_id, keyword_list)
print("Final Analysis Results:", results)
