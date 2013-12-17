from xml.etree import ElementTree as ET
from requests import get
from re import search, compile
from bs4 import BeautifulSoup

ns_clean_re = compile(r'xmlns=\".*\"')
chord_url_re = compile(r'.*_crd\.htm$')

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.63 Safari/537.36'}


def get_sitemaps():
    root = ET.fromstring(ns_clean_re.sub('', get('http://www.ultimate-guitar.com/sitemap.xml', headers=headers).text))
    return [l.text for l in root.findall('sitemap/loc') if search(r'sitemap\d+\.xml$', l.text)]


def get_chord_urls(sitemap_url):
    root = ET.fromstring(ns_clean_re.sub('', get(sitemap_url, headers=headers).text))
    return [u.text for u in root.findall('url/loc') if chord_url_re.search(u.text)]


def get_song_data(song_url):



def main():
    sitemaps = get_sitemaps()
    urls = get_chord_urls(sitemaps[-1])
    [print(u) for u in urls]


if __name__ == '__main__':
    main()