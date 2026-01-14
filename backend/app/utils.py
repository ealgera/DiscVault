import csv
import io
from typing import List, Dict

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
