from os import path, mkdir
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

DATABASE = path.join(path.dirname(__file__), 'data/chord-search.db')
engine = create_engine('sqlite:///{0}'.format(DATABASE), echo=True)
Base = declarative_base()

song_chord = Table('song_chord', Base.metadata,
                   Column('song_id', Integer, ForeignKey('song.id')),
                   Column('chord_id', Integer, ForeignKey('chord.id'))
)


class Song(Base):
    __tablename__ = 'song'
    id = Column(Integer(), primary_key=True, nullable=False, autoincrement=True)
    artist = Column(String(length=200))
    name = Column(String(length=200), nullable=False)
    url = Column(String(length=200), nullable=False)
    rating = Column(Integer())
    created_date = Column(DateTime(), nullable=False)
    chords = relationship('Chord', secondary=song_chord, backref='songs')


class Chord(Base):
    __tablename__ = 'chord'
    id = Column(Integer(), primary_key=True, nullable=False, autoincrement=True)
    name = Column(String(length=50), nullable=False)


Session = sessionmaker(bind=engine)
Session.configure(bind=engine)
dbsession = Session()
if not path.exists(DATABASE):
    if not path.exists(path.dirname(DATABASE)):
        mkdir(path.dirname(DATABASE))
    Base.metadata.create_all(engine)
