from xml.etree import ElementTree as ET
from requests import get
from re import search, compile
from bs4 import BeautifulSoup
from orm import dbsession, Song, Chord
from datetime import datetime
from sqlalchemy import not_

ns_clean_re = compile(r'xmlns=\".*\"')
chord_url_re = compile(r'.*_crd\.htm$')
rating_re = compile(r'x\s*(\d+)')
song_title_clean_re = compile(r' Chords$')

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.63 Safari/537.36'}


def get_sitemaps():
    root = ET.fromstring(ns_clean_re.sub('', get('http://www.ultimate-guitar.com/sitemap.xml', headers=headers).text))
    return [l.text for l in root.findall('sitemap/loc') if search(r'sitemap\d+\.xml$', l.text)]


def get_chord_urls(sitemap_url):
    root = ET.fromstring(ns_clean_re.sub('', get(sitemap_url, headers=headers).text))
    return [u.text for u in root.findall('url/loc') if chord_url_re.search(u.text)]


def get_song_data(song_url):
    soup = BeautifulSoup(get(song_url, headers=headers).text)
    chords = list(set([c.text for c in soup.select('#cont span')]))

    title = song_title_clean_re.sub('', soup.select('.t_title h1')[0].text)
    artist = soup.select('.t_autor a')[0].text
    rt_match = rating_re.match(soup.select('.raiting .v_c')[0].text.strip())
    rating = int(rt_match.group(1)) if rt_match else None
    song = Song(artist=artist, name=title, url=song_url, rating=rating, created_date=datetime.now())
    return song, chords


def get_songs_with_chords(chords):
    chords = chords if isinstance(chords, list) else [chords]
    q1 = dbsession.query(Song).join(Song.chords).filter(Chord.name.in_(chords))
    q2 = dbsession.query(Song).join(Song.chords).filter(not_(Chord.name.in_(chords)))
    return q1.except_(q2).all()


def main():
    #sitemaps = get_sitemaps()
    #urls = get_chord_urls(sitemaps[-1])
    #[print(u) for u in urls]
    #print(get_song_data('http://tabs.ultimate-guitar.com/o/oasis/a_bell_will_ring_crd.htm'))



if __name__ == '__main__':
    main()