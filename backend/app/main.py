from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from sqlmodel import Session, select, text
from typing import List

from .database import create_db_and_tables, get_session, engine
from .models import Album, Artist, Tag, Location, AlbumRead
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
    session.commit()

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    with Session(engine) as session:
        init_fts(session)
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
    # Using the FTS5 table for searching with prefix matching (*)
    query = text("SELECT rowid FROM album_search WHERE album_search MATCH :q")
    # We add * to the query for prefix matching (e.g. "pin" matches "pink")
    results = session.execute(query, {"q": f"{q}*"}).all()
    
    if not results:
        return []
    
    ids = [r[0] for r in results]
    # Fetch the full objects for the IDs found
    albums = session.exec(select(Album).where(Album.id.in_(ids))).all()
    return albums

# --- Album Endpoints ---
@app.post("/albums/", response_model=Album)
def create_album(album: Album, session: Session = Depends(get_session)):
    return crud.create_album(session=session, album=album)

@app.get("/albums/", response_model=List[AlbumRead])
def read_albums(offset: int = 0, limit: int = 100, session: Session = Depends(get_session)):
    return crud.get_albums(session=session, offset=offset, limit=limit)

@app.get("/albums/{album_id}", response_model=AlbumRead)
def read_album(album_id: int, session: Session = Depends(get_session)):
    album = crud.get_album(session=session, album_id=album_id)
    if not album:
        raise HTTPException(status_code=404, detail="Album not found")
    return album

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

# --- Location Endpoints ---
@app.post("/locations/", response_model=Location)
def create_location(location: Location, session: Session = Depends(get_session)):
    return crud.create_location(session=session, location=location)

@app.get("/locations/", response_model=List[Location])
def read_locations(session: Session = Depends(get_session)):
    return crud.get_locations(session=session)

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
