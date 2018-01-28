from flask import Flask, render_template
import requests
from urllib import parse
from requests_oauthlib import OAuth1
import http.client as httplib
import json

API_KEY = 'of1z9gzlrFWlNohnnJB9VWfQ2'
API_SECRET = 'f8gRmPzHDvCn4cLdd5doWY2vszlDzd4phgjA3joPmiUDLTHABI'
ACCESS_TOKEN = '3018938869-9ui88dzAu8UbMNcYD5zdZqJBuwSJsS61aAOLymE'
ACCESS_TOKEN_SECRET = 'ZbQXBayPluCWAdErv3FMVhxSht6V9mwEzVFbk9iWK03Pg'
TWEET_FORMAT = 'https://twitter.com/{screen_name}/status/{id_str}'

uri = 'westcentralus.api.cognitive.microsoft.com'
path = '/text/analytics/v2.0/sentiment'

accessKey = 'b0d9ff25c0c242b787254ca0953785c1'

def get_sentiment(tweets):
    l1 = []
    for i in range(len(tweets)):
        d = {}
        t1 = tweets[i]
        d['id'] = str(i)
        d['language'] = t1['language']
        d['text'] = t1['text']
        l1.append(d)
    documents = {'documents':l1}

    "Gets the sentiments for a set of documents and returns the information."

    headers = {'Ocp-Apim-Subscription-Key': accessKey}
    conn = httplib.HTTPSConnection (uri)
    body = json.dumps (documents)
    conn.request ("POST", path, body, headers)
    response = conn.getresponse ()
    scores = json.loads(response.read ().decode("utf-8"))['documents']
    # print (scores)
    for i in scores:
        index = int(i['id'])
        tweets[index]['score'] = i['score']
    return tweets


app = Flask(__name__)


@app.route('/')
def hello_world():
    response = requests.get(
        'https://api.twitter.com/1.1/search/tweets.json?q=%23disastermichelle&result_type=recent&count=20',
        auth=OAuth1(API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET))
    dict = response.json()
    tweets = []
    for i in dict['statuses']:
        t = {}
        t['text'] = i['text']
        t['user'] = i['user']['screen_name']
        t['place'] = i['place']
        t['retweet_count'] = i['retweet_count']
        t['language'] = i['metadata']['iso_language_code']
        t['url'] = TWEET_FORMAT.format(screen_name=i['user']['screen_name'],id_str=i['id_str'])
        tweets.append(t)
    tweets = get_sentiment(tweets)
    # print (type(tweets[0]))
    sorted_tweets = sorted(tweets,key=lambda k: k['score'])
    # print(json.dumps(sorted_tweets,indent=4))
    html_embed = []
    for s in sorted_tweets:
        response1 = requests.get(
            'https://publish.twitter.com/oembed?url=' + parse.quote_plus(s['url']),
            auth=OAuth1(API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET))
        dict1 = response1.json()
        html_embed.append(dict1['html'])
    # print (html_embed)
    # return '\n'.join(html_embed)
    return render_template('webpage.html',tweets=html_embed)

if __name__ == '__main__':
    app.run()
