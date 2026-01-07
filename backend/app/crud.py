from sqlmodel import Session, select, func
from .models import Album, Artist, Tag, Location, Track, AlbumArtistLink, AlbumTagLink
from typing import List, Optional

# --- Stats ---
def get_stats(session: Session):
    album_count = session.exec(select(func.count(Album.id))).one()
    artist_count = session.exec(select(func.count(Artist.id))).one()
    genre_count = session.exec(select(func.count(Tag.id))).one() # We use tags as genres for now or actual genre table
    return {
        "albums": album_count,
        "artists": artist_count,
        "genres": genre_count
    }

# --- Albums ---
def create_album(session: Session, album: Album) -> Album:
    session.add(album)
    session.commit()
    session.refresh(album)
    return album

def get_albums(session: Session, offset: int = 0, limit: int = 100) -> List[Album]:
    return session.exec(select(Album).offset(offset).limit(limit)).all()

def get_album(session: Session, album_id: int) -> Optional[Album]:
    return session.get(Album, album_id)

# --- Artists ---
def create_artist(session: Session, artist: Artist) -> Artist:
    session.add(artist)
    session.commit()
    session.refresh(artist)
    return artist

def get_artists(session: Session) -> List[Artist]:
    return session.exec(select(Artist)).all()

# --- Tags ---
def create_tag(session: Session, tag: Tag) -> Tag:
    session.add(tag)
    session.commit()
    session.refresh(tag)
    return tag

def get_tags(session: Session) -> List[Tag]:
    return session.exec(select(Tag)).all()

# --- Locations ---
def create_location(session: Session, location: Location) -> Location:
    session.add(location)
    session.commit()
    session.refresh(location)
    return location

def get_locations(session: Session) -> List[Location]:
    return session.exec(select(Location)).all()

# --- Links ---
def add_artist_to_album(session: Session, album_id: int, artist_id: int, role: Optional[str] = None) -> AlbumArtistLink:
    link = AlbumArtistLink(album_id=album_id, artist_id=artist_id, role=role)
    session.add(link)
    session.commit()
    session.refresh(link)
    return link
