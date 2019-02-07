from flask import Flask, request
from flask_restful import Resource, Api
from sqlalchemy import create_engine
from json import dumps
from flask import jsonify
from newspaper import Article
import nltk
import requests
from flask_cors import CORS, cross_origin

############################################################################################################################################################
## curl -i -H "Content-Type: application/json" -X POST -d https://www.burytimes.co.uk/news/17359742.cocaine-tragedy-of-loving-mother/ 127.0.0.1:5002/hello
############################################################################################################################################################

app = Flask(__name__)
api = Api(app)
CORS(app, support_credentials=True)

db_connect = create_engine('sqlite:///test.db')

class whitelistedSites(Resource):
    def get(self):
        conn = db_connect.connect()
        query = conn.execute("select * from whitelist")
        return {'whitelistedSites': [i[1] for i in query.cursor.fetchall()]}

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

class keywords(Resource):
    def get(self):
        conn = db_connect.connect()
        query = conn.execute("select * from keywords")
        return {'keywords': [i[1] for i in query.cursor.fetchall()]}

api.add_resource(whitelistedSites, '/whitelistedSites')
api.add_resource(satiricalSites, '/satiricalSites')
api.add_resource(blacklistedSites, '/blacklistedSites')

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

@app.route('/hello', methods=['POST'])
@cross_origin(supports_credentials=True)
def test():

    nltk.download('punkt')

    url = request.form.get('url')

    article = Article(url)

    article.download()

    article.parse()

    article.nlp()

    return jsonify(title=article.title,
                   publishDate=article.publish_date,
                   authors=article.authors,
                   content=article.text,
                   keywords=article.keywords,
                   summary=article.summary)


if __name__ == '__main__':
    app.run(port='5002')