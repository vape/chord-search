from datetime import datetime
from flask import Flask, render_template, request, send_from_directory, jsonify
from lib.decorators import cached
from lib.pagination import Pagination
from orm import dbsession, Chord, Song
from redis import StrictRedis
from sqlalchemy import not_, or_, and_, desc, asc
from lib.template_helpers import url_for_other_page
from os import path, environ
from re import compile, IGNORECASE as RE_IGNORECASE
from config import is_debug
from flask_babel import Babel


app = Flask(__name__)
app.jinja_env.globals['url_for_other_page'] = url_for_other_page
babel = Babel(app)
rds = StrictRedis(host=environ['REDISHOST'], port=int(environ['REDISPORT']), password=environ['REDISPASS'])

exclude_re = compile(r'(-[a-z0-9]+)', RE_IGNORECASE)
specific_re = compile(r'([a-z0-9]+):([a-z0-9]+)', RE_IGNORECASE)
DEFINED_CRITERIA = ['artist', 'song']
PAGE_SIZE = 10


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(path.join(app.root_path, 'static'), 'img/favicon.png')


@cached('all_chords', rds)
def _get_all_chords():
    return [{'id': c[0], 'name': c[1]} for c in dbsession.query(Chord.id, Chord.name).all()]


def _get_selected_chords():
    return list(map(int, request.args.get('crd', '').split(',')))


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

    parsed['exclude'] = list(map(lambda x: x.strip('-'), exclude_re.findall(q)))
    q = exclude_re.sub('', q, RE_IGNORECASE).strip()

    specific_criteria = [c for c in specific_re.findall(q) if isinstance(c, tuple) and c[0] in DEFINED_CRITERIA]
    for c in specific_criteria:
        crits = parsed.get(c[0], [])
        crits.append(c[1])
        parsed[c[0]] = crits

    q = specific_re.sub('', specific_re.sub('', q, RE_IGNORECASE), RE_IGNORECASE).strip()

    parsed['q'] = q

    return parsed


def _apply_extra_criteria(q_obj, parsed_query):
    if parsed_query.get('q', ''):
        query = parsed_query.get('q')
        q_obj = q_obj.filter(or_(Song.name.ilike('%{0}%'.format(query)), Song.artist.ilike('%{0}%'.format(query))))
    for exc in parsed_query.get('exclude', []):
        q_obj = q_obj.filter(and_(not_(Song.name.ilike('%{0}%'.format(exc))), not_(Song.artist.ilike('%{0}%'.format(exc)))))
    for ats in parsed_query.get('artist', []):
        q_obj = q_obj.filter(Song.artist.ilike('%{0}%'.format(ats)))
    for sng in parsed_query.get('song', []):
        q_obj = q_obj.filter(Song.name.ilike('%{0}%'.format(sng)))
    return q_obj


def _search(q, chords, page=1, sort=None):
    parsed_query = _parse_query(q)
    if not parsed_query and not chords:
        return [], [], 0, 0

    st = datetime.now()
    q1 = dbsession.query(Song)
    if chords:
        q1 = q1.join(Song.chords).filter(Chord.id.in_(chords))
    q1 = _apply_extra_criteria(q1, parsed_query)
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
    selected_chords = [{'id': c[0], 'name': c[1]} for c in
                   dbsession.query(Chord.id, Chord.name).filter(Chord.id.in_(chords)).order_by(Chord.name)] if chords else []
    return res, selected_chords, cnt, (end - st).total_seconds()


@cached('stats', rds)
def _get_stats():
    return {
        'song_count': dbsession.query(Song).count(),
        'chord_count': dbsession.query(Chord).count()
    }


@app.route('/')
def index():
    page_data = {
        'stats': _get_stats()
    }
    return render_template('index.html', **page_data)


@app.route('/chord_filter', methods=['GET'])
def chord_filter():
    q = request.args.get('q')
    r = [c for c in _get_all_chords() if c['name'].lower().startswith(q.lower())] if q else []
    return jsonify(results=r)


@app.route('/search', methods=['GET'])
def search():
    results, chords, total_count, elapsed = _search(request.args.get('q'),
                                                    list(map(int, request.args.get('crd', '').split(','))) if request.args.get('crd', '') else [],
                                                    _get_current_page(),
                                                    request.args.get('s'))
    page_data = {
        'query': request.args.get('q'),
        'chord_names': ', '.join([c['name'] for c in chords]) if chords else '',
        'selected_chords': chords,
        'results': results,
        'total_count': total_count,
        'elapsed': elapsed,
        'pagination': Pagination(_get_current_page(), PAGE_SIZE, total_count),
        'stats': _get_stats()
    }
    return render_template('search_results.html', **page_data)


if __name__ == '__main__':
    app.run(debug=is_debug(), use_reloader=False)
