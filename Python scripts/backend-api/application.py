import flask
import urllib3
from flask import request
from flask_cors import CORS, cross_origin
import json
urllib3.disable_warnings()
import random
import requests
from htmldocx import HtmlToDocx

application = flask.Flask(__name__)
cors = CORS(application, resources={r"/api/v1/*": {"origins": "*"}})
application.config['CORS_HEADERS'] = 'Content-Type'
from elasticsearch import Elasticsearch



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
    amt = 20
    if 'q' in request.args:
        id = request.args['q']
    else:
        return "<h1>400</h1> <p>No query field provided. Please specify an query.</p>", 400

    if 'p' in request.args:
        page = int(request.args['p'])
    else:
        return "<h1>400</h1><p> No page field provided. Please specify a page.</p>", 400
    
    if 'amt' in request.args:
        if not int(request.args['amt']) > 70:
            amt = int(request.args['amt'])

    if 'year' in request.args and 'dtype' in request.args:
        year = request.args['year'].split(',')
        dtype = request.args['dtype']
        if not dtype == 'pf':
            body = {"query":{"bool":{"must":[{"multi_match": {"query": id, "fields": ["tag^2","cardHtml", "_id"], "operator": "and"}},{"terms": {"year": year}}]}}}
        else:
            body = {"query":{"bool":{"must":[{"multi_match": {"query": id, "fields": ["tag+cite^2","cardHtml"], "operator": "and"}},{"terms": {"year": year}}]}}}
        res = es.search(index= str(dtype), from_ = (int(page)*amt), size = amt, doc_type="cards", track_total_hits = True, body = body)
    
    elif 'year' in request.args:
        year = request.args['year'].split(',')
        body = {"query":{"bool":{"must":[{"multi_match": {"query": id, "fields": ["tag^2","cardHtml","_id"], "operator": "and"}},{"terms": {"year": year}}]}}}
        res = es.search(index= "openev,ld,college,hspolicy", from_ = (int(page)*amt), size = amt, doc_type="cards", track_total_hits = True, body=body)
    
    elif 'dtype' in request.args:
        dtype = request.args['dtype']
        if not dtype == 'pf':
            res = es.search(index= str(dtype), doc_type="cards", from_ = (int(page)*amt), track_total_hits = True, size = amt, body={"query": {"multi_match": {"query": id, "fields": [ "tag^2","cardHtml","_id"], "operator": "and"}}})
        else:
            res = es.search(index= str(dtype), doc_type="cards", from_ = (int(page)*amt), track_total_hits = True, size = amt, body={"query": {"multi_match": {"query": id, "fields": [ "tag+cite^2","cardHtml","_id"], "operator": "and"}}})
    else:
        res = es.search(index= "openev,ld,college,hspolicy", doc_type="cards", from_ = (int(page)*amt), track_total_hits = True, size = amt, body={"query": {"multi_match": {"query": id, "fields": [ "tag^2","cardHtml","_id"], "operator": "and"}}})
    
    tags = []
    cite = []
    results = {}
    i=0
    results['hits'] = res['hits']['total']['value']
    try:
        for doc in res['hits']['hits']:
            if doc['_source']['tag'] not in tags and doc['_source']['cite'] not in cite:
                tags.append(doc['_source']['tag']) 
                cite.append(doc['_source']['cite'])
                results['_source' + str(i)] = (doc['_id'], doc['_source'], 'dtype: ' + doc['_index'])
                i+=1
            else:
                es.delete_by_query(index="_all", doc_type="cards", wait_for_completion = False, body={"query": {"match_phrase": {"_id": doc['_id']}}})
    except KeyError:
        for doc in res['hits']['hits']:
            if doc['_source']['tag+cite'] not in cite:
                cite.append(doc['_source']['tag+cite'])
                results['_source' + str(i)] = (doc['_id'], doc['_source'], 'dtype: ' + doc['_index'])
                i+=1
            else:
                es.delete_by_query(index="_all", doc_type="cards", wait_for_completion = False, body={"query": {"match_phrase": {"_id": doc['_id']}}})

    return results

@cross_origin(origin='*',headers=['Content-Type','Authorization'])
@application.route('/api/v1/autocomplete', methods=['GET'])
def autocomplete():
    """
    Have rogas elasticsearch stuff here and search for a card and return tag, HTMLtext, download link
    """
    amt = 5
    if 'q' in request.args:
        id = request.args['q']
    else:
        return "<h1>400</h1> <p>No query field provided. Please specify an query.</p>", 400

    if 'year' in request.args and 'dtype' in request.args:
        year = request.args['year'].split(',')
        dtype = request.args['dtype']
        if not dtype == 'pf':
            body = {"query":{"bool":{"must":[{"multi_match": {"query": id, "fields": ["tag^2","cardHtml", "_id"], "operator": "and"}},{"terms": {"year": year}}]}}}
        else:
            body = {"query":{"bool":{"must":[{"multi_match": {"query": id, "fields": ["tag+cite^2","cardHtml"], "operator": "and"}},{"terms": {"year": year}}]}}}
        res = es.search(index= str(dtype), from_ = (int(0)*amt), size = amt, doc_type="cards", track_total_hits = True, body = body)
    
    elif 'year' in request.args:
        year = request.args['year'].split(',')
        body = {"query":{"bool":{"must":[{"multi_match": {"query": id, "fields": ["tag^2","cardHtml","_id"], "operator": "and"}},{"terms": {"year": year}}]}}}
        res = es.search(index= "openev,ld,college,hspolicy", from_ = (int(0)*amt), size = amt, doc_type="cards", track_total_hits = True, body=body)
    
    elif 'dtype' in request.args:
        dtype = request.args['dtype']
        if not dtype == 'pf':
            res = es.search(index= str(dtype), doc_type="cards", from_ = (int(0)*amt), track_total_hits = True, size = amt, body={"query": {"multi_match": {"query": id, "fields": [ "tag^2","cardHtml","_id"], "operator": "and"}}})
        else:
            res = es.search(index= str(dtype), doc_type="cards", from_ = (int(0)*amt), track_total_hits = True, size = amt, body={"query": {"multi_match": {"query": id, "fields": [ "tag+cite^2","cardHtml","_id"], "operator": "and"}}})
    else:
        res = es.search(index= "openev,ld,college,hspolicy", doc_type="cards", from_ = (int(0)*amt), track_total_hits = True, size = amt, body={"query": {"multi_match": {"query": id, "fields": [ "tag^2","cardHtml","_id"], "operator": "and"}}})
        
    tags = []
    cite = []
    results = {}
    i=0
    try:
        for doc in res['hits']['hits']:
            if doc['_source']['tag'] not in tags and doc['_source']['cite'] not in cite:
                tags.append(doc['_source']['tag'])
                cite.append(doc['_source']['cite'])
                results['_source' + str(i)] = (doc['_id'], doc['_source']['tag'], 'dtype: ' + doc['_index'])
                i+=1
            else:
                es.delete_by_query(index="_all", doc_type="cards", wait_for_completion = False, body={"query": {"match_phrase": {"_id": doc['_id']}}})
    except KeyError:
        for doc in res['hits']['hits']:
            if doc['_source']['tag+cite'] not in cite:
                cite.append(doc['_source']['tag+cite'])
                results['_source' + str(i)] = (doc['_id'], doc['_source'], 'dtype: ' + doc['_index'])
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
@application.route('/api/v1/saved', methods=['GET'])
def saved():
    if 'q' in request.args:
        cardid = request.args['q']
    else:
        return "<h1>400</h1> <p>No query field provided. Please specify an query.</p>", 400
    cardid = cardid.split(',')
    search_arr = []
    for i in range(len(cardid)):
        search_arr.append({'index': '_all'})
        search_arr.append({"query": {"match_phrase": {"_id": cardid[i]}}})
    req = ''
    for each in search_arr:
        req += '%s \n' %json.dumps(each)
    res = es.msearch(body = req)
    x = {}
    i = 0
    for card in res['responses']:
        x['_source' + str(i)] = (card['hits']['hits'][0]['_id'], card['hits']['hits'][0]['_source'], 'dtype: ' + card['hits']['hits'][0]['_index'])
        i += 1
    return x

@cross_origin(origin='*',headers=['Content-Type','Authorization'])
@application.route('/api/v1/cards/imfeelinglucky', methods=['GET'])
def randomcard():
    """
    Gets a random card from the database for "I'm feeling lucky"
    """
    results = {}
    res = es.search(index="openev,ld,college,hspolicy", doc_type="cards", body={"size": 1, "query": {"function_score": {"functions": [{"random_score": {"seed": ''.join(["{}".format(random.randint(0, 9)) for num in range(0, 13)])}}]}}})
    for doc in res['hits']['hits']:
        results['_source'] = ( doc['_id'], doc['_source'], 'dtype: ' + doc['_index'])
    return results

@application.route('/', methods=['GET'])
def home():
    return '<h1>Welcome to the DebateEV API</h1><p>If you came here by accident, go to <a href="http://debatev.com">the main site</a></p>'



@application.errorhandler(404)
def page_not_found(e):
    return "<h1>404</h1><p>The resource could not be found.</p>", 404

@application.route('/api/v1/download', methods=['GET'])
@cross_origin(origin='*',headers=['Content-Type','Authorization'])
def download():
    if 'q' in request.args:
        cardid = request.args['q']
    else:
        return "<h1>400</h1> <p>No query field provided. Please specify an query.</p>", 400
    cardid = cardid.split(',')
    search_arr = []
    for i in range(len(cardid)):
        search_arr.append({'index': '_all'})
        search_arr.append({"query": {"match_phrase": {"_id": cardid[i]}}})
    req = ''
    for each in search_arr:
        req += '%s \n' %json.dumps(each)
    res = es.msearch(body = req)
    a = ""
    for card in res['responses']:
        a += card['hits']['hits'][0]['_source']['cardHtml']
    new_parser = HtmlToDocx()
    
    docx = new_parser.parse_html_string(a)
    docx.save('test.docx')
    return flask.send_file('test.docx')


    
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

@application.route('/api/v1/analytics', methods=['GET'])
def analytics():
    res = requests.get('https://papertrailapp.com/api/v1/events/search.json?q=search', headers = {"X-Papertrail-Token": "d62sBTc9nkUTf9je0c"})
    data = {}
    searches = {}
    res = json.loads(res.content)
    for event in res['events']:
        data[event['display_received_at']] = ("search: " + event['message'])

    endindex = 0
    total = 0
    while endindex < len(str(data))-500:
        firstindex = str(data).find('/search/', endindex)
        secondindex = str(data).find('/', firstindex+6)
        endindex = str(data).find('"', secondindex)
        searches[str(total)] = (str(data)[secondindex:endindex])
        total+=1
    return searches
    
if __name__ == "__main__":
    application.debug = True
    application.run()
