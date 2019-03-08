from flask import Flask, request
from flask_restful import Resource, Api
from sqlalchemy import create_engine
from json import dumps
from flask import jsonify
from newspaper import Article
import nltk
import requests
from flask_cors import CORS, cross_origin

app = Flask(__name__)
api = Api(app)
CORS(app, support_credentials=True)

db_connect = create_engine('sqlite:///test.db')

class whitelistedSites(Resource):
    def get(self):
        conn = db_connect.connect()
        query = conn.execute("select * from whitelist")
        return {'whitelistedSites': [i[1] for i in query.cursor.fetchall()]}

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

class blacklistedSites(Resource):
    def get(self):
        conn = db_connect.connect()
        query = conn.execute("select * from blacklist")
        return {'blacklistedSites': [i[1] for i in query.cursor.fetchall()]}

class fakeNewsSites(Resource):
    def get(self):
        conn = db_connect.connect()
        query = conn.execute("select * from fake")
        return {'fakeNewsSites': [i[1] for i in query.cursor.fetchall()]}

class keywords(Resource):
    def get(self):
        conn = db_connect.connect()
        query = conn.execute("select * from keywords")
        return {'keywords': [i[1] for i in query.cursor.fetchall()]}

api.add_resource(whitelistedSites, '/whitelistedSites')
api.add_resource(biasedSites, '/biasedSites')
api.add_resource(satiricalSites, '/satiricalSites')
api.add_resource(blacklistedSites, '/blacklistedSites')
api.add_resource(fakeNewsSites, '/fakeNewsSites')

api.add_resource(keywords, '/keywords')

@app.route('/keywords', methods=['POST'])
@cross_origin(supports_credentials=True)
def test5():

    f = []

    text = request.form.get('text')

    conn = db_connect.connect()

    query = conn.execute("select * from keywords")

    for i in query.cursor.fetchall():

        if i[1] in text:

            f.append(i)

    result = {'keywords': [i[1] for i in f]}

    return jsonify(result)

@app.route('/whitelistedSites', methods=['POST'])
@cross_origin(supports_credentials=True)
def test2():

    url = request.form.get('url')

    conn = db_connect.connect()

    query = conn.execute("select * from whitelist where ? LIKE '%' || ADDRESS || '%'", (str(url)))

    result = {'whitelistedSites': [i[1] for i in query.cursor.fetchall()]}
    return jsonify(result)

@app.route('/biasedSites', methods=['POST'])
@cross_origin(supports_credentials=True)
def test9():

    url = request.form.get('url')

    conn = db_connect.connect()

    query = conn.execute("select * from biaslinks where ? LIKE '%' || ADDRESS || '%'", (str(url)))

    result = {'biasedSites': [i[1] for i in query.cursor.fetchall()]}
    return jsonify(result)

@app.route('/satiricalSites', methods=['POST'])
@cross_origin(supports_credentials=True)
def test3():

    url = request.form.get('url')

    conn = db_connect.connect()

    query = conn.execute("select * from satirical where ? LIKE '%' || ADDRESS || '%'", (str(url)))

    result = {'satiricalSites': [i[1] for i in query.cursor.fetchall()]}
    return jsonify(result)

@app.route('/blacklistedSites', methods=['POST'])
@cross_origin(supports_credentials=True)
def test4():

    url = request.form.get('url')

    conn = db_connect.connect()

    query = conn.execute("select * from blacklist where ? LIKE '%' || ADDRESS || '%'", (str(url)))

    result = {'blacklistedSites': [i[1] for i in query.cursor.fetchall()]}
    return jsonify(result)

@app.route('/fakeNewsSites', methods=['POST'])
@cross_origin(supports_credentials=True)
def test6():

    url = request.form.get('url')

    conn = db_connect.connect()

    query = conn.execute("select * from fake where ? LIKE '%' || ADDRESS || '%'", (str(url)))

    result = {'fakeNewsSites': [i[1] for i in query.cursor.fetchall()]}
    return jsonify(result)

@app.route('/hello', methods=['POST'])
@cross_origin(supports_credentials=True)
def extract_entities():
    nltk.download('punkt')

    nltk.download('averaged_perceptron_tagger')
    nltk.download('maxent_ne_chunker')
    nltk.download('words')


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