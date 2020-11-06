from flask import Flask, render_template
import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient
import urllib3
import json

app = Flask(__name__)


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/task1')
def my_page():
    print(step1())
    print(step3(step2('https://news.v.daum.net/v/20201106110404888')))
    return 'This is My Page!'

#url을 변경해서기 검색 쿼리를 변경하고, 각 뉴스의 url을 가져오기
def step1():
    # URL을 읽어서 HTML를 받아오고,
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
    data = requests.get('https://search.daum.net/search?w=news&nil_search=btn&DA=NTB&enc=utf8&cluster=y&cluster_page=1&q=%EA%B2%80%EC%B0%B0%EC%B4%9D%EC%9E%A5%20%EC%9C%A4%EC%84%9D%EC%97%B4', headers=headers)

    #clusterResultUL > li.fst > div.wrap_cont > div > span.f_nb.date > a
    # clusterResultUL > li.fst > div.wrap_cont > div > span.f_nb.date > a
    # clusterResultUL > li:nth-child(2) > div.wrap_cont > div > span.f_nb.date > a
    soup = BeautifulSoup(data.text, 'html.parser')

    links = soup.select('#clusterResultUL > li > div.wrap_cont > div > span.f_nb.date > a')
    news_link = []
    for link in links:
        news_link.append(link['href'])

    return news_link


#가져온 url에서 본문 text 가져오기
def step2(news_link):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
    data = requests.get(news_link,headers=headers)

    soup = BeautifulSoup(data.text, 'html.parser')
    contents = soup.select('#harmonyContainer > section > p')
    news_contents = []
    for content in contents:
        news_contents.append(content.getText())
    one_content = " ".join(news_contents)
    return one_content


#가져온 text를 분석기로 보내서 나온 인물명을 총장명칭과 함께 저장하기
def step3(text):
    openApiURL = "http://aiopen.etri.re.kr:8000/WiseNLU"

    accessKey = "*****"
    analysisCode = "ner"

    requestJson = {
        "access_key": accessKey,
        "argument": {
            "text": text,
            "analysis_code": analysisCode
        }
    }

    http = urllib3.PoolManager()
    response = http.request(
        "POST",
        openApiURL,
        headers={"Content-Type": "application/json; charset=UTF-8"},
        body=json.dumps(requestJson)
    )

    api_doc = str(response.data, "utf-8")
    print(api_doc)
    json_data = json.loads(api_doc)
    print(json_data)

    api_results = []
# return_object > sentence(배열) 반복문을 돌면서 0(딕셔너리) key 'NE'(배열) 내 요소는 딕서녀리 'type' : PS_NAME 딕셔너리의 text key의 밸
    for sentence in json_data['return_object']['sentence']:
        for a in sentence['NE']:
            if a['type'] == 'PS_NAME':
                api_results.append(a['text'])

    return api_results


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
