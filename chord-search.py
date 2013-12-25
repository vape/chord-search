from datetime import datetime

from flask import Flask, render_template, request, url_for, send_from_directory
from lib.pagination import Pagination
from orm import dbsession, Chord, Song
from sqlalchemy import not_
from lib.template_helpers import url_for_other_page
from os import path

app = Flask(__name__)
app.jinja_env.globals['url_for_other_page'] = url_for_other_page
PAGE_SIZE = 10


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(path.join(app.root_path, 'static'), 'img/favicon.png')


def _get_selected_chords():
    return list(map(int, request.args.getlist('crd')))


def _get_all_chords():
    return dbsession.query(Chord).order_by(Chord.name).all()


def _get_current_page():
    try:
        return int(request.args.get('p', '1'))
    except ValueError:
        return 1


def _search(q, chords, page=1):
    if not q and not chords:
        return [], 0, 0
    st = datetime.now()
    q1 = dbsession.query(Song).join(Song.chords).filter(Chord.id.in_(chords))
    if q:
        q1 = q1.filter(Song.name.like('%{0}%'.format(q) or Song.artist.like('%{0}%'.format(q))))
    q2 = dbsession.query(Song).join(Song.chords).filter(not_(Chord.id.in_(chords))) if len(chords) > 1 else None
    q = q1.except_(q2) if q2 else q1
    cnt = q.count()
    res = q.limit(PAGE_SIZE).offset((page-1) * PAGE_SIZE).all()
    end = datetime.now()
    return res, cnt, (end - st).total_seconds()


def _get_stats():
    return {
        'song_count': dbsession.query(Song).count(),
        'chord_count': dbsession.query(Chord).count()
    }


@app.route('/')
def index():
    page_data = {
        'chords':_get_all_chords(),
        'sel_chords': _get_selected_chords(),
        'stats': _get_stats()
    }
    return render_template('index.html', **page_data)


@app.route('/search', methods=['GET'])
def search():
    results, total_count, elapsed = _search(request.args.get('q'), list(map(int, request.args.getlist('crd'))),
                                            _get_current_page())
    page_data = {
        'results': results,
        'total_count': total_count,
        'elapsed': elapsed,
        'chords': _get_all_chords(),
        'sel_chords': _get_selected_chords(),
        'pagination': Pagination(_get_current_page(), PAGE_SIZE, total_count),
        'stats': _get_stats()
    }
    return render_template('search_results.html', **page_data)


if __name__ == '__main__':
    app.run(debug=True)
