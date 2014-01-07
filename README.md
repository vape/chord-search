### chord-search

This app consists of two components:

1. [indexer.py](https://github.com/vape/chord-search/blob/master/scripts/indexer.py) which indexes chord pages from [ultimate-guitar.com](http://ultimate-guitar.com) using their sitemap.xml files.
2. [chord-search.py](https://github.com/vape/chord-search/blob/master/chord-search.py) which is a Flask app that provides a search interface for the song database according to song, artist name and (more importantly) chords.

I'm learning to play guitar, and I needed to find songs which consist of the few chords I know how to play. No online tab/chord site has search by chord capability (understandably). So I made one for myself. I also got to play with Flask and practice Python which were added incentives for me.
