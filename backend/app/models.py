from datetime import datetime
from typing import Optional, List
from sqlmodel import Field, SQLModel, Relationship

# Link tables
class AlbumTagLink(SQLModel, table=True):
    __tablename__ = "album_tag_links"
    album_id: Optional[int] = Field(default=None, foreign_key="albums.id", primary_key=True)
    tag_id: Optional[int] = Field(default=None, foreign_key="tags.id", primary_key=True)

class AlbumArtistLink(SQLModel, table=True):
    __tablename__ = "album_artist_links"
    album_id: Optional[int] = Field(default=None, foreign_key="albums.id", primary_key=True)
    artist_id: Optional[int] = Field(default=None, foreign_key="artists.id", primary_key=True)
    role: Optional[str] = "Main"

class AlbumGenreLink(SQLModel, table=True):
    __tablename__ = "album_genre_links"
    album_id: Optional[int] = Field(default=None, foreign_key="albums.id", primary_key=True)
    genre_id: Optional[int] = Field(default=None, foreign_key="genres.id", primary_key=True)

# --- Genre ---
class GenreBase(SQLModel):
    name: str = Field(unique=True)

class Genre(GenreBase, table=True):
    __tablename__ = "genres"
    id: Optional[int] = Field(default=None, primary_key=True)
    albums: List["Album"] = Relationship(back_populates="genres", link_model=AlbumGenreLink)

class GenreRead(GenreBase):
    id: int
    album_count: int = 0

# --- Tag ---
class TagBase(SQLModel):
    name: str = Field(index=True, unique=True)
    color: str = "#CCCCCC"

class Tag(TagBase, table=True):
    __tablename__ = "tags"
    id: Optional[int] = Field(default=None, primary_key=True)
    albums: List["Album"] = Relationship(back_populates="tags", link_model=AlbumTagLink)

class TagRead(TagBase):
    id: int
    album_count: int = 0

# --- Artist ---
class ArtistBase(SQLModel):
    name: str = Field(index=True)

class Artist(ArtistBase, table=True):
    __tablename__ = "artists"
    id: Optional[int] = Field(default=None, primary_key=True)
    albums: List["Album"] = Relationship(back_populates="artists", link_model=AlbumArtistLink)

class ArtistRead(ArtistBase):
    id: int

# --- Location ---
class LocationBase(SQLModel):
    name: str
    storage_type: str
    section: Optional[str] = None
    shelf: Optional[str] = None
    position: Optional[str] = None

class Location(LocationBase, table=True):
    __tablename__ = "locations"
    id: Optional[int] = Field(default=None, primary_key=True)
    albums: List["Album"] = Relationship(back_populates="location")

class LocationRead(LocationBase):
    id: int

# --- Track ---
class TrackBase(SQLModel):
    track_no: int
    title: str
    duration: Optional[str] = None

class Track(TrackBase, table=True):
    __tablename__ = "tracks"
    id: Optional[int] = Field(default=None, primary_key=True)
    album_id: int = Field(foreign_key="albums.id")
    album: "Album" = Relationship(back_populates="tracks")

class TrackRead(TrackBase):
    id: int

# --- Album ---
class AlbumBase(SQLModel):
    title: str = Field(index=True)
    year: Optional[int] = None
    upc_ean: Optional[str] = Field(default=None, index=True)
    catalog_no: Optional[str] = None
    spars_code: Optional[str] = None
    cover_url: Optional[str] = None
    media_type: str = "CD"
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    archived_at: Optional[datetime] = None
    location_id: Optional[int] = Field(default=None, foreign_key="locations.id")

class Album(AlbumBase, table=True):
    __tablename__ = "albums"
    id: Optional[int] = Field(default=None, primary_key=True)
    
    location: Optional[Location] = Relationship(back_populates="albums")
    artists: List[Artist] = Relationship(back_populates="albums", link_model=AlbumArtistLink)
    tags: List[Tag] = Relationship(back_populates="albums", link_model=AlbumTagLink)
    genres: List[Genre] = Relationship(back_populates="albums", link_model=AlbumGenreLink)
    tracks: List[Track] = Relationship(back_populates="album")

# --- Create Models (DTOs) ---
class AlbumCreate(AlbumBase):
    tag_ids: List[int] = []
    artist_names: List[str] = []
    genre_names: List[str] = []

class AlbumUpdate(SQLModel):
    title: Optional[str] = None
    year: Optional[int] = None
    notes: Optional[str] = None
    media_type: Optional[str] = None
    spars_code: Optional[str] = None
    catalog_no: Optional[str] = None
    upc_ean: Optional[str] = None
    location_id: Optional[int] = None
    tag_ids: Optional[List[int]] = None
    genre_ids: Optional[List[int]] = None
    artist_names: Optional[List[str]] = None
    cover_url: Optional[str] = None

# --- Read Models (DTOs) ---
class AlbumRead(AlbumBase):
    id: int
    location: Optional[LocationRead] = None
    artists: List[ArtistRead] = []
    tags: List[TagRead] = []
    genres: List[GenreRead] = []
    tracks: List[TrackRead] = []