from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from config import initialize_config
from os import environ

initialize_config()

engine = create_engine('postgresql://{DBUSER}:{DBPASS}@{DBSERVER}:{DBPORT}/{DBNAME}'.format(**environ), echo=True)
Base = declarative_base()

song_chord = Table('song_chord', Base.metadata,
                   Column('song_id', Integer, ForeignKey('song.id'), index=True),
                   Column('chord_id', Integer, ForeignKey('chord.id'), index=True)
)


class Song(Base):
    __tablename__ = 'song'
    id = Column(Integer(), primary_key=True, nullable=False, autoincrement=True)
    artist = Column(String(length=200))
    name = Column(String(length=200), nullable=False)
    url = Column(String(length=200), nullable=False, unique=True, index=True)
    rating = Column(Integer())
    created_date = Column(DateTime(), nullable=False, index=True)
    chords = relationship('Chord', secondary=song_chord, backref='songs')

    def __str__(self):
        return '"{0}" by {1}'.format(self.name, self.artist)

    def __repr__(self):
        return '{0}({1})'.format(self.__class__, self.name)


class Chord(Base):
    __tablename__ = 'chord'
    id = Column(Integer(), primary_key=True, nullable=False, autoincrement=True)
    name = Column(String(length=50), nullable=False, unique=True, index=True)

    def __str__(self):
        return self.name

    def __repr__(self):
        return '{0}({1})'.format(self.__class__, self.name)


class IndexingJob(Base):
    __tablename__ = 'indexing_job'
    id = Column(Integer(), primary_key=True, nullable=False, autoincrement=True)
    run_date = Column(DateTime(), nullable=False)


Session = sessionmaker(bind=engine)
Session.configure(bind=engine)
dbsession = Session()
Base.metadata.create_all(engine)
