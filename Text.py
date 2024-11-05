from Text_processing_helper import extract_text_from_url, detect_biased_sentences, detect_geo_bias, extract_alt_text_from_url, detect_biased_sentences_in_alt_text, extract_text_from_images

def text_analysis_results(url, transaction_id, keyword_list):
    """
    Conducts comprehensive analysis on the text content, alt text, and images from a webpage 
    to detect gender and geographical bias.
    
    Parameters:
        url (str): URL of the page to analyze.
        transaction_id (int): Unique identifier for the database transaction.
        keyword_list (list): List of keywords to detect gender-biased terms.
        
    Returns:
        tuple: Contains results of biased text, biased alt text, and biased image text analysis.
    """
    # Extracts raw text content from the webpage's HTML
    text_content = extract_text_from_url(url)

    # Detects biased sentences within the main text content using specified keywords
    txt_results = detect_biased_sentences(text_content, keyword_list, 'biased_text_results', transaction_id)

    # Identifies geographical bias within the main text content
    text_countries,text_cities = detect_geo_bias(text_content, transaction_id, source='text')

    # Alt text extraction and analysis
    alt_texts = extract_alt_text_from_url(url)  # Retrieves alt text and image source pairs from images on the page
    
    # Detects gender-biased words within alt text descriptions and logs to the database
    alt_results = detect_biased_sentences_in_alt_text(alt_texts, keyword_list, transaction_id)
    print(f'alt results: {alt_results}')

    # Detects geographical bias within alt text descriptions
    alttext_countries,alttext_cities = detect_geo_bias(' '.join([alt[0] for alt in alt_texts]), transaction_id, source='alt_text')

    # Image text extraction and analysis
    img_results = extract_text_from_images(url, transaction_id, keyword_list)  # Extracts and analyzes text from images for bias

    # Returns results of text, alt text, and image bias analyses
    return txt_results,text_countries,text_cities, alt_results, alttext_countries,alttext_cities,img_results
