from sqlmodel import Session, select, func, text, desc
from sqlalchemy.orm import selectinload
from .models import Album, Artist, Tag, Location, Track, AlbumArtistLink, AlbumTagLink, AlbumGenreLink, AlbumCreate, AlbumUpdate, Genre
from typing import List, Optional

# --- Stats ---
def get_stats(session: Session):
    album_count = session.exec(select(func.count(Album.id))).one()
    artist_count = session.exec(select(func.count(Artist.id))).one()
    genre_count = session.exec(select(func.count(Genre.id))).one()
    return {
        "albums": album_count,
        "artists": artist_count,
        "genres": genre_count
    }

# --- Albums ---
def create_album(session: Session, album_create: AlbumCreate) -> Album:
    # Convert AlbumCreate DTO to Album table model, excluding relationships handled manually
    db_album = Album.model_validate(album_create.model_dump(exclude={"tracks", "artist_names", "genre_names", "tag_ids"}))
    
    # Handle Tags
    if album_create.tag_ids:
        tags = session.exec(select(Tag).where(Tag.id.in_(album_create.tag_ids))).all()
        db_album.tags = tags

    # Handle Artists
    if album_create.artist_names:
        artists = []
        for name in album_create.artist_names:
            artist = session.exec(select(Artist).where(Artist.name == name)).first()
            if not artist:
                artist = Artist(name=name)
                session.add(artist)
                session.commit()
                session.refresh(artist)
            artists.append(artist)
        db_album.artists = artists

    # Handle Genres
    if album_create.genre_names:
        genres = []
        for name in album_create.genre_names:
            genre = session.exec(select(Genre).where(Genre.name == name)).first()
            if not genre:
                genre = Genre(name=name)
                session.add(genre)
                session.commit()
                session.refresh(genre)
            genres.append(genre)
        db_album.genres = genres
        
    # Handle Tracks
    if album_create.tracks:
        db_tracks = [Track(**t.model_dump(), album=db_album) for t in album_create.tracks]
        db_album.tracks = db_tracks

    session.add(db_album)
    session.commit()
    session.refresh(db_album)
    return db_album

def update_album(session: Session, album_id: int, album_update: AlbumUpdate) -> Optional[Album]:
    db_album = session.get(Album, album_id)
    if not db_album:
        return None
    
    update_data = album_update.model_dump(exclude_unset=True)
    
    # Handle Tags
    if "tag_ids" in update_data:
        tag_ids = update_data.pop("tag_ids")
        if tag_ids is not None:
            tags = session.exec(select(Tag).where(Tag.id.in_(tag_ids))).all()
            db_album.tags = tags

    # Handle Genres
    if "genre_ids" in update_data:
        genre_ids = update_data.pop("genre_ids")
        if genre_ids is not None:
            genres = session.exec(select(Genre).where(Genre.id.in_(genre_ids))).all()
            db_album.genres = genres

    # Handle Artists
    if "artist_names" in update_data:
        artist_names = update_data.pop("artist_names")
        if artist_names is not None:
            artists = []
            for name in artist_names:
                artist = session.exec(select(Artist).where(Artist.name == name)).first()
                if not artist:
                    artist = Artist(name=name)
                    session.add(artist)
                    session.commit()
                    session.refresh(artist)
                artists.append(artist)
            db_album.artists = artists
            
    # Handle Tracks
    if "tracks" in update_data:
        new_tracks = update_data.pop("tracks")
        if new_tracks is not None:
            # Simple approach: Replace tracklist
            # Delete old tracks
            session.exec(text("DELETE FROM tracks WHERE album_id = :id"), params={"id": album_id})
            # Add new tracks
            db_tracks = []
            for t in new_tracks:
                # Strip extra fields like _originalIndex and ensure album_id is set
                clean_track = {k: v for k, v in t.items() if k in Track.model_fields}
                clean_track["album_id"] = album_id
                db_tracks.append(Track(**clean_track))
            db_album.tracks = db_tracks
            
    # Update other fields
    for key, value in update_data.items():
        setattr(db_album, key, value)
        
    session.add(db_album)
    session.commit()
    session.refresh(db_album)
    return db_album

# --- Genres ---
def get_genres(session: Session):
    # Return list of dicts with count
    statement = select(Genre, func.count(AlbumGenreLink.album_id)).join(AlbumGenreLink, isouter=True).group_by(Genre.id)
    results = session.exec(statement).all()
    return [{"id": g.id, "name": g.name, "album_count": count} for g, count in results]

def update_genre(session: Session, genre_id: int, genre_data: Genre) -> Optional[Genre]:
    db_genre = session.get(Genre, genre_id)
    if not db_genre:
        return None
    genre_data_dict = genre_data.model_dump(exclude_unset=True)
    for key, value in genre_data_dict.items():
        setattr(db_genre, key, value)
    session.add(db_genre)
    session.commit()
    session.refresh(db_genre)
    return db_genre

def delete_genre(session: Session, genre_id: int) -> bool:
    genre = session.get(Genre, genre_id)
    if not genre:
        return False
    
    # Check dependencies or cascade? 
    # SQLModel/SQLAlchemy relationships might block delete if not configured to cascade.
    # Manually delete links first to be safe and ensure "force delete" behavior for cleanup.
    session.exec(text("DELETE FROM album_genre_links WHERE genre_id = :id"), params={"id": genre_id})
    
    session.delete(genre)
    session.commit()
    return True

def get_albums(session: Session, offset: int = 0, limit: int = 100, sort_by: str = "created_at", order: str = "desc", album_ids: Optional[List[int]] = None) -> List[Album]:
    statement = select(Album).options(
        selectinload(Album.artists),
        selectinload(Album.location),
        selectinload(Album.tags),
        selectinload(Album.genres),
        selectinload(Album.tracks)
    )
    
    if album_ids is not None:
        statement = statement.where(Album.id.in_(album_ids))

    # Sort Logic
    sort_attr = None
    if sort_by == "title":
        # Case insensitive sort for title
        sort_attr = func.lower(Album.title)
    elif sort_by == "year":
        sort_attr = Album.year
    elif sort_by == "created_at":
        sort_attr = Album.created_at
    elif sort_by == "artist":
        # To sort by artist, we join and take the first artist name
        # This is a bit complex for a single query, but we can join and use func.min(Artist.name)
        statement = statement.join(AlbumArtistLink, isouter=True).join(Artist, isouter=True).group_by(Album.id)
        sort_attr = func.min(Artist.name)
    
    if sort_attr is not None:
        if order == "desc":
            statement = statement.order_by(desc(sort_attr))
        else:
            statement = statement.order_by(sort_attr)
    else:
        # Default fallback
        statement = statement.order_by(desc(Album.created_at))

    return session.exec(statement.offset(offset).limit(limit)).all()

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

def get_tags(session: Session):
    # Return list of dicts with count
    statement = select(Tag, func.count(AlbumTagLink.album_id)).join(AlbumTagLink, isouter=True).group_by(Tag.id)
    results = session.exec(statement).all()
    return [{"id": t.id, "name": t.name, "color": t.color, "album_count": count} for t, count in results]

def update_tag(session: Session, tag_id: int, tag_data: Tag) -> Optional[Tag]:
    db_tag = session.get(Tag, tag_id)
    if not db_tag:
        return None
    
    tag_data_dict = tag_data.model_dump(exclude_unset=True)
    for key, value in tag_data_dict.items():
        setattr(db_tag, key, value)
    
    session.add(db_tag)
    session.commit()
    session.refresh(db_tag)
    return db_tag

# --- Locations ---
def create_location(session: Session, location: Location) -> Location:
    session.add(location)
    session.commit()
    session.refresh(location)
    return location

def get_location(session: Session, location_id: int) -> Optional[Location]:
    return session.get(Location, location_id)

def update_location(session: Session, location_id: int, location_data: Location) -> Optional[Location]:
    db_location = session.get(Location, location_id)
    if not db_location:
        return None
    
    location_data_dict = location_data.model_dump(exclude_unset=True)
    for key, value in location_data_dict.items():
        setattr(db_location, key, value)
    
    session.add(db_location)
    session.commit()
    session.refresh(db_location)
    return db_location

def get_locations(session: Session) -> List[Location]:
    return session.exec(select(Location)).all()

# --- Links ---
def add_artist_to_album(session: Session, album_id: int, artist_id: int, role: Optional[str] = None) -> AlbumArtistLink:
    link = AlbumArtistLink(album_id=album_id, artist_id=artist_id, role=role)
    session.add(link)
    session.commit()
    session.refresh(link)
    return link

def check_duplicate_album(session: Session, title: str, artist_names: List[str], upc_ean: Optional[str] = None) -> List[Album]:
    """
    Checks if an album already exists by barcode or Title + Artists combination.
    """
    results = []
    
    # 1. Check by barcode (highest confidence)
    if upc_ean:
        stmt = select(Album).where(Album.upc_ean == upc_ean).options(selectinload(Album.artists))
        barcode_matches = session.exec(stmt).all()
        for m in barcode_matches:
            if m not in results:
                results.append(m)
                
    # 2. Check by Title + Artists (case insensitive title, exact artist match)
    if title and artist_names:
        # Get albums with matching title first
        stmt = select(Album).where(func.lower(Album.title) == title.lower()).options(selectinload(Album.artists))
        title_matches = session.exec(stmt).all()
        
        for album in title_matches:
            album_artist_names = [a.name for a in album.artists]
            # Check if all provided artists are in the album's artists (simplification)
            # or if the lists match exactly
            if sorted(album_artist_names) == sorted(artist_names):
                if album not in results:
                    results.append(album)
                    
    return results
