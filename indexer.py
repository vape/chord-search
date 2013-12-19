from xml.etree import ElementTree as ET
from datetime import datetime

from requests import get
from re import search, compile
from bs4 import BeautifulSoup
from orm import dbsession, Song, Chord, IndexingJob
from sqlalchemy import not_, desc
from sys import stdout
from os import path


ns_clean_re = compile(r'xmlns=\".*\"')
chord_url_re = compile(r'.*_crd\.htm$')
song_title_clean_re = compile(r' Chords$')

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.63 Safari/537.36'}
vote_map = {'poor': 1, 'not so good': 2, 'worth learning': 3, 'accurate': 4, 'excellent!': 5}


def get_sitemaps():
    root = ET.fromstring(ns_clean_re.sub('', get('http://www.ultimate-guitar.com/sitemap.xml', headers=headers).text))
    return [l.text for l in root.findall('sitemap/loc') if search(r'sitemap\d+\.xml$', l.text)]


def get_song_page_urls(sitemap_url, from_date):
    root = ET.fromstring(ns_clean_re.sub('', get(sitemap_url, headers=headers).text))
    return [u.find('loc').text for u in root.findall('url') if
            chord_url_re.search(u.find('loc').text) and
            datetime.strptime(u.find('lastmod').text, '%Y-%m-%d') > from_date]


def get_song_data(song_url):
    #print('getting song data for', song_url)
    try:
        r = get(song_url, headers=headers)
        if r.status_code != 200:
            return None, None

        soup = BeautifulSoup(r.text)
        chords = list(set([c.text for c in soup.select('#cont span')]))
        title = song_title_clean_re.sub('', soup.select('.t_title h1')[0].text)
        artist = soup.select('.t_autor a')[0].text
        rating = vote_map.get(soup.select('.vote-success')[0].text, None)
        song = Song(artist=artist, name=title, url=song_url, rating=rating, created_date=datetime.now())
        return song, chords
    except Exception as ex:
        print('Some exception:', ex)
        return None, None


def get_songs_with_chords(chords):
    chords = chords if isinstance(chords, list) else [chords]
    q1 = dbsession.query(Song).join(Song.chords).filter(Chord.name.in_(chords))
    q2 = dbsession.query(Song).join(Song.chords).filter(not_(Chord.name.in_(chords)))
    return q1.except_(q2).all()


def insert_chords(chords):
    for c in chords:
        chord = dbsession.query(Chord).filter(Chord.name == c).first()
        if not chord:
            chord = Chord(name=c)
            dbsession.add(chord)
    dbsession.commit()
    return dbsession.query(Chord).all()


def index_chords(songs):
    song_chords = []
    [song_chords.extend(s[1]) for s in songs if s[1]]
    return insert_chords(list(set(song_chords)))


def index_songs(songs):
    all_chords = index_chords(songs)
    for s in songs:
        try:
            if not s[1]:
                continue

            song = dbsession.query(Song).filter(Song.url == s[0].url).first()
            if not song:
                song = s[0]
                song.chords = [c for c in all_chords if c.name in s[1]]
                dbsession.add(song)
        except Exception as ex:
            print('some error:', ex)

    dbsession.commit()


def report_progress(num_songs, song_index, song_url, start_time):
    elapsed = (datetime.now() - start_time).total_seconds()
    time_per_song = elapsed / (song_index + 1)
    est_time_remaining = (num_songs - (song_index + 1)) * time_per_song / 60
    stdout.write('\rSong {0} of {1}. Elapsed: {2:.2f} min. Remaining: {3:.2f} min. Last song: {4}.'.format(
        song_index + 1,
        num_songs,
        elapsed / 60,
        est_time_remaining,
        path.splitext(path.basename(song_url))[0]))
    stdout.flush()


def main():
    job_start_date = datetime.now()
    last_run = dbsession.query(IndexingJob).order_by(desc(IndexingJob.run_date)).first()
    last_run_date = last_run.run_date if last_run else datetime(2010, 1, 1)
    print(last_run_date)
    sitemaps = get_sitemaps()
    urls = get_song_page_urls(sitemaps[-1], last_run_date)
    num_songs = len(urls)
    songs = []
    start_time = datetime.now()
    for i, u in enumerate(urls):
        songs.append(get_song_data(u))
        report_progress(num_songs, i, u, start_time)

    index_songs([s for s in songs if s[1]])

    dbsession.add(IndexingJob(run_date=job_start_date))
    dbsession.commit()


if __name__ == '__main__':
    main()
