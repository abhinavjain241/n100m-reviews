from flask import Flask, request, abort, jsonify
import uuid
import profanity

app = Flask(__name__)


@app.route('/api/profanity/', methods=['POST'])
def check_profanity():
    if not request.json or not 'entityText' in request.json:
        abort(400)

    request_id = uuid.uuid4()
    review_text = request.json['entityText']
    threshold = 50
    if 'threshold' in request.json:
        threshold = request.json['threshold']
    profanity_scores = profanity.get_profanity_score(review_text, threshold)
    return jsonify({'requestId': request_id, 'body': profanity_scores}), 200


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
    return jsonify({'requestId': request_id, 'body': lang_response, 'lang': 'en'}), 200


@app.route('/')
def index():
    return '<h1>Hello world!</h1>'


if __name__ == '__main__':
    app.run(debug=True)
