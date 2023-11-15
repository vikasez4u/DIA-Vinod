# DIA

This project was generated with [Angular CLI](https://github.com/angular/angular-cli) version 16.0.2.

## Development server

Run `ng serve` for a dev server. Navigate to `http://localhost:4200/`. The application will automatically reload if you change any of the source files.

## Code scaffolding

Run `ng generate component component-name` to generate a new component. You can also use `ng generate directive|pipe|service|class|guard|interface|enum|module`.

## Build

Run `ng build` to build the project. The build artifacts will be stored in the `dist/` directory.

## Running unit tests

Run `ng test` to execute the unit tests via [Karma](https://karma-runner.github.io).

## Running end-to-end tests

Run `ng e2e` to execute the end-to-end tests via a platform of your choice. To use this command, you need to first add a package that implements end-to-end testing capabilities.

## Further help

To get more help on the Angular CLI use `ng help` or go check out the [Angular CLI Overview and Command Reference](https://angular.io/cli) page.
## Web Scraping and Gender Detection

This Python script performs web scraping on a given web page, extracts the text content, and detects gender-biased sentences using a list of gender-biased words. It also extracts alt texts from images on the web page and performs gender detection on the images using a pre-trained deep learning model.


### Dependencies

- Python 3.x
- requests
- beautifulsoup4
- pillow
- pytesseract
- tesseract
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
Gender: Male -0 ,Female -3
Image is Gender-biased

Image URL: https://www.example.com/image4.jpg
Gender: Male -5 , Female-0
Image is Gender-biased
```

Note: The gender detection results for images are based on a pre-trained deep learning model and may not be accurate in all cases.

### License

This project is licensed under the MIT License.
