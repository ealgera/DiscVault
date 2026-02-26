import csv
import io
import httpx
import os
from pathlib import Path
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)

async def download_image(url: str, dest_path: Path) -> Optional[str]:
    """
    Downloads an image from a URL and saves it to dest_path.
    Returns the filename if successful, None otherwise.
    """
    if not url or not url.startswith("http"):
        return None
        
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url, follow_redirects=True)
            if response.status_code == 200:
                # Ensure directory exists
                dest_path.parent.mkdir(parents=True, exist_ok=True)
                
                with dest_path.open("wb") as f:
                    f.write(response.content)
                logger.info(f"Successfully downloaded {url} to {dest_path}")
                return dest_path.name
            else:
                logger.error(f"Failed to download image from {url}: Status {response.status_code} - Body: {response.text[:100]}")
    except Exception as e:
        logger.error(f"Error downloading image from {url}: {type(e).__name__}: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        
    return None

def parse_tracklist_csv(text: str) -> List[Dict]:
    """
    Parses a raw text string as CSV into a list of track dictionaries.
    Expected format: <tracknr>, <tracktitel>, <trackduur>
    """
    # Use io.StringIO to treat the string as a file for the csv module
    f = io.StringIO(text.strip())
    # DictReader would be nice but the user input doesn't have headers
    # We use a simple reader and map the columns ourselves
    reader = csv.reader(f, skipinitialspace=True)
    
    parsed_tracks = []
    
    for i, row in enumerate(reader):
        if not row:
            continue
            
        # Try to extract data based on column count
        # Default values
        track_no = i + 1
        title = ""
        duration = None
        
        if len(row) >= 3:
            # Full format: nr, title, duration
            try:
                track_no = int(row[0])
            except ValueError:
                track_no = i + 1
            title = row[1]
            duration = row[2]
        elif len(row) == 2:
            # Short format: title, duration OR nr, title
            # Let's check if the first column is a number
            try:
                track_no = int(row[0])
                title = row[1]
            except ValueError:
                title = row[0]
                duration = row[1]
        elif len(row) == 1:
            # Minimal format: title only
            title = row[0]
            
        parsed_tracks.append({
            "position": track_no,
            "title": title.strip() if title else f"Track {i+1}",
            "duration": duration.strip() if duration else None,
            "disc_no": 1
        })
        
    return parsed_tracks
