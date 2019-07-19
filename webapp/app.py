from flask import Flask, request, abort, jsonify, render_template, redirect, url_for
import uuid
import profanity
from bulk_load import load_csv
from model_utils import predict
from clients import LivAI
from text_utils import preprocess, remove_emojis, filter_non_asci

app = Flask(__name__)


@app.route('/api/profanity/', methods=['POST'])
def check_profanity():
    threshold = 75
    language = 'en'
    if request.json and 'threshold' in request.json:
        threshold = request.json['threshold']

    if 'X-Language' in request.headers:
        language = request.headers.get('X-Language')

    if 'file' in request.files:
        return check_profanity_bulk(request.files['file'], threshold)

    if not request.json or not 'entityText' in request.json:
        abort(400)

    request_id = uuid.uuid4()
    review_text = request.json['entityText']

    profanity_scores = []

    for word in review_text.split(" "):
        profanity_scores.append(profanity.get_profanity_score(word, threshold, language))

    if len(profanity_scores) == 0:
        moderation_status = "accepted"
    else:
        moderation_status = "rejected"

    return jsonify({'requestId': request_id,
                    'moderationStatus': moderation_status,
                    'body': profanity_scores}), 200


def check_profanity_bulk(csv_file, threshold):
    request_id = uuid.uuid4()
    nrows = 10
    if 'X-Rows' in request.headers:
        nrows = int(request.headers.get('X-Rows'))
    reviews = load_csv(csv_file, nrows)
    # review_profanity_map = {}
    review_profanity_list = []

    filename = str(request_id) + '.csv'
    print(threshold)
    with open('output/' + filename, 'a+') as f:
        for review in reviews:
            response = get_response(review, threshold)
            status = response.get('moderation_status')
            # print(response.get('profanity_scores'))
            # for score in response.get('profanity_scores'):
            #     print(score)
            if (status == "rejected"):
                is_profane = "yes"
            elif (status == "accepted"):
                is_profane = "no"
            else:
                is_profane = "NAN"
            f.write("%s\n" % is_profane)
            print(review, is_profane)
            # review_profanity_list.append((review, is_profane))
            # review_profanity_list.append(is_profane)

    # print(len(review_profanity_list))
    # filename = str(request_id) + '.csv'
    # with open('output/' + filename , 'w') as f:
    #     for item in review_profanity_list:
    #         # f.write("%s, %s\n" % (item[0], item[1]))
    #         f.write("%s\n" % item)

    return jsonify({"requestId": request_id,
                    'body': "Successfully dumped to {}".format(filename)}), 200


@app.route('/api/moderation/', methods=['POST'])
def moderation():
    request_id = uuid.uuid4()
    if not request.json or not 'entityText' in request.json:
        abort(400)

    threshold = 50
    if 'threshold' in request.json:
        threshold = int(request.json['threshold'])

    review_text = request.json['entityText']

    response = get_response(review_text, threshold)

    return jsonify({'requestId': request_id,
                    'body': response}), 200


@app.route('/api/language/', methods=['POST'])
def get_language():
    request_id = uuid.uuid4()
    if not request.json or 'entityText' not in request.json:
        abort(400)
    review_text = request.json['entityText']

    label, score = predict_language(review_text)

    response = {
        'label': label,
        'score': score
    }
    return jsonify({'requestId': request_id,
                    'body': response}), 200


@app.route('/', methods=['POST'])
def my_form_post():
    review_text = request.form['review_text']
    threshold = int(request.form['threshold'])

    return get_response(review_text, threshold)


def get_response(review_text, threshold):
    label, score = predict_language(review_text)

    lang_response = {
        'label': "other",
        'text': "other language not supported"
    }

    if score < 0.5:
        return lang_response
    liv_ai_client = LivAI()

    wc_list = []
    profanity_scores = []

    print(label)
    if label != 'hie' and label != 'eng' and label != 'hin':
        return lang_response

    if label == 'hie' or label == 'eng':
        review_text = remove_emojis(review_text)
        review_text = preprocess(review_text)
        # call WC
        liv_ai_client.generate_payload(review_text, "FOR_WC")

    elif label == 'hin':
        liv_ai_client.generate_payload(review_text, "REV")
        converted_text = liv_ai_client.call('output')
        converted_text = filter_non_asci(converted_text)
        # converted_text = remove_emojis(converted_text)
        # converted_text = preprocess(converted_text)
        liv_ai_client.generate_payload(converted_text, "FOR_WC")

    wc_list = liv_ai_client.call('word_classifier')
    for word in wc_list:
        match_list = profanity.get_profanity_score(word[0], threshold, 'en' if word[1] == 1 else 'hi')
        if match_list and len(match_list) > 0:
            profanity_scores.append(match_list)

    moderation_status = "accepted"

    for profanity_map in profanity_scores:
        if len(profanity_map) > 0:
            moderation_status = "rejected"
            break

    lang_response = {
        'label': label,
        'score': score,
        'wc_list': wc_list,
        'moderation_status': moderation_status,
        'profanity_scores': profanity_scores
    }
    return lang_response


def predict_language(review_text):
    review_text = remove_emojis(review_text)
    review_text = preprocess(review_text)
    prediction = predict(review_text)
    label = prediction[0][0]
    score = prediction[1][0]
    label = label.replace('__label__', '')
    return label, score


@app.route('/')
def index():
    return render_template('my-form.html')
    # return '<h1>Hello world!</h1>'


if __name__ == '__main__':
    app.run(debug=True)
