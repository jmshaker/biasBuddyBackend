import flask
import nltk
import nltk.data
import requests
import json

from flask import Flask, request, jsonify
from flask_restful import Resource, Api
from sqlalchemy import create_engine
from json import dumps
from newspaper import Article
from nltk import tokenize
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from flask_cors import CORS, cross_origin

nltk.download('vader_lexicon')

app = Flask(__name__)
api = Api(app)
CORS(app, support_credentials=True)

db_connect = create_engine('sqlite:///test2.db')

class biasedSites(Resource):
    def get(self):
        conn = db_connect.connect()
        query = conn.execute("select * from biaslinks")
        return {'biasedSites': [i[1] for i in query.cursor.fetchall()]}

class satiricalSites(Resource):
    def get(self):
        conn = db_connect.connect()
        query = conn.execute("select * from satirical")
        return {'satiricalSites': [i[1] for i in query.cursor.fetchall()]}

class fakeNewsSites(Resource):
    def get(self):
        conn = db_connect.connect()
        query = conn.execute("select * from fake")
        return {'fakeNewsSites': [i[1] for i in query.cursor.fetchall()]}

class sentiment(Resource):
    def get(self):
        conn = db_connect.connect()
        query = conn.execute("select * from keywords")
        return {'keywords': [i[1] for i in query.cursor.fetchall()]}

class keywords(Resource):
    def get(self):
        conn = db_connect.connect()
        query = conn.execute("select * from keywords")
        return {'keywords': [i[1] for i in query.cursor.fetchall()]}

api.add_resource(biasedSites, '/biasedSites')
api.add_resource(satiricalSites, '/satiricalSites')
api.add_resource(fakeNewsSites, '/fakeNewsSites')
api.add_resource(keywords, '/keywords')

@app.route('/sentences', methods=['POST'])
@cross_origin(supports_credentials=True)
def test15():

    content = request.form.get('content')

    tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')

    sentences = tokenizer.tokenize(content)

    for sentence in sentences:

        if '\n\n' in sentence:
            
            sentence = sentence.replace('\n\n', ' ')

    ss = {'sentences': [sentence for sentence in sentences]}

    return jsonify(ss)

@app.route('/sentiment', methods=['POST'])
@cross_origin(supports_credentials=True)
def test10():

    content = request.form.get('content')

    tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')

    sentences = tokenizer.tokenize(content)

    sid = SentimentIntensityAnalyzer()

    for sentence in sentences:

        if '\n\n' in sentence:
            
            sentence = sentence.replace('\n\n', ' ')

    x = {'sentiments': [sid.polarity_scores(sentence) for sentence in sentences]}

    return jsonify(x)

@app.route('/keywords', methods=['POST'])
@cross_origin(supports_credentials=True)
def test5():

    f = []

    text = request.form.get('text')

    conn = db_connect.connect()

    query = conn.execute("select * from keywords")

    for i in query.cursor.fetchall():

        if i[0] in text.split():

            f.append(i)

    result = {'keywords': [i[0] for i in f]}

    return jsonify(result)

@app.route('/keywordsType', methods=['POST'])
@cross_origin(supports_credentials=True)
def test20():

    types = []

    words = request.form.get('words')

    words = json.loads(words)

    conn = db_connect.connect()

    for word in words:

        query = conn.execute("select TYPE from keywords WHERE WORD = \"%s\";" %(word))
        
        response = [i[0] for i in query.cursor.fetchall()]

        types.append(response)

    return jsonify(types)    

@app.route('/keywordsDef', methods=['POST'])
@cross_origin(supports_credentials=True)
def test19():

    definitions = []

    words = request.form.get('words')

    words = json.loads(words)

    conn = db_connect.connect()

    for word in words:

        query = conn.execute("select DEFINITION from keywords WHERE WORD = \"%s\";" %(word))
        
        response = [i[0] for i in query.cursor.fetchall()]

        definitions.append(response)

    return jsonify(definitions)

@app.route('/biasedSites', methods=['POST'])
@cross_origin(supports_credentials=True)
def test9():

    url = request.form.get('url')

    conn = db_connect.connect()

    query = conn.execute("select * from biaslinks where ? LIKE '%' || ADDRESS || '%'", (str(url)))

    result = {'biasedSites': [i[0] for i in query.cursor.fetchall()]}

    return jsonify(result)

@app.route('/satiricalSites', methods=['POST'])
@cross_origin(supports_credentials=True)
def test3():

    url = request.form.get('url')

    conn = db_connect.connect()

    query = conn.execute("select * from satirical where ? LIKE '%' || ADDRESS || '%'", (str(url)))

    result = {'satiricalSites': [i[0] for i in query.cursor.fetchall()]}

    return jsonify(result)

@app.route('/fakeNewsSites', methods=['POST'])
@cross_origin(supports_credentials=True)
def test6():

    url = request.form.get('url')

    conn = db_connect.connect()

    query = conn.execute("select * from fake where ? LIKE '%' || ADDRESS || '%'", (str(url)))

    result = {'fakeNewsSites': [i[0] for i in query.cursor.fetchall()]}

    return jsonify(result)

@app.route('/hello', methods=['POST'])
@cross_origin(supports_credentials=True)
def extract_entities():

    url = request.form.get('url')

    article = Article(url)

    article.download()

    article.parse()

    article.nlp()

    people = []
    organisations = []
    GPE = []

    for sent in nltk.sent_tokenize(article.text):
        for chunk in nltk.ne_chunk(nltk.pos_tag(nltk.word_tokenize(sent))):

            if hasattr(chunk, 'label'):

                print(chunk.label(), ' '.join(c[0] for c in chunk.leaves()))

                if (chunk.label() == 'PERSON'):
                    people.append(' '.join(c[0] for c in chunk.leaves()))
                else:
                    if (chunk.label() == 'ORGANIZATION'):
                        organisations.append(' '.join(c[0] for c in chunk.leaves()))
                    else:
                        if (chunk.label() == 'GPE'):
                            GPE.append(' '.join(c[0] for c in chunk.leaves()))


    try:
        publishedDate = str(article.publish_date.date())
    except:
        publishedDate = "null"

    return jsonify(title=article.title,
                   publishDate=publishedDate,
                   authors=article.authors,
                   content=article.text,
                   keywords=article.keywords,
                   summary=article.summary,
                   people=people,
                   organisations=organisations,
                   gpe=GPE)

if __name__ == '__main__':
    app.run(port='5002')

    nltk.download('punkt')

    nltk.download('averaged_perceptron_tagger')
    nltk.download('maxent_ne_chunker')
    nltk.download('words')

    nltk.downloader.download('vader_lexicon')