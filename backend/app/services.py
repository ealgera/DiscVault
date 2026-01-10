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
            
            # To get better genres, we might need a separate call to the release-group or use tags from the release
            # For simplicity, we check if tags are in the release object or fetch release-group tags
            genres = []
            release_group = release.get("release-group", {})
            rg_id = release_group.get("id")
            
            if rg_id:
                try:
                    rg_url = f"{MUSICBRAINZ_API}/release-group/{rg_id}"
                    rg_params = {"inc": "tags", "fmt": "json"}
                    rg_res = await client.get(rg_url, params=rg_params, headers=headers)
                    if rg_res.status_code == 200:
                        rg_data = rg_res.json()
                        # Sort tags by count to get best genres
                        tags = rg_data.get("tags", [])
                        if tags:
                            # Filter tags that are likely genres (MusicBrainz tags are messy)
                            # We take top 3 tags as genres
                            tags.sort(key=lambda x: x.get("count", 0), reverse=True)
                            genres = [t.get("name").title() for t in tags[:5]]
                except Exception as e:
                    print(f"Error fetching genres: {e}")
                    # Continue without genres

            # Check Cover Art Archive (Optimistic check, or just construct URL)
            # We use the 'front-500' thumbnail for better performance (original can be huge)
            # Or even 'front-250' if we want it super fast for mobile lists.
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
                "cover_url": cover_url
            }
            return result
        except httpx.RequestError as e:
            print(f"Network error during MusicBrainz lookup: {e}")
            return None
