from flask import Flask, render_template, request
from orm import dbsession, Chord

app = Flask(__name__)


def _get_selected_chords():
    return list(map(int, request.args.getlist('crd')))


def _get_all_chords():
    return dbsession.query(Chord).order_by(Chord.name).all()


@app.route('/')
def index():
    return render_template('index.html', chords=_get_all_chords(), sel_chords=_get_selected_chords())


@app.route('/search', methods=['GET'])
def search():
    chord_ids = list(map(int, request.args.getlist('crd')))
    query = request.args.get('q')
    print(query, chord_ids)
    return render_template('index.html', chords=_get_all_chords(), sel_chords=_get_selected_chords())


if __name__ == '__main__':
    app.run(debug=True)
