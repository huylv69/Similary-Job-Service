from flask import Flask, request, Response
from flask import json
from pyvi import ViTokenizer, ViPosTagger

app = Flask(__name__)


def jaccard_similarity(list1, list2):
    intersection = len(list(set(list1).intersection(list2)))
    print(list(set(list1).intersection(list2)))
    union = (len(list1) + len(list2)) - intersection
    return float(intersection / union)


def normalize_text(string):
    string = string.lower()
    return string.strip()


def tokenize(string):
    text_token = ViTokenizer.tokenize(string).split()
    return text_token


@app.route('/')
def hello_world():
    title = tokenize(normalize_text(u"Trường đại học bách khoa hà nội"))

    title2 = tokenize(normalize_text(u"Trường đại học bách khoa Hà nội"))
    print(jaccard_similarity(title, title2))

    return 'Job Recommend System!'


@app.route('/messages', methods=['POST'])
def api_message():
    if request.headers['Content-Type'] == 'text/plain':
        return "Text Message: " + request.data

    elif request.headers['Content-Type'] == 'application/json':
        return "JSON Message: " + json.dumps(request.json)

    elif request.headers['Content-Type'] == 'application/octet-stream':
        f = open('./binary', 'wb')
        f.write(request.data)
        f.close()
        return "Binary message written!"
    else:
        return "415 Unsupported Media Type ;)"


@app.route('/hello', methods=['GET'])
def api_hello():
    data = {
        'hello': 'world',
        'number': 3
    }
    js = json.dumps(data)

    resp = Response(js, status=200, mimetype='application/json')
    resp.headers['Link'] = 'http://luisrei.com'

    return resp


if __name__ == '__main__':
    app.run()
