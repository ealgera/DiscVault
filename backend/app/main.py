from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from sqlmodel import Session, select, text, func
from typing import List

from .database import create_db_and_tables, get_session, engine
from .models import Album, Artist, Tag, Location, AlbumRead, AlbumCreate, AlbumUpdate, AlbumArtistLink
from . import crud, services

def init_fts(session: Session):
    # Create FTS5 virtual table for albums if it doesn't exist
    session.exec(text("CREATE VIRTUAL TABLE IF NOT EXISTS album_search USING fts5(title, notes, content='album', content_rowid='id');"))
    
    # Triggers to keep FTS index in sync
    session.exec(text("""
    CREATE TRIGGER IF NOT EXISTS album_ai AFTER INSERT ON album BEGIN
      INSERT INTO album_search(rowid, title, notes) VALUES (new.id, new.title, new.notes);
    END;
    """))
    session.exec(text("""
    CREATE TRIGGER IF NOT EXISTS album_ad AFTER DELETE ON album BEGIN
      INSERT INTO album_search(album_search, rowid, title, notes) VALUES('delete', old.id, old.title, old.notes);
    END;
    """))
    session.exec(text("""
    CREATE TRIGGER IF NOT EXISTS album_au AFTER UPDATE ON album BEGIN
      INSERT INTO album_search(album_search, rowid, title, notes) VALUES('delete', old.id, old.title, old.notes);
      INSERT INTO album_search(rowid, title, notes) VALUES (new.id, new.title, new.notes);
    END;
    """))
    
    # Force rebuild of the FTS index to ensure existing data is indexed (Good for dev/small dbs)
    session.exec(text("INSERT INTO album_search(album_search) VALUES('rebuild');"))
    
    session.commit()

def seed_data(session: Session):
    # Ensure 'Favoriet' tag exists
    fav_tag = session.exec(select(Tag).where(Tag.name == "Favoriet")).first()
    if not fav_tag:
        session.add(Tag(name="Favoriet", color="#ef4444")) # Red color
        session.commit()

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    with Session(engine) as session:
        init_fts(session)
        seed_data(session)
    yield

app = FastAPI(title="DiscVault API", lifespan=lifespan)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow all for dev, restrict in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Welcome to DiscVault API"}

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/stats")
def read_stats(session: Session = Depends(get_session)):
    return crud.get_stats(session)

@app.get("/search", response_model=List[AlbumRead])
def search_albums(q: str, session: Session = Depends(get_session)):
    q_lower = q.lower()
    
    # 1. Search by Title (case-insensitive contains)
    title_results = session.exec(select(Album).where(func.lower(Album.title).contains(q_lower))).all()
    
    # 2. Search by Artist Name (case-insensitive contains)
    artist_results = session.exec(select(Album).join(AlbumArtistLink).join(Artist).where(func.lower(Artist.name).contains(q_lower))).all()
    
    # 3. Search by Notes (case-insensitive contains)
    notes_results = session.exec(select(Album).where(func.lower(Album.notes).contains(q_lower))).all()

    # Combine and Deduplicate (by ID)
    seen_ids = set()
    combined_results = []
    
    for album in title_results + artist_results + notes_results:
        if album.id not in seen_ids:
            combined_results.append(album)
            seen_ids.add(album.id)
            
    return combined_results

# --- Album Endpoints ---
@app.post("/albums/", response_model=Album)
def create_album(album: AlbumCreate, session: Session = Depends(get_session)):
    return crud.create_album(session=session, album_create=album)

@app.get("/albums/", response_model=List[AlbumRead])
def read_albums(offset: int = 0, limit: int = 100, session: Session = Depends(get_session)):
    return crud.get_albums(session=session, offset=offset, limit=limit)

@app.get("/albums/{album_id}", response_model=AlbumRead)
def read_album(album_id: int, session: Session = Depends(get_session)):
    album = crud.get_album(session=session, album_id=album_id)
    if not album:
        raise HTTPException(status_code=404, detail="Album not found")
    return album

@app.put("/albums/{album_id}", response_model=AlbumRead)
def update_album(album_id: int, album_update: AlbumUpdate, session: Session = Depends(get_session)):
    updated_album = crud.update_album(session=session, album_id=album_id, album_update=album_update)
    if not updated_album:
        raise HTTPException(status_code=404, detail="Album not found")
    return updated_album

# --- Artist Endpoints ---
@app.post("/artists/", response_model=Artist)
def create_artist(artist: Artist, session: Session = Depends(get_session)):
    return crud.create_artist(session=session, artist=artist)

@app.get("/artists/", response_model=List[Artist])
def read_artists(session: Session = Depends(get_session)):
    return crud.get_artists(session=session)

# --- Tag Endpoints ---
@app.post("/tags/", response_model=Tag)
def create_tag(tag: Tag, session: Session = Depends(get_session)):
    return crud.create_tag(session=session, tag=tag)

@app.get("/tags/", response_model=List[Tag])
def read_tags(session: Session = Depends(get_session)):
    return crud.get_tags(session=session)

@app.put("/tags/{tag_id}", response_model=Tag)
def update_tag(tag_id: int, tag: Tag, session: Session = Depends(get_session)):
    updated_tag = crud.update_tag(session=session, tag_id=tag_id, tag_data=tag)
    if not updated_tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    return updated_tag

# --- Location Endpoints ---
@app.post("/locations/", response_model=Location)
def create_location(location: Location, session: Session = Depends(get_session)):
    return crud.create_location(session=session, location=location)

@app.get("/locations/", response_model=List[Location])
def read_locations(session: Session = Depends(get_session)):
    return crud.get_locations(session=session)

@app.put("/locations/{location_id}", response_model=Location)
def update_location(location_id: int, location: Location, session: Session = Depends(get_session)):
    updated_location = crud.update_location(session=session, location_id=location_id, location_data=location)
    if not updated_location:
        raise HTTPException(status_code=404, detail="Location not found")
    return updated_location

# --- External Lookup ---
@app.get("/lookup/{barcode}")
async def lookup_barcode(barcode: str):
    result = await services.lookup_musicbrainz_by_barcode(barcode)
    if not result:
        raise HTTPException(status_code=404, detail="Barcode not found in MusicBrainz")
    return result

# --- Relationships ---
@app.post("/albums/{album_id}/artists/{artist_id}")
def link_artist_to_album(album_id: int, artist_id: int, role: str = "Main", session: Session = Depends(get_session)):
    # Check if exist (basic check)
    album = crud.get_album(session, album_id)
    if not album:
         raise HTTPException(status_code=404, detail="Album not found")
    # In a real app check for artist too and duplicates
    
    return crud.add_artist_to_album(session=session, album_id=album_id, artist_id=artist_id, role=role)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
