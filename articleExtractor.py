from flask import Flask, request
from flask_restful import Resource, Api
from sqlalchemy import create_engine
from json import dumps
from flask import jsonify
from newspaper import Article
import requests
from flask_cors import CORS, cross_origin

############################################################################################################################################################
## curl -i -H "Content-Type: application/json" -X POST -d https://www.burytimes.co.uk/news/17359742.cocaine-tragedy-of-loving-mother/ 127.0.0.1:5002/hello
############################################################################################################################################################

app = Flask(__name__)
api = Api(app)
CORS(app, support_credentials=True)

@app.route('/hello', methods=['POST'])
@cross_origin(supports_credentials=True)
def test():

    url = request.form.get('url')

    article = Article(url)

    article.download()

    article.parse()

    return jsonify(title=article.title,
                   publish_date=article.publish_date,
                   authors=article.authors,
                   content=article.text,
                   keywords=article.keywords,
                   summary=article.summary)


if __name__ == '__main__':
    app.run(port='5002')