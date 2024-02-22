from sqlalchemy import and_
from sqlalchemy.orm import Session, joinedload

from src.api.myapi.metadata_model import MetadataResponse
from src.database.musicDB.db_models import Album, File, Genre, Song, Artist, SongArtist


def add_file_and_metadata(db: Session, file, metadata: MetadataResponse):
    album = Album(ALBUM_NAME=metadata.album)
    file = File(FILE_DATA=file, FILE_TYPE='mp3')

    genre_res = db.query(Genre).filter(Genre.GENRE_NAME == metadata.genre).first()
    if not genre_res:
        genre = Genre(GENRE_NAME=metadata.genre)
        song = Song(
            DURATION=metadata.duration,
            TITLE=metadata.title,
            RELEASE_DATE=metadata.date,
            file=file,
            album=album,
            genre=genre
        )
    else:
        song = Song(
            DURATION=metadata.duration,
            TITLE=metadata.title,
            RELEASE_DATE=metadata.date,
            file=file,
            album=album,
            GENRE_ID=genre_res.GENRE_ID
        )

    for artist_name in metadata.artists:
        artist_res = db.query(Artist).filter(Artist.ARTIST_NAME == artist_name.name).first()
        if not artist_res:
            artist = Artist(ARTIST_NAME=artist_name.name)
            song_artist = SongArtist(song=song, artist=artist)
            song.artist.append(song_artist)

    db.add(song)
    db.flush()


def search_for_title_and_artist(db: Session, title: str, artist: str):
    if title and artist:
        return db.query(Song).filter(
            and_(
                Song.TITLE.like(title),
                Artist.ARTIST_NAME == artist
            )
        ).options(
            joinedload(Song.artist),
            joinedload(Song.album),
            joinedload(Song.genre)) \
            .all()
    elif title and not artist:
        return db.query(Song).filter(Song.TITLE.like(title)).options(
            joinedload(Song.artist),
            joinedload(Song.album),
            joinedload(Song.genre)).all()
    else:
        # only artist
        return db.query(Song).join(Song.artist).filter(Artist.ARTIST_NAME == artist).options(
            joinedload(Song.artist),
            joinedload(Song.album),
            joinedload(Song.genre)).all()
