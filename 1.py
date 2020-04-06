import requests
from bs4 import BeautifulSoup as BS

r = requests.get('https://yastat.net/s3/milab/2020/podomam/map/index.html')
html = BS(r.content, 'html.parser')
