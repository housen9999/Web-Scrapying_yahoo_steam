#!/usr/bin/env python
# coding: utf-8

# In[ ]:


get_ipython().run_line_magic('autosave', '120')
get_ipython().system('pip install --upgrade pymongo')


# # Yahoo Movie 上映分析

# - response 預覽

# In[ ]:


# import requests
# from bs4 import BeautifulSoup
# resp = requests.request(method='GET' ,url='https://movies.yahoo.com.tw/movie_intheaters.html?page=1')
# print(resp.text)


# - 完整功能程式

# In[ ]:


import csv, requests, os, glob
import pandas as pd
from bs4 import BeautifulSoup
pages = 8
dct = {'電影片名':[], '電影英文片名':[], '上映時間':[], '網友期待度':[], '網友評分':[]}

def getInfo(url):
    resp = requests.request(method='GET' ,url=url)
    soup = BeautifulSoup(resp.text, 'lxml')
    return soup.find_all('div', 'release_info')

def appendToDct(dct, name, english_name, release_time, level, finalScore):
    dct['電影片名'].append(name)
    dct['電影英文片名'].append(english_name)
    dct['上映時間'].append(release_time)
    dct['網友期待度'].append(level)
    dct['網友評分'].append(finalScore)

def getMovInfo(dct, name, english_name, release_time, level, finalScore):
    # 電影名稱
    name = item.find('div', 'release_movie_name').a.text.strip()
    # 電影英文名稱
    english_name = item.find('div', 'en').a.text.strip()
    # 上映日期
    release_time = item.find('div', 'release_movie_time').text.split('：')[-1].strip()
    # 網友期待度
    level = item.find('div', 'leveltext').span.text.strip()
    # 網友評分
    score = item.find_all('div', 'leveltext')
    finalScore = ''
    for i in score:
        finalScore = i.find('span').get('data-num')
    # 將資料存入
    appendToDct(dct, name, english_name, release_time, level, finalScore)
    
# --------Main---------
for page in range(1, pages+1):
    url = 'https://movies.yahoo.com.tw/movie_intheaters.html?page={}'.format(page)
    info_items = getInfo(url)
    name, english_name, release_time, level, finalScore = '', '', '', '', ''
    for item in info_items:
        getMovInfo(dct, name, english_name, release_time, level, finalScore)
        
# dict轉 df及輸出成csv
df = pd.DataFrame(dct)
# path_ = r'D:\DataEngineering'
path_ = r'C:\Users\user\Python'
if not os.path.exists(path_):
    os.mkdir(path_)
df.to_csv(path_ + r'\YahooMovie.csv', encoding='UTF-8-sig')
df.sort_values(['網友評分'], ascending=False)[:10]


# # Steam遊戲折扣分析

# - response 預覽

# In[ ]:


# import requests
# from bs4 import BeautifulSoup
# url = 'https://store.steampowered.com/search/?filter=topsellers&page=1'
# headers = {"User-Agent":'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)'
#                ' Chrome/96.0.4664.110 Safari/537.36 ', 'Accept-Language': 'zh-TW '}
# resp = requests.get(url, headers=headers)
# print(resp.text)


# - 完整功能程式

# In[ ]:


from platform import python_version
import os, time, json, requests, bs4, urllib
import pandas as pd
from bs4 import BeautifulSoup
from IPython.display import clear_output

def get_text(url):
    headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)'
               ' Chrome/96.0.4664.110 Safari/537.36 ', 'Accept-Language': 'zh-TW '}
    resp = requests.get(url, headers=headers)
    return resp.text

def get_evaluation(soup, game_evaluation):
    eva = soup.find_all(class_="col search_reviewscore responsive_secondrow")
    for i in eva:
        if i.span is not None:
            game_evaluation.append(i.span["data-tooltip-html"].split("<br>")[0])
        else:
            game_evaluation.append("暫無評價")
            
def get_link(soup, link):
    lk = soup.find_all("div", id="search_resultsRows")
    for i in lk:
        b = i.find_all('a')
    for i in b:
        link.append(i['href'].strip())

def get_name_and_discount(soup, game_info, link, game_evaluation):
    n = 0
    name_text = soup.find_all('div', class_="responsive_search_name_combined")
    for z in name_text:
        name = z.find(class_="title").string.strip()
        # 判斷折扣是否為None，獲取價格
        if z.find(class_="col search_discount responsive_secondrow").string is None:
            price = z.find(class_="col search_price discounted responsive_secondrow").text.strip().split("NT$")
            discount = z.find(class_="col search_discount responsive_secondrow").text.strip()
            game_info.append([name, price[1].strip(), discount, price[2].strip(), game_evaluation[n], link[n]])
        else:
            price = z.find(class_="col search_price responsive_secondrow").string.strip().split("NT$")
            discount = '-0%'
            game_info.append([name, price[1].strip(), discount, price[1], game_evaluation[n], link[n]])
        n += 1

def run(game_info, link, game_evaluation, text):
    soup = BeautifulSoup(text, "html.parser")
    get_evaluation(soup, game_evaluation)                         # 遊戲評價
    get_link(soup, link)                                          # 遊戲詳情網址
    get_name_and_discount(soup, game_info, link, game_evaluation) # 遊戲名稱及價格
        
# ------------Main-------------
Game_info = []          # 遊戲訊息
Link = []               # 遊戲連結
Game_evaluation = []    # 遊戲評價
pages = 10
for page in range(1, pages+1):
    url = 'https://store.steampowered.com/search/?filter=topsellers&page={}'.format(page)
    get_text(url)
    run(Game_info, Link, Game_evaluation, get_text(url))

df = pd.DataFrame(Game_info, columns=['遊戲名稱', '遊戲原價', '遊戲折扣', '遊戲價格(NT)', '遊戲評價', '遊戲連結'])
# path_ = r'D:\DataEngineering'
path_ = r'C:\Users\user\Python'
if not os.path.exists(path_):
    os.mkdir(path_)
df.to_csv(path_ + r'\SteamDiscount.csv', index=0, encoding='UTF-8-sig')
df.sort_values(['遊戲折扣'], ascending=False)[:10]


# # 將上面兩個的結果放入資料庫

# In[ ]:


import os, time, socket, pymongo, glob
import pandas as pd
from pymongo.database import Database

client = pymongo.MongoClient(host='localhost', port=27017)
dbname = 'G4'
db = client[dbname]

if not 'YahMov' in db.list_collection_names():
    db.create_collection("YahMov")
if not 'SteamDc' in db.list_collection_names():
    db.create_collection("SteamDc")

path_ = r'D:\DataEngineering'
yahMovFile = pd.read_csv(path_ + r'\YahooMovie.csv', sep=',', encoding='UTF-8-sig')
db.YahMov.insert_many(yahMovFile.to_dict('record'))

steamDcFile = pd.read_csv(path_ + r'\Steam.csv', sep=',', encoding='UTF-8-sig')
db.SteamDc.insert_many(steamDcFile.to_dict('record'))

for n in db.SteamDc.find():
    if isinstance(n['遊戲價格(NT)'], str):
        temp = int(n['遊戲價格(NT)'].replace(',','').strip())
    else:
        temp = n['遊戲價格(NT)']
    db.SteamDc.update_many({"遊戲價格(NT)":n['遊戲價格(NT)']}, {"$set":{"遊戲價格(NT)":temp}})
for n in db.SteamDc.find():
    if isinstance(n['遊戲原價'], str):
        temp = int(n['遊戲原價'].replace(',','').strip())
    else:
        temp = n['遊戲原價']
    db.SteamDc.update_many({"遊戲原價":n['遊戲原價']}, {"$set":{"遊戲原價":temp}})
for n in db.SteamDc.find():
    if isinstance(n['遊戲折扣'], str):
        temp = float(n['遊戲折扣'].replace("-",'').replace("%",'').strip())
    else:
        temp = n['遊戲折扣']
    temp *= 0.01
    db.SteamDc.update_one({"遊戲折扣":n['遊戲折扣']}, {"$set":{"遊戲折扣":temp}})
for n in db.YahMov.find():
    if isinstance(n['網友評分'], str):
        temp = int(n['網友評分'].replace(',','').strip())
    else:
        temp = n['網友評分']


# # 從資料庫叫出我們需要的資料

# In[ ]:


L=[]
for n in db.YahMov.find({"網友評分":{'$gte':4}}, {"_id":0,  "網友期待度":0}):
    L.append(n)
df = pd.DataFrame(L)
df.sort_values(['網友評分'], ascending=False, ignore_index=True)[:10]


# In[ ]:


L=[]
for n in db.SteamDc.find({"遊戲價格(NT)":{'$lt':1000}}, {"_id":0, "編號":0, "遊戲連結":0}):
    L.append(n)
df = pd.DataFrame(L)
df.sort_values(['遊戲折扣'], ascending=False, ignore_index=True)[:10]

