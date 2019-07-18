from flask import Flask, request, abort, jsonify
import uuid
import pandas as pd
import profanity
from bulk_load import load_csv

app = Flask(__name__)


@app.route('/api/profanity/', methods=['POST'])
def check_profanity():
    threshold = 50
    if request.json and 'threshold' in request.json:
        threshold = request.json['threshold']

    if 'X-Language' in request.headers:
       language = request.headers.get('X-Language')

    if 'file' in request.files:
        return check_profanity_bulk(request.files['file'], threshold, language)

    if not request.json or not 'entityText' in request.json:
        abort(400)

    request_id = uuid.uuid4()
    review_text = request.json['entityText']

    profanity_scores = profanity.get_profanity_score(review_text, threshold, language)
    total_score = 0
    count = 0
    normalized_score = 0

    if len(profanity_scores) == 0:
        moderation_status = "accepted"
    else:
        moderation_status = "rejected"

    return jsonify({'requestId': request_id,
                    'normalizedScore': normalized_score,
                    'moderationStatus': moderation_status,
                    'body': profanity_scores}), 200


def check_profanity_bulk(csv_file, threshold, language):
    request_id = uuid.uuid4()
    reviews = load_csv(csv_file, 10)
    review_profanity_map = {}
    for review in reviews:
        review_profanity_map[review] = profanity.get_profanity_score(review, threshold, language)

    return jsonify({"requestId": request_id,
                    'body': review_profanity_map}), 200


@app.route('/api/language/', methods=['POST'])
def get_language():
    if not request.json or not 'entityText' in request.json:
        abort(400)

    request_id = uuid.uuid4()
    review_text = request.json['entityText']

    lang_response = {
        'text': review_text
    }

    # LANGUAGES = ['en', 'hi']
    # return LANGUAGES[0]
    return jsonify({'requestId': request_id,
                    'body': lang_response,
                    'lang': 'en'}), 200


@app.route('/')
def index():
    return '<h1>Hello world!</h1>'


if __name__ == '__main__':
    app.run(debug=True)
