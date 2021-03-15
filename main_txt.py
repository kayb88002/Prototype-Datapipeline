from flask import Flask, jsonify
from flask import request
from flask_cors import CORS, cross_origin
import tweepy
import re
from  textblob import TextBlob 
from gensim.summarization.summarizer import summarize
from gensim.summarization.textcleaner import split_sentences
from newspaper import Article     
from googlesearch import search
import os
from newspaper import Article
import requests
from bs4 import BeautifulSoup
import re
import time
import urllib.parse
from urllib.parse import urlparse
import mysql.connector
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize 
import nltk 
from newsio import news_head
import heapq
import mysql.connector
import wikipediaapi
import spacy
from itertools import combinations
import networkx as nx
import matplotlib.pyplot as plt
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from summarizer import Summarizer 

model=Summarizer()

nlp = spacy.load('en_core_web_lg')

mysqlDB=mysql.connector.connect(host="52.207.228.134",user="new_kapil",password="password",database='Datadash')
myDB=mysqlDB.cursor()

def f(seq): # Order preserving unique sentences - sometimes duplicate sentences appear in summaries
    seen = set()
    return [x for x in seq if x not in seen and not seen.add(x)]    


def summary(x, perc): #x input document, perc: percentage of the original document to keep
    if len(split_sentences(x)) > 100:
        test_summary = summarize(x, ratio = perc, split=True)
        test_summary = '\n'.join(map(str, f(test_summary)))
    else:
        test_summary = x
    return test_summary




def clean(text):
    text = re.sub(r'\[[0-9]*\]', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return text

def text_clean(text):
    for k in text.split("\n"):
        clean=(re.sub(r"[^a-zA-Z0-9]+", ' ', k))
    return clean



def wiki(query):
    wiki_wiki = wikipediaapi.Wikipedia('en')
    page = wiki_wiki.page(query)
    return page.summary


def googleSearch(query):
    g_clean = [ ] 
    url = 'https://www.google.com/search?client=ubuntu&channel=fs&q={}&ie=utf-8&oe=utf-8'.format(query)
    try:
            html = requests.get(url)
            if html.status_code==200:
                soup = BeautifulSoup(html.text, 'lxml')
                a = soup.find_all('a') 
                for i in a:
                    k = i.get('href')
                    try:
                        m = re.search("(?P<url>https?://[^\s]+)", k)
                        n = m.group(0)
                        rul = n.split('&')[0]
                        domain = urlparse(rul)
                        if(re.search('google.com', domain.netloc)):
                            continue
                        else:
                            g_clean.append(rul)
                    except:
                        continue
    except Exception as ex:
        print(str(ex))
    finally:
        return g_clean


def cleantxt(article_text):
    article_text = re.sub(r'\[[0-9]*\]', ' ', article_text)
    article_text = re.sub(r'\s+', ' ', article_text)

    # Removing special characters and digits
    formatted_article_text = re.sub('[^a-zA-Z]', ' ', article_text )
    formatted_article_text = re.sub(r'\s+', ' ', formatted_article_text)
    sentence_list = nltk.sent_tokenize(article_text)

    stopwords = nltk.corpus.stopwords.words('english')

    word_frequencies = {}

    for word in nltk.word_tokenize(formatted_article_text):
        if word not in stopwords:
            if word not in word_frequencies.keys():
                word_frequencies[word] = 1
            else:
                word_frequencies[word] += 1

    maximum_frequncy = max(word_frequencies.values())

    for word in word_frequencies.keys():
        word_frequencies[word] = (word_frequencies[word]/maximum_frequncy)
    
    sentence_scores = {}
    for sent in sentence_list:
        for word in nltk.word_tokenize(sent.lower()):
            if word in word_frequencies.keys():
                if len(sent.split(' ')) < 50:
                    if sent not in sentence_scores.keys():
                        sentence_scores[sent] = word_frequencies[word]
                    else:
                        sentence_scores[sent] += word_frequencies[word]

        
    summary_sentences = heapq.nlargest(50,sentence_scores, key=sentence_scores.get)
    summarize =' '.join(summary_sentences)
    return summarize

    
def search(links):
    article_text=''
    
    for link in links:
        res = requests.get(link)
        html_page = res.content
        soup = BeautifulSoup(html_page, 'html.parser')
        t=soup.find_all('p')
        for summary in t:
            article_text += summary.text
    return article_text

time.sleep(10)

def pre(query):
    myDB.execute("SELECT Summary FROM Data_pi WHERE Topic_Search =%s",[query])
    result=myDB.fetchall()
    for j in result:
        respond=j[0]
    return respond



app = Flask(__name__)
CORS(app)


@app.route('/', methods=['GET'])

def summary():
    query= request.args.get("summary")
    links=googleSearch(query)
    link_list=links[1:3]
    headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.104 Safari/537.36'}

    stored_text=''

    for link in link_list:
        res = requests.get(link,headers=headers)
        html_page = res.content
        soup = BeautifulSoup(html_page, 'html.parser')
        t=soup.find_all('p')
        for summary in t:
            stored_text += summary.text

    time.sleep(10)


    source=[str(j) for j in links]
    sources=' , '.join(source)


    # sql= "INSERT INTO Data_pi(Topic_Search,Summary,Links) VALUES(%s,%s,%s)"
    # val= (query,stored_text,sources)
    # myDB.execute(sql,val)
    # mysqlDB.commit()

    # myDB.execute('SELECT Links FROM Data_pi WHERE Topic_Search= %s',[query])
    # datadb=myDB.fetchall()
    # if len(datadb)==0:
    #     print("None")
    # else:
    #     for datalinks in datadb:
    #         sqllink=datalinks[0]


    # res = sqllink.strip('][').split(', ')
    # ele=[element for element in links if element not in res]

    # corpus=search(ele)


    result = model(stored_text, min_length=100)
    mysummary = ''.join(result)

    summary=clean(wiki(query))+text_clean(mysummary)
    my_summary=summary


    article_1 = nltk.sent_tokenize(my_summary)
    entities_system_know = dict()
    entities_in_article = dict()
    relations = set()
    ENTITIES=[]
    for article in article_1:
        doc = nlp(article)
        for ent in doc.ents: 
            if ent.label_ not in ['DATE', 'TIME', 'CARDINAL', 'ORDINAL', 'PERCENT','MONEY']:
                entities_in_article[ent.text] = ent.label_

        if(len(entities_system_know) > 0):
            for entity in  entities_system_know.keys():
                if entity in entities_in_article.keys():
                    for ent_new in entities_in_article.keys():
                        if not ent_new == entity:
                            relations.add((entity, ent_new))
            entities_system_know = {**entities_system_know, **entities_in_article}

            entities_in_article = dict()

        else:
            entities_system_know = {**entities_system_know, **entities_in_article}
            for comb in combinations(entities_system_know, 2):
                relations.add(comb)
            entities_in_article = dict()

    G = nx.Graph()
    G.add_edges_from(list(relations))

    fig = plt.figure(figsize=(100, 44))

    nx.draw(G, with_labels=True, node_size=1000, node_color="#28ADFB", node_shape="o", alpha=0.5, linewidths=4, font_size=24, font_color="#ffffff", font_weight="bold", width=2, edge_color="#28ADFB")
    fig.set_facecolor("#013856")
    
    plt.savefig(query.strip()+'.png', facecolor=fig.get_facecolor())

    #########################################################################################################

    news=news_head()

    #########################################################################################################

    consumer_key = "1r556HjZ7fQ6mUYbpCWcVrcST"
    consumer_secret = "Tpjv02wJt8yy1ExCgwmXUk6kWDU3gAcdKWDlK9Ji8ialSz2NuT"
    access_key =  "635591553-kVTaKh2G1hNPzFNdNsQSkTSenUx4m7xjWNH2MTYO"
    access_secret = "9NzYsCUkCPD3xOc6EiFTErjF0lX6NeJK163av1Zef4XZD"
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_key, access_secret)
    api = tweepy.API(auth)

    max_tweets = 10
    searched_tweets = [status for status in tweepy.Cursor(api.search, q=query).items(max_tweets)]

    hashtags=list()
    for tweet in searched_tweets:
        a=tweet.text
        b=tweet.created_at
        c=tweet.user.screen_name
        d=tweet.user.location
        hashtags.append((str(a)+str(b)+str(c)+str(c))+"<br><br>")

    # hashtags=unicodedata.normalize('NFKD', hashtags).encode('ascii', 'ignore')
    for k in range(len(hashtags)):
        hashtags[k] = "• " + hashtags[k]




    #########################################################################################################

    text_tokens = word_tokenize(my_summary)
    tokens_without_sw = [word for word in text_tokens if not word in stopwords.words()]
    filtered_sentence = (" ").join(tokens_without_sw)


    def sentiment_scores(sentence):
        sid_obj = SentimentIntensityAnalyzer()
        sentiment_dict = sid_obj.polarity_scores(sentence)
        analysis = ""

        if sentiment_dict['compound'] >= 0.05 :
            analysis = "Positive"

        elif sentiment_dict['compound'] <= - 0.05 :
            analysis = "Negative"

        else :
            analysis = "Neutral"

        positive=sentiment_dict['pos']*100
        negative=sentiment_dict['neg']*100
        neutral=sentiment_dict['neu']*100

        mylist=[positive,negative,neutral]
        sents=list()
    
        for l in mylist:
            round_off=round(l,2)
            sents.append(round_off)
        return sents

    sentiments=sentiment_scores(filtered_sentence)
    
    #########################################################################################################

    linked=links[1:5]

    beautifiedLinks = list()

    for l in linked:
        l = "<a target='_blank' href='"+l+"'>"+l+"<a/>"
        beautifiedLinks.append(l+"<br><br>")
    
    return jsonify({"response":{"summary":my_summary,"news":news,"hashtags":hashtags,"sentiments":sentiments,"link":beautifiedLinks, "kg":query.strip()+'.png'}}), 200 



if __name__ == '__main__':
    app.run(debug=False, port="5000",host="0.0.0.0") 




