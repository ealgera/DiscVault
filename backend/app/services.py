import httpx
from typing import Optional, Dict, Any

MUSICBRAINZ_API = "https://musicbrainz.org/ws/2"
USER_AGENT = "DiscVault/0.1.0 ( https://github.com/eric/discvault )"

async def lookup_musicbrainz_by_barcode(barcode: str) -> Optional[Dict[str, Any]]:
    # we use 'barcode' filter in release query
    # added inc=tags to get genres
    url = f"{MUSICBRAINZ_API}/release/"
    params = {
        "query": f"barcode:{barcode}",
        "fmt": "json"
    }
    headers = {"User-Agent": USER_AGENT}
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.get(url, params=params, headers=headers)
            if response.status_code != 200:
                return None
            
            data = response.json()
            releases = data.get("releases", [])
            
            if not releases:
                return None
            
            # We take the first match
            release = releases[0]
            mbid = release.get("id")
            
            # To get better genres and TRACKS, we need a detailed lookup
            # inc=recordings+media gives us the tracklist
            # inc=tags/release-groups gives us genres
            tracks = []
            if mbid:
                try:
                    detail_url = f"{MUSICBRAINZ_API}/release/{mbid}"
                    detail_params = {"inc": "recordings+media+tags+release-groups", "fmt": "json"}
                    detail_res = await client.get(detail_url, params=detail_params, headers=headers)
                    if detail_res.status_code == 200:
                        detail_data = detail_res.json()
                        
                        # 1. Genres from release-group or release tags
                        tags = detail_data.get("tags", [])
                        if not tags:
                            tags = detail_data.get("release-group", {}).get("tags", [])
                        
                        if tags:
                            tags.sort(key=lambda x: x.get("count", 0), reverse=True)
                            genres = [t.get("name").title() for t in tags[:5]]
                        
                        # 2. Tracks from media (discs)
                        media_list = detail_data.get("media", [])
                        for i, media in enumerate(media_list):
                            disc_no = i + 1
                            disc_format = media.get("format", f"Disc {disc_no}")
                            for track in media.get("tracks", []):
                                duration_ms = track.get("length")
                                duration_str = None
                                if duration_ms:
                                    s = duration_ms // 1000
                                    m, s = divmod(s, 60)
                                    duration_str = f"{m}:{s:02d}"
                                
                                tracks.append({
                                    "track_no": int(track.get("number", "0")),
                                    "title": track.get("recording", {}).get("title") or track.get("title"),
                                    "duration": duration_str,
                                    "disc_no": disc_no,
                                    "disc_name": disc_format
                                })
                except Exception as e:
                    print(f"Error fetching MB details: {e}")

            # Check Cover Art Archive 
            cover_url = f"https://coverartarchive.org/release/{mbid}/front-250" if mbid else None

            # Map MB data to our internal format
            result = {
                "title": release.get("title"),
                "year": int(release.get("date", "0")[:4]) if release.get("date") else None,
                "artists": [a.get("artist", {}).get("name") for a in release.get("artist-credit", [])],
                "genres": genres,
                "barcode": barcode,
                "mbid": mbid,
                "catalog_no": release.get("label-info", [{}])[0].get("catalog-number") if release.get("label-info") else None,
                "cover_url": cover_url,
                "tracks": tracks
            }
            return result
        except httpx.RequestError as e:
            print(f"Network error during MusicBrainz lookup: {e}")
            return None
