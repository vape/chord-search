from datetime import datetime

from flask import Flask, render_template, request, send_from_directory
from lib.pagination import Pagination
from orm import dbsession, Chord, Song
from sqlalchemy import not_, or_, and_, desc, asc
from lib.template_helpers import url_for_other_page
from os import path
from re import compile, IGNORECASE as RE_IGNORECASE
from config import is_debug
from flask_babel import Babel

app = Flask(__name__)
app.jinja_env.globals['url_for_other_page'] = url_for_other_page
babel = Babel(app)

PAGE_SIZE = 10

exclude_re = compile(r'(-[a-z0-9]+)', RE_IGNORECASE)


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


def _get_order_by(sort):
    if sort == 'artist':
        return Song.artist, asc
    elif sort == 'song':
        return Song.name, asc
    elif sort == 'rating':
        return Song.rating, desc
    return None, None


def _parse_query(q):
    parsed = dict()
    if not q:
        return parsed
    exclude_words = exclude_re.findall(q)
    if exclude_words:
        parsed['exclude'] = list(map(lambda x: x.strip('-'), exclude_words))
        q = exclude_re.sub('', q, RE_IGNORECASE).strip()

    parsed['q'] = q

    return parsed


def _search(q, chords, page=1, sort=None):
    parsed_query = _parse_query(q)
    if not parsed_query and not chords:
        return [], 0, 0

    st = datetime.now()
    q1 = dbsession.query(Song)
    if chords:
        q1 = q1.join(Song.chords).filter(Chord.id.in_(chords))
    if parsed_query.get('q', ''):
        query = parsed_query.get('q')
        q1 = q1.filter(or_(Song.name.ilike('%{0}%'.format(query)), Song.artist.ilike('%{0}%'.format(query))))
    for exc in parsed_query.get('exclude', []):
        q1 = q1.filter(and_(not_(Song.name.ilike('%{0}%'.format(exc))), not_(Song.artist.ilike('%{0}%'.format(exc)))))
    q2 = dbsession.query(Song).join(Song.chords).filter(not_(Chord.id.in_(chords))) if len(chords) > 1 else None
    q = q1.except_(q2) if q2 else q1
    ord_by, ord_func = _get_order_by(sort)
    if ord_by:
        q = q.order_by(ord_func(ord_by))
        if ord_by == Song.rating:
            q = q.filter(Song.rating != None)
    cnt = q.count()
    res = q.limit(PAGE_SIZE).offset((page - 1) * PAGE_SIZE).all()
    end = datetime.now()
    chord_names = [c[0] for c in
                   dbsession.query(Chord.name).filter(Chord.id.in_(chords)).order_by(Chord.name)] if chords else []
    return res, chord_names, cnt, (end - st).total_seconds()


def _get_stats():
    return {
        'song_count': dbsession.query(Song).count(),
        'chord_count': dbsession.query(Chord).count()
    }


@app.route('/')
def index():
    page_data = {
        'chords': _get_all_chords(),
        'sel_chords': _get_selected_chords(),
        'stats': _get_stats()
    }
    return render_template('index.html', **page_data)


@app.route('/search', methods=['GET'])
def search():
    results, chords, total_count, elapsed = _search(request.args.get('q'),
                                                    list(map(int, request.args.getlist('crd'))),
                                                    _get_current_page(),
                                                    request.args.get('s'))
    page_data = {
        'query': request.args.get('q'),
        'chord_names': ', '.join(chords) if chords else '',
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
    app.run(debug=is_debug(), use_reloader=False)
