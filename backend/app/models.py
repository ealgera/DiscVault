from datetime import datetime
from typing import Optional, List
from sqlmodel import Field, SQLModel, Relationship

# --- Link Tables ---
class AlbumTagLink(SQLModel, table=True):
    album_id: Optional[int] = Field(default=None, foreign_key="album.id", primary_key=True)
    tag_id: Optional[int] = Field(default=None, foreign_key="tag.id", primary_key=True)

class AlbumArtistLink(SQLModel, table=True):
    album_id: Optional[int] = Field(default=None, foreign_key="album.id", primary_key=True)
    artist_id: Optional[int] = Field(default=None, foreign_key="artist.id", primary_key=True)
    role: Optional[str] = "Main"

# --- Genre ---
class GenreBase(SQLModel):
    name: str = Field(unique=True)

class Genre(GenreBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

# --- Tag ---
class TagBase(SQLModel):
    name: str = Field(index=True, unique=True)
    color: str = "#CCCCCC"

class Tag(TagBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    albums: List["Album"] = Relationship(back_populates="tags", link_model=AlbumTagLink)

class TagRead(TagBase):
    id: int

# --- Artist ---
class ArtistBase(SQLModel):
    name: str = Field(index=True)

class Artist(ArtistBase, table=True):
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
    id: Optional[int] = Field(default=None, primary_key=True)
    album_id: int = Field(foreign_key="album.id")
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
    genre_id: Optional[int] = Field(default=None, foreign_key="genre.id")
    location_id: Optional[int] = Field(default=None, foreign_key="location.id")

class Album(AlbumBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    
    location: Optional[Location] = Relationship(back_populates="albums")
    artists: List[Artist] = Relationship(back_populates="albums", link_model=AlbumArtistLink)
    tags: List[Tag] = Relationship(back_populates="albums", link_model=AlbumTagLink)
    tracks: List[Track] = Relationship(back_populates="album")

# --- Read Models (DTOs) ---
class AlbumRead(AlbumBase):
    id: int
    location: Optional[LocationRead] = None
    artists: List[ArtistRead] = []
    tags: List[TagRead] = []
    tracks: List[TrackRead] = []