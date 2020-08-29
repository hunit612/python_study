from selenium import webdriver
from bs4 import BeautifulSoup
import time
import urllib
import requests, json
import re
#import pandas as pd
from pytube import YouTube

word = ['삼겹살 맛집', '곱창 맛집']
dic = {}

for i in word:
    print([i])
    n = 1
    val = []
    word_encode = urllib.parse.quote(i)
    driver = webdriver.Chrome('chromedriver')
    driver.get('https://www.youtube.com/results?search_query={}'.format(word_encode))

    time.sleep(2)

    #print(word_encode)
    
    html = driver.page_source
    #print(html)

    bs = BeautifulSoup(html, 'html.parser') 
    a = bs.findAll("a", {"id":"thumbnail"})
    count = 0

    for af in a:
        if count < 20:
            print(n)

            print('https://www.youtube.com' + af['href'])
            count += 1
            n += 1
            val.append(af['href'])
        else:
            break
            
    #driver.close()
    
    dic[i] = val
#print(dic)    
    
print('ㅡ * ㅡ' * 10)

for w in word:
    for mat in dic[w]:
        print('url : https://www.youtube.com' + mat)

        video_url = 'https://www.youtube.com' + mat
        yt = YouTube(video_url)
        new_data = [yt]
        print(new_data)

        #script = "[영상 설명]", yt.description

        #print(yt) # 영상 설명