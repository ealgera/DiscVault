import httpx
from typing import Optional, Dict, Any

MUSICBRAINZ_API = "https://musicbrainz.org/ws/2"
USER_AGENT = "DiscVault/0.1.0 ( https://github.com/eric/discvault )"

async def lookup_musicbrainz_by_barcode(barcode: str) -> Optional[Dict[str, Any]]:
    # we use 'barcode' filter in release query
    url = f"{MUSICBRAINZ_API}/release/"
    params = {
        "query": f"barcode:{barcode}",
        "fmt": "json"
    }
    headers = {"User-Agent": USER_AGENT}
    
    async with httpx.AsyncClient() as client:
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
        
        # Check Cover Art Archive (Optimistic check, or just construct URL)
        # We use the 'front-500' thumbnail for better performance (original can be huge)
        # Or even 'front-250' if we want it super fast for mobile lists.
        cover_url = f"https://coverartarchive.org/release/{mbid}/front-250" if mbid else None

        # Map MB data to our internal format
        result = {
            "title": release.get("title"),
            "year": int(release.get("date", "0")[:4]) if release.get("date") else None,
            "artists": [a.get("artist", {}).get("name") for a in release.get("artist-credit", [])],
            "barcode": barcode,
            "mbid": mbid,
            "catalog_no": release.get("label-info", [{}])[0].get("catalog-number") if release.get("label-info") else None,
            "cover_url": cover_url
        }
        return result
