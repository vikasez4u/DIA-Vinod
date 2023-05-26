# DIA
## Web Scraping and Gender Detection

This Python script performs web scraping on a given web page, extracts the text content, and detects gender-biased sentences using a list of gender-biased words. It also extracts alt texts from images on the web page and performs gender detection on the images using a pre-trained deep learning model.

### Dependencies

- Python 3.x
- requests
- beautifulsoup4
- pillow
- pytesseract
- pandas
- numpy
- cv2
- imghdr
- deepface

### Usage

1. Install the required dependencies listed above.
2. Download the gender_biased_words.xlsx file and place it in the same directory as the script.
3. Run the script using the command `python web_scraping_gender_detection.py`.
4. Enter the URL of the web page when prompted.
5. The script will perform web scraping, extract text content, detect gender-biased sentences, and provide the results.

Note: The script assumes the presence of the gender_biased_words.xlsx file in the same directory. Make sure to download and place it in the correct location.

### Examples

Example 1:
```
Enter the URL of the webpage: https://www.example.com
Gender-biased sentences found in the text content:
1. The man was the CEO of the company.
2. She is a nurse.

Gender detection results for images:
Image URL: https://www.example.com/image1.jpg
Gender: Male

Image URL: https://www.example.com/image2.jpg
Gender: Female
```

Example 2:
```
Enter the URL of the webpage: https://www.example.com/blog
No gender-biased sentences found in the text content.

Gender detection results for images:
Image URL: https://www.example.com/image3.jpg
Gender: Male

Image URL: https://www.example.com/image4.jpg
Gender: Female
```

Note: The gender detection results for images are based on a pre-trained deep learning model and may not be accurate in all cases.

### License

This project is licensed under the MIT License.
