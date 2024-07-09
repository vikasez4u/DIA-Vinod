from flask import Flask, request, jsonify
from flask_cors import CORS
from . import backend_logic, diadb

app = Flask(__name__)
CORS(app)  # This allows cross-origin requests for development purposes

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.json
    url = data['url']
    result = backend_logic.web_scrape_and_extract_entities(url)
    return jsonify(result)

@app.route('/save_biased_word', methods=['POST'])
def save_biased_word():
    data = request.json
    name = data["name"]
    gender_id = data["genderId"]
    result = diadb.biased_word_save(gender_id, name)
    return jsonify({'result': result})

# Add more routes as needed...

if __name__ == '__main__':
    app.run(debug=True)
