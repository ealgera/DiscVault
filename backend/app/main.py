from fastapi import FastAPI, Depends, HTTPException, File, UploadFile, Query, BackgroundTasks, Body, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from sqlmodel import Session, select, text, func
from sqlalchemy.orm import selectinload
from typing import List, Optional
import os
import shutil
from pathlib import Path
import zipfile
import tempfile
import json
from datetime import datetime
from fastapi.responses import FileResponse

from .database import create_db_and_tables, get_session, engine
from .models import Album, Artist, Tag, Location, AlbumRead, AlbumCreate, AlbumUpdate, AlbumArtistLink, AlbumTagLink, AlbumGenreLink, Genre, GenreRead, TagRead
from . import crud, services, utils
from pydantic import BaseModel

def init_fts(session: Session):
    # Create FTS5 virtual table for albums if it doesn't exist
    session.exec(text("CREATE VIRTUAL TABLE IF NOT EXISTS album_search USING fts5(title, notes, content='albums', content_rowid='id');"))
    
    # Triggers to keep FTS index in sync
    session.exec(text("""
    CREATE TRIGGER IF NOT EXISTS album_ai AFTER INSERT ON albums BEGIN
      INSERT INTO album_search(rowid, title, notes) VALUES (new.id, new.title, new.notes);
    END;
    """))
    session.exec(text("""
    CREATE TRIGGER IF NOT EXISTS album_ad AFTER DELETE ON albums BEGIN
      INSERT INTO album_search(album_search, rowid, title, notes) VALUES('delete', old.id, old.title, old.notes);
    END;
    """))
    session.exec(text("""
    CREATE TRIGGER IF NOT EXISTS album_au AFTER UPDATE ON albums BEGIN
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

default_data_dir = Path(__file__).parent.parent.parent / "data"
data_dir = os.getenv("DATA_DIR", str(default_data_dir))
COVERS_DIR = Path(data_dir) / "covers"

@asynccontextmanager
async def lifespan(app: FastAPI):
    COVERS_DIR.mkdir(exist_ok=True)
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

app.mount("/covers", StaticFiles(directory=COVERS_DIR), name="covers")

@app.get("/")
def read_root():
    return {"message": "Welcome to DiscVault API", "version": "1.5.0"}

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/stats")
def read_stats(session: Session = Depends(get_session)):
    return crud.get_stats(session)

@app.get("/constants")
def read_constants():
    return {
        "media_types": ['CD', 'CD-R', 'CD-Single', 'SACD', 'Blu-ray Video', 'Blu-ray Audio', 'DVD Audio', 'Digital', 'Vinyl']
    }

@app.get("/search", response_model=List[AlbumRead])
def search_albums(q: str, filter: str = "all", sort_by: str = "created_at", order: str = "desc", session: Session = Depends(get_session)):
    q_lower = q.lower().strip()
    
    results = []
    
    # helper for AND logic on tags/genres
    def search_with_logic(model, link_model, attr_name):
        nonlocal results
        # Check for AND/OR
        if " and " in q_lower:
            terms = [t.strip() for t in q_lower.split(" and ") if t.strip()]
            if not terms: return
            
            # For AND, we need albums that have ALL terms. 
            # We find IDs that match each term and then intersect.
            id_sets = []
            for term in terms:
                stmt = select(Album.id).join(link_model).join(model).where(func.lower(getattr(model, attr_name)).contains(term))
                id_sets.append(set(session.exec(stmt).all()))
            
            if not id_sets: return
            matching_ids = set.intersection(*id_sets)
            if matching_ids:
                results += session.exec(select(Album).where(Album.id.in_(list(matching_ids)))).all()
        
        elif " or " in q_lower:
            terms = [t.strip() for t in q_lower.split(" or ") if t.strip()]
            if not terms: return
            
            # For OR, any term matches.
            from sqlmodel import or_
            stmt = select(Album).join(link_model).join(model).where(
                or_(*[func.lower(getattr(model, attr_name)).contains(term) for term in terms])
            )
            results += session.exec(stmt).all()
        else:
            # Standard single term search
            results += session.exec(select(Album).join(link_model).join(model).where(func.lower(getattr(model, attr_name)).contains(q_lower))).all()

    # 1. Search by Title
    if filter in ["all", "title"]:
        results += session.exec(select(Album).where(func.lower(Album.title).contains(q_lower))).all()
    
    # 2. Search by Artist Name
    if filter in ["all", "artist"]:
        # We can also support AND/OR for artists if we want, but requirements specifically mentioned genres/tags
        results += session.exec(select(Album).join(AlbumArtistLink).join(Artist).where(func.lower(Artist.name).contains(q_lower))).all()
    
    # 3. Search by Notes
    if filter == "all":
        results += session.exec(select(Album).where(func.lower(Album.notes).contains(q_lower))).all()

    # 4. Search by Genre
    if filter in ["all", "genre"]:
        search_with_logic(Genre, AlbumGenreLink, "name")

    # 5. Search by Tag
    if filter in ["all", "tag"]:
        search_with_logic(Tag, AlbumTagLink, "name")
        
    # 6. Search by Track Title
    if filter in ["all", "track"]:
        # Join Tracks and filter by title
        from .models import Track
        results += session.exec(select(Album).join(Track).where(func.lower(Track.title).contains(q_lower))).all()

    # 7. Search by Media Type
    if filter in ["all", "media_type"]:
        results += session.exec(select(Album).where(func.lower(Album.media_type).contains(q_lower))).all()

    # Combine and Deduplicate (by ID)
    seen_ids = set()
    deduped_ids = []
    for album in results:
        if album.id not in seen_ids:
            deduped_ids.append(album.id)
            seen_ids.add(album.id)
    
    if not deduped_ids:
        return []

    # Final query to get full objects with relations and APPLY SORTING
    return crud.get_albums(session, offset=0, limit=1000, sort_by=sort_by, order=order, album_ids=deduped_ids)

# --- Album Endpoints ---
@app.post("/albums/", response_model=Album)
def create_album(album: AlbumCreate, session: Session = Depends(get_session)):
    return crud.create_album(session=session, album_create=album)

@app.get("/albums/check-duplicate", response_model=List[AlbumRead])
def check_duplicate(
    title: str, 
    artist_names: List[str] = Query([]), 
    upc_ean: Optional[str] = None, 
    session: Session = Depends(get_session)
):
    return crud.check_duplicate_album(session, title=title, artist_names=artist_names, upc_ean=upc_ean)

@app.get("/albums/", response_model=List[AlbumRead])
def read_albums(offset: int = 0, limit: int = 100, sort_by: str = "created_at", order: str = "desc", session: Session = Depends(get_session)):
    return crud.get_albums(session=session, offset=offset, limit=limit, sort_by=sort_by, order=order)

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

@app.get("/tags/", response_model=List[TagRead])
def read_tags(session: Session = Depends(get_session)):
    return crud.get_tags(session=session)

@app.put("/tags/{tag_id}", response_model=Tag)
def update_tag(tag_id: int, tag: Tag, session: Session = Depends(get_session)):
    updated_tag = crud.update_tag(session=session, tag_id=tag_id, tag_data=tag)
    if not updated_tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    return updated_tag

# --- Genre Endpoints ---
@app.post("/genres/", response_model=Genre)
def create_genre(genre: Genre, session: Session = Depends(get_session)):
    session.add(genre)
    session.commit()
    session.refresh(genre)
    return genre

@app.get("/genres/", response_model=List[GenreRead])
def read_genres(session: Session = Depends(get_session)):
    return crud.get_genres(session=session)

@app.put("/genres/{genre_id}", response_model=Genre)
def update_genre(genre_id: int, genre: Genre, session: Session = Depends(get_session)):
    updated_genre = crud.update_genre(session=session, genre_id=genre_id, genre_data=genre)
    if not updated_genre:
        raise HTTPException(status_code=404, detail="Genre not found")
    return updated_genre

@app.delete("/genres/{genre_id}")
def delete_genre(genre_id: int, session: Session = Depends(get_session)):
    success = crud.delete_genre(session=session, genre_id=genre_id)
    if not success:
        raise HTTPException(status_code=404, detail="Genre not found")
    return {"ok": True}

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

@app.post("/albums/{album_id}/cover")
async def upload_album_cover(album_id: int, file: UploadFile = File(...), session: Session = Depends(get_session)):
    album = crud.get_album(session, album_id)
    if not album:
        raise HTTPException(status_code=404, detail="Album not found")
    
    # Save file
    file_extension = os.path.splitext(file.filename)[1]
    file_path = COVERS_DIR / f"album_{album_id}{file_extension}"
    
    with file_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Update DB
    cover_url = f"/covers/{file_path.name}"
    crud.update_album(session, album_id, AlbumUpdate(cover_url=cover_url))
    
    return {"cover_url": cover_url}

@app.post("/albums/{album_id}/sync", response_model=AlbumRead)
async def sync_album_with_musicbrainz(album_id: int, session: Session = Depends(get_session)):
    db_album = crud.get_album(session, album_id)
    if not db_album:
        raise HTTPException(status_code=404, detail="Album not found")
    
    if not db_album.upc_ean:
        raise HTTPException(status_code=400, detail="Album has no barcode for syncing")
    
    # Fetch data from MusicBrainz
    mb_data = await services.lookup_musicbrainz_by_barcode(db_album.upc_ean)
    if not mb_data:
        raise HTTPException(status_code=404, detail="Could not find album on MusicBrainz")
    
    # Prepare update
    # We prioritize MB data for tracks and genres, and potentially catalog_no/year if missing
    update_params = {
        "artist_names": mb_data.get("artists"),
        "genre_names": mb_data.get("genres"),
        "tracks": mb_data.get("tracks")
    }
    
    # Only update title/year/catalog_no if they are currently null or empty
    if not db_album.title:
        update_params["title"] = mb_data.get("title")
    if not db_album.year:
        update_params["year"] = mb_data.get("year")
    if not db_album.catalog_no:
        update_params["catalog_no"] = mb_data.get("catalog_no")
    if not db_album.cover_url:
        update_params["cover_url"] = mb_data.get("cover_url")

    # Use AlbumUpdate to validate (though crud.update_album does it too)
    album_update = AlbumUpdate(**{k: v for k, v in update_params.items() if v is not None})
    
    updated_album = crud.update_album(session, album_id, album_update)
    return updated_album

# --- Relationships ---
@app.post("/albums/{album_id}/artists/{artist_id}")
def link_artist_to_album(album_id: int, artist_id: int, role: str = "Main", session: Session = Depends(get_session)):
    # Check if exist (basic check)
    album = crud.get_album(session, album_id)
    if not album:
         raise HTTPException(status_code=404, detail="Album not found")
    # In a real app check for artist too and duplicates
    
    return crud.add_artist_to_album(session=session, album_id=album_id, artist_id=artist_id, role=role)

# --- Bulk Track Parsing ---
@app.post("/tracks/parse")
async def parse_tracks(
    text: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None)
):
    """
    Parse a tracklist from pasted text or a TXT file via FormData.
    """
    text_content = ""
    
    if file:
        content = await file.read()
        text_content = content.decode('utf-8', errors='ignore')
    elif text:
        text_content = text
    else:
        raise HTTPException(status_code=400, detail="Geen tekst of bestand ontvangen.")
        
    if not text_content.strip():
        raise HTTPException(status_code=400, detail="Inhoud is leeg.")
        
    parsed = utils.parse_tracklist_csv(text_content)
    return parsed

# --- Backup & Restore ---
@app.get("/export")
def export_collection(background_tasks: BackgroundTasks, session: Session = Depends(get_session)):
    """
    Export the entire collection (database + covers) as a ZIP file.
    """
    temp_dir = tempfile.mkdtemp()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    zip_filename = f"discvault_backup_{timestamp}.zip"
    zip_path = os.path.join(temp_dir, zip_filename)
    
    from .database import sqlite_file_name
    db_path = sqlite_file_name
    
    # 2. Create manifest
    album_count = session.exec(select(func.count(Album.id))).one()
    manifest = {
        "version": "1.5.0",
        "date": datetime.now().isoformat(),
        "album_count": album_count
    }
    
    try:
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            # Add DB
            if os.path.exists(db_path):
                zip_file.write(db_path, "discvault.db")
            
            # Add Covers
            if os.path.exists(COVERS_DIR):
                for root, dirs, files in os.walk(COVERS_DIR):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.join("covers", os.path.relpath(file_path, COVERS_DIR))
                        zip_file.write(file_path, arcname)
            
            # Add manifest
            manifest_path = os.path.join(temp_dir, "manifest.json")
            with open(manifest_path, 'w') as f:
                json.dump(manifest, f)
            zip_file.write(manifest_path, "manifest.json")

        background_tasks.add_task(lambda: shutil.rmtree(temp_dir))
        return FileResponse(zip_path, filename=zip_filename, media_type="application/zip")
    except Exception as e:
        shutil.rmtree(temp_dir)
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")

@app.post("/import")
async def import_collection(file: UploadFile = File(...), session: Session = Depends(get_session)):
    """
    Restore the collection from a ZIP backup. WARNING: Overwrites current data.
    """
    if not file.filename.endswith(".zip"):
        raise HTTPException(status_code=400, detail="Ongeldig bestandstype. Upload een ZIP-bestand.")
    
    temp_dir = tempfile.mkdtemp()
    zip_path = os.path.join(temp_dir, "import.zip")
    
    try:
        with open(zip_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)
            
        # Validate
        import_db_path = os.path.join(temp_dir, "discvault.db")
        if not os.path.exists(import_db_path):
             raise HTTPException(status_code=400, detail="Ongeldige backup: discvault.db ontbreekt.")
        
        # Replace Covers
        import_covers_dir = os.path.join(temp_dir, "covers")
        if os.path.exists(import_covers_dir):
            if os.path.exists(COVERS_DIR):
                shutil.rmtree(COVERS_DIR)
            shutil.copytree(import_covers_dir, COVERS_DIR)
            
        # Replace DB
        from .database import sqlite_file_name
        shutil.copy(import_db_path, sqlite_file_name)
        
        return {"message": "Import succesvol. Herlaad de app."}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Import mislukt: {str(e)}")
    finally:
        shutil.rmtree(temp_dir)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
