#!/usr/bin/env python3

COOKIE = "_session_id=ID GOES HERE"
COURSE_URLS = [
    "https://chinesezerotohero.teachable.com/courses/enrolled/185499",
    "https://chinesezerotohero.teachable.com/courses/enrolled/188342",
    "https://chinesezerotohero.teachable.com/courses/enrolled/191818",
    "https://chinesezerotohero.teachable.com/courses/enrolled/191830",
    "https://chinesezerotohero.teachable.com/courses/enrolled/182498",
    "https://chinesezerotohero.teachable.com/courses/enrolled/183827",
]
cookies_dict = dict(token.strip().split('=') for token in COOKIE.split(';'))

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from concurrent.futures import ThreadPoolExecutor

exe = ThreadPoolExecutor(10)

import re

lecture_hrefs = set()
for url in COURSE_URLS:
    response = requests.get(url, cookies=cookies_dict)
    assert response.ok
    print(url)
    for a in BeautifulSoup(response.text, 'lxml').find_all('a'):
        href = a.attrs.get('href', '')
        if re.match('/courses/[0-9]+/lectures/[0-9]+', href):
            lecture_hrefs.add(urljoin(url, href))


video_urls = {}

def get_urls(lecture_href):
    print(lecture_href)
    response = requests.get(lecture_href, cookies=cookies_dict)
    for a in BeautifulSoup(response.text, 'lxml').find_all('a', attrs={"class": "download"}):
        name = a.attrs['data-x-origin-download-name']
        if name.endswith('.pdf'):
            continue
        video_urls[name] = a.attrs['href']


[e for e in exe.map(get_urls, lecture_hrefs)]

import os

def download_file(pair):
    name, url = pair
    filename = 'mp4s/' + name
    if os.path.isfile(filename):
        return
    print(name)
    # there's a way to stream into a file but not worth effort
    response = requests.get(url)
    with open(filename, 'xb') as out:
        out.write(response.content)

[e for e in exe.map(download_file, sorted(video_urls.items()))]
