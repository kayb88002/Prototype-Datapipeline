
def news_head():
    import urllib.request
    import requests
    import re
    import time
    from newspaper import Article
    import nltk
    from nltk.stem import WordNetLemmatizer
    from nltk.corpus import stopwords
    from gensim.summarization.summarizer import summarize
    from gensim.summarization.textcleaner import split_sentences
    from flask import request

    query= request.args.get("summary")
    url = "https://www.livemint.com/Search/Link/Keyword/"+query

    from bs4 import BeautifulSoup

    headers = {'User-Agent': 'Mozilla/5.0'}

    r = requests.get(url, headers=headers)


    soup = BeautifulSoup(r.text, 'html.parser')

    news= soup.find_all("div",class_="headlineSec")

    headlines=soup.findAll('div', attrs={'class':'headlineSec'})
    links=[]
    for div in headlines:
        link=div.find('a')['href']
        if not link.startswith('http'):
            link = "https://www.livemint.com/"+link
        links.append(link)


    corpus=list()
    from newspaper import Article
    for i in links:
        article = Article(i)
        article.download()
        article.parse()
        corpus.append(article.text)
        
    time.sleep(10)


    url=('\n'.join(corpus))



    def f(seq):
        seen=set()
        return [x for x in seq if x not in seen and not seen.add(x)]




    def summary(x, perc): 
        if len(split_sentences(x)) > 100:
            test_summary = summarize(x, ratio = perc, split=True)
            test_summary = '\n'.join(map(str, f(test_summary)))
        else:
            test_summary = x
        return test_summary


    db = summary(url, 0.25)

    text = db.split("\n")
    new_list=list()

    for line in text:
        new_list.append(line+"<br>")

    for k in range(len(new_list)):
        new_list[k] = "➤ " + new_list[k] 
    
   
    return new_list





