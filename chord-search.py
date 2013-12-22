from flask import Flask, render_template, request
from orm import dbsession, Chord

app = Flask(__name__)


@app.route('/')
def index():
    chords = dbsession.query(Chord).order_by(Chord.name).all()
    return render_template('index.html', chords=chords)

@app.route('/search', methods=['GET'])
def search():
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)
