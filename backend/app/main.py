from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from sqlmodel import Session
from typing import List

from .database import create_db_and_tables, get_session
from .models import Album, Artist, Tag, Location, AlbumRead
from . import crud

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
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
