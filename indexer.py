from xml.etree import ElementTree as ET
from requests import get
from re import sub, search

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.63 Safari/537.36'}


def get_sitemaps():
    root = ET.fromstring(sub(r"xmlns=\".*\"", "", get('http://www.ultimate-guitar.com/sitemap.xml', headers=headers).text))
    return [l.text for l in root.findall('sitemap/loc') if search(r'sitemap\d+\.xml$', l.text)]


def main():
    sitemaps = get_sitemaps()
    print(sitemaps)


if __name__ == '__main__':
    main()