import flask
import urllib3
from flask import request
from flask_cors import CORS, cross_origin

urllib3.disable_warnings()
import random

import pymongo
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

application = flask.Flask(__name__)
cors = CORS(application, resources={r"/api/v1/*": {"origins": "*"}})
application.config['CORS_HEADERS'] = 'Content-Type'

from elasticsearch import Elasticsearch

limiter = Limiter(
    application,
    key_func=get_remote_address
)

import datetime

es = Elasticsearch(
    hosts = [{'host': 'vpc-debateev2-rh4osogaj2xrcjufnehcrce7hm.us-west-1.es.amazonaws.com', 'port': 443}],
    use_ssl = True
)

banner = '<div>This site is still in development. Email us at <a href="mailto:debatev.contact@gmail.com"> debatev.contact@gmail.com </a> if you have suggestions or click <a href="https://docs.google.com/forms/d/e/1FAIpQLSe3yVxCuqRkbBZeRAYZRa71RLnoPKUHTIxpu8-UkZ2L61b3WQ/viewform?fbzx=4735404296845035546"> here </a>to fill out a suggestion form</div>'
working = True
@cross_origin(origin='*',headers=['Content-Type','Authorization'])
@application.route('/api/v1/search', methods=['GET'])
def search():
    """
    Have rogas elasticsearch stuff here and search for a card and return tag, HTMLtext, download link
    """
    
    if 'q' in request.args:
        id = request.args['q']
    else:
        return "<h1>400</h1> <p>No query field provided. Please specify an query.</p>", 400

    if 'p' in request.args:
        page = int(request.args['p'])
    else:
        return "<h1>400</h1><p> No page field provided. Please specify a page.</p>", 400

    if 'year' in request.args and 'dtype' in request.args:
        year = request.args['year'].split(',')
        dtype = request.args['dtype']
        body = {"query":{"bool":{"must":[{"multi_match": {"query": id, "fields": ["tag", "cardHtml"]}},{"terms": {"year": year}}]}}}
        res = es.search(index= str(dtype), from_ = (int(page)*20), size = 20, doc_type="cards", track_total_hits = True, body = body)
    
    elif 'year' in request.args:
        year = request.args['year'].split(',')
        body = {"query":{"bool":{"must":[{"multi_match": {"query": id, "fields": ["tag", "cardHtml"]}},{"terms": {"year": year}}]}}}
        res = es.search(index= "_all", from_ = (int(page)*20), size = 20, doc_type="cards", track_total_hits = True, body=body)
    
    elif 'dtype' in request.args:
        dtype = request.args['dtype']
        res = es.search(index= str(dtype), doc_type="cards", from_ = (int(page)*20), track_total_hits = True, size = 20, body={"query": {"multi_match": {"query": id, "fields": [ "tag", "cardHtml" ]}}})
    else:
        res = es.search(index= "_all", doc_type="cards", from_ = (int(page)*20), track_total_hits = True, size = 20, body={"query": {"multi_match": {"query": id, "fields": [ "tag", "cardHtml" ]}}})
    
    tags = []
    results = {}
    i=0

    for doc in res['hits']['hits']:
        if doc['_source']['tag'] not in tags:
            tags.append(doc['_source']['cardHtml'])
            results['_source' + str(i)] = ('_id: ' + doc['_id'], doc['_source'], 'dtype: ' + doc['_index'])
            i+=1
        else:
            es.delete_by_query(index="_all", doc_type="cards", wait_for_completion = False, body={"query": {"match_phrase": {"_id": doc['_id']}}})
    
    return results

@cross_origin(origin='*',headers=['Content-Type','Authorization'])
@application.route('/api/v1/cards/<cardid>', methods=['GET'])
def getcards(cardid):
    """
    Use es module in order to get a certain card directly and return its details
    """
    
    res = es.search(index="_all", doc_type="cards", body={"query": {"match_phrase": {"_id": cardid}}})
    return res

@cross_origin(origin='*',headers=['Content-Type','Authorization'])
@application.route('/api/v1/cards/imfeelinglucky', methods=['GET'])
def randomcard():
    """
    Gets a random card from the database for "I'm feeling lucky"
    """
    results = {}
    res = es.search(index="_all", doc_type="cards", body={"size": 1, "query": {"function_score": {"functions": [{"random_score": {"seed": ''.join(["{}".format(random.randint(0, 9)) for num in range(0, 13)])}}]}}})
    for doc in res['hits']['hits']:
        results['_source'] = ('_id: ' + doc['_id'], doc['_source'], 'dtype: ' + doc['_index'])
    return results

@application.route('/', methods=['GET'])
def home():
    return '<h1>Welcome to the DebateEV API</h1><p>If you came here by accident, go to <a href="http://debatev.com">the main site</a></p>'

@application.route('/api/v1/makeReport', methods=['GET'])
@limiter.limit(["80 per day", "10 per hour"])
@cross_origin(origin='*',headers=['Content-Type','Authorization'])
def report():
    client = pymongo.MongoClient("mongodb+srv://reports:ksNxap14TuHwFUDh@cluster0.eoxkw.mongodb.net/reports?retryWrites=true&w=majority")
    db = client.reports
    reports = db.report

    if 'id' in request.args:
        cardid = request.args['id']
    else:
        return "<h1>400</h1> <p>No id field provided. Please specify a card id.</p>", 400

    if 'issue' in request.args:
        report = request.args['issue']
    else:
        return "<h1>400</h1> <p>No issue field provided. Please specify an issue.</p>", 400
    
    post = {
        "cardid": cardid,
        "report": report,
        "date": datetime.datetime.utcnow()
    }
    reports.insert_one(post)
    return "Success", 200

@application.errorhandler(404)
def page_not_found(e):
    return "<h1>404</h1><p>The resource could not be found.</p>", 404


@application.route('/api/v1/getBanner', methods=['GET'])
@cross_origin(origin='*',headers=['Content-Type','Authorization'])
def display_banner():
    if working:
        return banner
    else:
        return '<div>The website is currently under maintenance and some features may be disabled or may not be working correctly.</div>'

@application.route('/api/v1/maintenanceMode', methods=['GET'])
def maintenanceMode():
    global working
    if "api_key" in request.args:
        api_key = request.args['api_key']
        if api_key == "7CZwtblhHpQGVflBeCYM":
            if working:
                working = False
                return "<h1>The website has been put into maintance mode</h1><p>To switch back make another request to this endpoint</p>"
            else:
                working = True
                return "<h1>The website has been taken out of maintance mode</h1><p>To switch back make another request to this endpoint</p>"
        else:
            return "<h1>401</h1><p>Not authorized to make this request</p>", 401
    else:
        return "<h1>400</h1><p> No api_key field provided. Please provide an api key.</p>", 400


if __name__ == "__main__":
    application.debug = True
    application.run()
