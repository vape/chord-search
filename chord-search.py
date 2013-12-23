from flask import Flask, render_template, request
from orm import dbsession, Chord, Song
from sqlalchemy import not_
from datetime import datetime

app = Flask(__name__)


def _get_selected_chords():
    return list(map(int, request.args.getlist('crd')))


def _get_all_chords():
    return dbsession.query(Chord).order_by(Chord.name).all()


def _search(q, chords):
    if not q and not chords:
        return [], 0
    st = datetime.now()
    q1 = dbsession.query(Song).join(Song.chords).filter(Chord.id.in_(chords))
    if q:
        q1 = q1.filter(Song.name.like('%{0}%'.format(q) or Song.artist.like('%{0}%'.format(q))))
    q2 = dbsession.query(Song).join(Song.chords).filter(not_(Chord.id.in_(chords))) if len(chords) > 1 else None
    res = q1.except_(q2).all() if q2 else q1.all()
    end = datetime.now()
    return res, (end - st).total_seconds()


@app.route('/')
def index():
    return render_template('index.html', chords=_get_all_chords(), sel_chords=_get_selected_chords())


@app.route('/search', methods=['GET'])
def search():
    results, elapsed = _search(request.args.get('q'), list(map(int, request.args.getlist('crd'))))
    return render_template('search_results.html', results=results, elapsed=elapsed, chords=_get_all_chords(), sel_chords=_get_selected_chords())


if __name__ == '__main__':
    app.run(debug=True)
