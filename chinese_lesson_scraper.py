
# coding: utf-8

# In[1]:


COOKIE = "add a cookie here"
COURSE_URLS = [
    "https://chinesezerotohero.teachable.com/courses/enrolled/185499",
    "https://chinesezerotohero.teachable.com/courses/enrolled/188342",
    "https://chinesezerotohero.teachable.com/courses/enrolled/191818",
    "https://chinesezerotohero.teachable.com/courses/enrolled/191830",
    "https://chinesezerotohero.teachable.com/courses/enrolled/182498",
    "https://chinesezerotohero.teachable.com/courses/enrolled/183827",
]
cookies_dict = dict(token.strip().split('=') for token in COOKIE.split(';'))


# In[2]:


import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin


# In[3]:


import re

lecture_hrefs = set()
for url in COURSE_URLS:
    response = requests.get(url, cookies=cookies_dict)
    assert response.ok
    for a in BeautifulSoup(response.text, 'lxml').find_all('a'):
        href = a.attrs.get('href', '')
        if re.match('/courses/[0-9]+/lectures/[0-9]+', href):
            lecture_hrefs.add(urljoin(url, href))


# In[4]:


# intentionally single threaded so I don't slam their servers

video_urls = {}

for lecture_href in lecture_hrefs:
    print(lecture_href)
    response = requests.get(lecture_href, cookies=cookies_dict)
    for a in BeautifulSoup(response.text, 'lxml').find_all('a', attrs={"class": "download"}):
        video_urls[a.attrs['data-x-origin-download-name']] = a.attrs['href']


# In[8]:


import os

for name, url in sorted(video_urls.items()):
    filename = 'mp4s/' + name
    if os.path.isfile(filename):
        continue
    print(name)
    # savings to a variable and writing is dumb but whatever
    response = requests.get(url)
    with open(filename, 'xb') as out:
        out.write(response.content)
