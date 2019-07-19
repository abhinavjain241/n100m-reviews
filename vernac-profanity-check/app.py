from flask import Flask, request, abort, jsonify
import uuid
import pandas as pd
import profanity
from bulk_load import load_csv
from model_utils import predict
from clients import LivAI
from text_utils import preprocess, remove_emojis, filter_non_asci

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

    # TODO: Refactor to single line
    threshold = 50
    if 'threshold' in request.json:
        threshold = request.json['threshold']

    request_id = uuid.uuid4()
    review_text = request.json['entityText']

    prediction = predict(review_text)
    label = prediction[0][0]
    score = prediction[1][0]

    label = label.replace('__label__', '')

    liv_ai_client = LivAI()

    wc_list = []
    profanity_scores = {}

    if label == 'hie' or label == 'eng':
        # preproceseing
        review_text = remove_emojis(review_text)
        review_text = preprocess(review_text)
        # call WC
        liv_ai_client.generate_payload(review_text, "FOR_WC")
        wc_list = liv_ai_client.call('word_classifier')
        profanity_scores = profanity.get_profanity_score(review_text, threshold, label[:2])

    elif label == 'hin':
        # call REV
        liv_ai_client.generate_payload(review_text, "REV")
        converted_text = liv_ai_client.call('output')
        converted_text = filter_non_asci(converted_text)
        # converted_text = remove_emojis(converted_text)
        # converted_text = preprocess(converted_text)
        liv_ai_client.generate_payload(converted_text, "FOR_WC")
        wc_list = liv_ai_client.call('word_classifier')
        profanity_scores = profanity.get_profanity_score(converted_text, threshold, label[:2])
        # call WC now
    else:
        lang_response = {
            'label': "other",
            'text': "other language not supported"
        }
        return jsonify({'requestId': request_id,
                        'body': lang_response}), 200

    if len(profanity_scores) == 0:
        moderation_status = "accepted"
    else:
        moderation_status = "rejected"

    # wc_list = [for w in wc_list: if w == 1: 'en' else 'hi']

    lang_response = {
        'label': label,
        'score': score,
        'wc_list': wc_list,
        'moderation_status': moderation_status,
        'profanity_scores': profanity_scores
    }
    return jsonify({'requestId': request_id,
                    'body': lang_response}), 200


@app.route('/')
def index():
    return '<h1>Hello world!</h1>'


if __name__ == '__main__':
    app.run(debug=True)
