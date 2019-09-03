# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.4'
#       jupytext_version: 1.2.3
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# +
# !pip install requests
# !pip install bs4
# !pip install pandas

import csv
import json

import requests
from bs4 import BeautifulSoup

import pandas as pd

from IPython.display import display, HTML

SITE_ROOT = 'https://www.alltrails.com'
pd.set_option('display.max_colwidth', -1)

# + {"jupyter": {"source_hidden": true}}
url = "https://en.wikipedia.org/wiki/List_of_national_capitals"

r = requests.get(url)

soup = BeautifulSoup(r.content, "html.parser")
table = soup.find_all('table')[1]
rows = table.find_all('tr')
row_list = list()

for tr in rows:
    td = tr.find_all('td')
    row = [i.text for i in td]
    row_list.append(row)

row_list


# +
def get_trails(soup):
    trails_ul = soup.find_all("ul", {"data-reactid": "4"})[0]
    for li in trails_ul.find_all("li"):
        for trail_result in li.find_all("div", {"class": "trail-result-card lazyload"}):
            yield trail_result

            
def get_trails_by_attr(trails, attr='itemid'):
    for trail in trails:
        yield trail.attrs[attr]

        
def get_each_trail_link(trails):
    for t in get_trails_by_attr(trails):
        name = t.split('/')[-1]
        link1 = '/'.join([SITE_ROOT, t.lstrip('/')])
        link2 = '/'.join([SITE_ROOT, 'explore', t.lstrip('/')]) + '?ref=sidebar-static-map'
        yield name, link1, link2


def get_trail_data(name, link1, link2):

    r_t = requests.get(link1)
    soup_t = BeautifulSoup(r_t.content, "html.parser")

    detail_data = soup_t.find_all('span', class_="detail-data")
    tag_cloud = soup_t.find('section', class_='tag-cloud').find_all('span', class_='big rounded active')

    data = {
        "thumb": '=IMAGE("{}")'.format(soup_t.find('img', id="static-map-img").attrs['data-src']),
        "name": name,
        "difficulty": soup_t.find('span', class_="diff").get_text(),
        "elevation": soup_t.find('span', class_="detail-data xlate-none").get_text().strip(),
        "distance": detail_data[0].get_text().strip(),
        "description": soup_t.find('p', id="auto-overview").get_text(),
        "link": link2,
        "avg rating": json.loads(soup_t.find('span', {"data-react-class": "TrailRatingStars"}).attrs['data-react-props'])['avgRating'],
        "rewiew count": soup_t.find('span', itemprop="reviewCount").get_text(),
        "route type": detail_data[2].get_text().strip(),
        "tags": ', '.join([tag.get_text() for tag in tag_cloud]),
    }

    return data


# +
url = "https://www.alltrails.com/parks/canada/quebec/mont-orford-national-park"

r = requests.get(url)
soup = BeautifulSoup(r.content, "html.parser")
trails = list(get_trails(soup))
trail_links = list(get_each_trail_link(trails))

display(pd.DataFrame(trail_links))

trails_data_gen = (get_trail_data(*tl) for tl in trail_links)
# -

data = list(trails_data_gen)

df = pd.DataFrame(data)
display(df)



# +
# unit example

name, link1, link2 = trail_links[0]
data = get_trail_data(name, link1, link2)
display(data)
