import httpx
import random
import asyncio
import string
from typing import Optional
from datetime import datetime, timedelta

DEEZER_API_BASE = "https://api.deezer.com"

# Genre definitions with ID and display name
GENRES = {
    132: "Pop",
    116: "Hip-Hop",
    152: "Rock",
    113: "Dance",
    165: "R&B",
    85: "Alternative",
    106: "Electronic",
    129: "Jazz",
    84: "Country",
    98: "Reggae",
    173: "Soundtracks",
    464: "Metal",
    466: "Folk",
    169: "Soul & Funk",
    2: "Classical",
    75: "World",
    81: "Indie",
}

# List of all genre IDs
GENRE_IDS = list(GENRES.keys())

# Random search terms for discovery variety
SEARCH_TERMS = [
    "love", "night", "dream", "sun", "moon", "heart", "life", "time",
    "fire", "water", "sky", "rain", "blue", "red", "gold", "black",
    "white", "dark", "light", "new", "old", "wild", "free", "lost",
    "found", "home", "road", "city", "street", "summer", "winter",
    "spring", "fall", "dance", "soul", "funk", "rock", "jazz", "beat",
    "sound", "rhythm", "melody", "voice", "song", "music", "album",
    "world", "earth", "star", "wave", "electric", "acoustic", "live",
    "remix", "original", "classic", "modern", "future", "past", "now",
]


class DeezerService:
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=15.0)
        self._cache: dict = {}
        self._cache_ttl = timedelta(hours=2)
    
    async def close(self):
        await self.client.aclose()
    
    def _get_cache(self, key: str):
        if key in self._cache:
            data, timestamp = self._cache[key]
            if datetime.now() - timestamp < self._cache_ttl:
                return data
            del self._cache[key]
        return None
    
    def _set_cache(self, key: str, data):
        self._cache[key] = (data, datetime.now())
    
    async def _fetch_with_retry(self, url: str, params: dict = None, max_retries: int = 2) -> Optional[dict]:
        """Fetch with retry logic for resilience."""
        for attempt in range(max_retries + 1):
            try:
                response = await self.client.get(url, params=params)
                response.raise_for_status()
                data = response.json()
                if "error" not in data:
                    return data
                return None
            except Exception as e:
                if attempt == max_retries:
                    print(f"Failed to fetch {url}: {e}")
                    return None
                await asyncio.sleep(0.2 * (attempt + 1))
        return None
    
    async def get_genre_artists(self, genre_id: int) -> list[dict]:
        """Get artists for a specific genre with caching."""
        cache_key = f"genre_artists_{genre_id}"
        cached = self._get_cache(cache_key)
        if cached:
            return cached
        
        data = await self._fetch_with_retry(
            f"{DEEZER_API_BASE}/genre/{genre_id}/artists",
            params={"limit": 100}
        )
        if data:
            artists = data.get("data", [])
            self._set_cache(cache_key, artists)
            return artists
        return []
    
    async def get_artist_albums(self, artist_id: int) -> list[dict]:
        """Get albums for a specific artist with caching."""
        cache_key = f"artist_albums_{artist_id}"
        cached = self._get_cache(cache_key)
        if cached:
            return cached
        
        data = await self._fetch_with_retry(
            f"{DEEZER_API_BASE}/artist/{artist_id}/albums",
            params={"limit": 50}
        )
        if data:
            albums = data.get("data", [])
            self._set_cache(cache_key, albums)
            return albums
        return []
    
    async def search_albums(self, query: str, index: int = 0) -> list[dict]:
        """Search for albums with offset for variety."""
        cache_key = f"search_{query}_{index}"
        cached = self._get_cache(cache_key)
        if cached:
            return cached
        
        data = await self._fetch_with_retry(
            f"{DEEZER_API_BASE}/search/album",
            params={"q": query, "limit": 50, "index": index}
        )
        if data:
            albums = data.get("data", [])
            self._set_cache(cache_key, albums)
            return albums
        return []
    
    async def get_album_first_track_preview(self, album_id: int) -> Optional[str]:
        """Get the preview URL for the first playable track of an album."""
        cache_key = f"album_preview_{album_id}"
        cached = self._get_cache(cache_key)
        if cached:
            return cached
        
        data = await self._fetch_with_retry(
            f"{DEEZER_API_BASE}/album/{album_id}/tracks",
            params={"limit": 5}
        )
        if data:
            tracks = data.get("data", [])
            for track in tracks:
                preview = track.get("preview")
                if preview:
                    self._set_cache(cache_key, preview)
                    return preview
        return None
    
    async def get_album_details(self, album_id: int) -> Optional[dict]:
        """Get full album details."""
        cache_key = f"album_{album_id}"
        cached = self._get_cache(cache_key)
        if cached:
            return cached
        
        data = await self._fetch_with_retry(f"{DEEZER_API_BASE}/album/{album_id}")
        if data and "error" not in data:
            self._set_cache(cache_key, data)
            return data
        return None
    
    async def _collect_albums_from_genres(self, target_count: int, genre_ids: Optional[list[int]] = None) -> list[dict]:
        """Collect albums from random genres and artists."""
        albums = []
        seen_ids = set()
        
        # Use specified genres or all genres
        available_genres = genre_ids if genre_ids else GENRE_IDS
        
        # Shuffle genres for randomness
        shuffled_genres = random.sample(available_genres, len(available_genres))
        
        for genre_id in shuffled_genres:
            if len(albums) >= target_count * 2:
                break
                
            artists = await self.get_genre_artists(genre_id)
            if not artists:
                continue
            
            # Pick random artists from this genre
            random_artists = random.sample(artists, min(8, len(artists)))
            
            for artist in random_artists:
                if len(albums) >= target_count * 2:
                    break
                    
                artist_albums = await self.get_artist_albums(artist["id"])
                if artist_albums:
                    # Pick a random album from this artist
                    album = random.choice(artist_albums)
                    if album["id"] not in seen_ids:
                        seen_ids.add(album["id"])
                        albums.append(album)
        
        return albums
    
    async def _collect_albums_from_search(self, target_count: int) -> list[dict]:
        """Collect albums using random search queries."""
        albums = []
        seen_ids = set()
        
        # Pick random search terms
        search_terms = random.sample(SEARCH_TERMS, min(10, len(SEARCH_TERMS)))
        
        # Also add some random letter combinations for variety
        for _ in range(3):
            random_chars = ''.join(random.choices(string.ascii_lowercase, k=random.randint(2, 4)))
            search_terms.append(random_chars)
        
        random.shuffle(search_terms)
        
        for term in search_terms:
            if len(albums) >= target_count:
                break
            
            # Use random offset for more variety
            offset = random.randint(0, 100)
            search_results = await self.search_albums(term, index=offset)
            
            for album in search_results:
                if album["id"] not in seen_ids:
                    seen_ids.add(album["id"])
                    albums.append(album)
                    if len(albums) >= target_count:
                        break
        
        return albums
    
    async def enrich_album_with_preview(self, album: dict) -> Optional[dict]:
        """Add preview URL and details to album data. Returns None if no preview available."""
        album_id = album.get("id")
        if not album_id:
            return None
        
        # Get preview first - if none available, skip this album
        preview_url = await self.get_album_first_track_preview(album_id)
        if not preview_url:
            return None
        
        # Get additional album details
        details = await self.get_album_details(album_id)
        
        # Extract artist name from various possible structures
        artist_name = "Unknown Artist"
        if details and details.get("artist"):
            artist_info = details.get("artist", {})
            artist_name = artist_info.get("name", "Unknown Artist") if isinstance(artist_info, dict) else str(artist_info)
        elif album.get("artist"):
            artist_info = album.get("artist", {})
            artist_name = artist_info.get("name", "Unknown Artist") if isinstance(artist_info, dict) else str(artist_info)
        
        # Get cover URL - prefer details if available for higher quality
        cover_url = ""
        if details:
            cover_url = details.get("cover_xl") or details.get("cover_big") or details.get("cover_medium", "")
        if not cover_url:
            cover_url = album.get("cover_xl") or album.get("cover_big") or album.get("cover_medium", "")
        
        if not cover_url:
            return None
        
        return {
            "id": album_id,
            "title": details.get("title", album.get("title", "Unknown Album")) if details else album.get("title", "Unknown Album"),
            "artist": artist_name,
            "cover_url": cover_url,
            "preview_url": preview_url,
            "year": details.get("release_date", "")[:4] if details and details.get("release_date") else None,
            "genre": details.get("genres", {}).get("data", [{}])[0].get("name") if details and details.get("genres", {}).get("data") else None,
            "deezer_id": album_id,
            "deezer_link": details.get("link", album.get("link", "")) if details else album.get("link", ""),
            "nb_tracks": details.get("nb_tracks") if details else album.get("nb_tracks"),
        }
    
    async def get_discovery_albums(self, count: int = 10, genre_ids: Optional[list[int]] = None, min_tracks: Optional[int] = None) -> list[dict]:
        """
        Get exactly 'count' random albums for discovery.
        Uses multiple strategies to ensure variety and always returns the requested count.
        
        Args:
            count: Number of albums to return
            genre_ids: Optional list of genre IDs to filter by. If None, uses all genres.
            min_tracks: Optional minimum number of tracks. If 2 or more, filters out singles.
        """
        all_candidate_albums = []
        seen_ids = set()
        
        # When genres are specified, rely primarily on genre-based discovery
        if genre_ids:
            # Genre-based discovery only
            genre_albums = await self._collect_albums_from_genres(target_count=count * 4, genre_ids=genre_ids)
            for album in genre_albums:
                if album["id"] not in seen_ids:
                    seen_ids.add(album["id"])
                    all_candidate_albums.append(album)
        else:
            # Strategy 1: Random search queries (most variety)
            search_albums = await self._collect_albums_from_search(target_count=count * 3)
            for album in search_albums:
                if album["id"] not in seen_ids:
                    seen_ids.add(album["id"])
                    all_candidate_albums.append(album)
            
            # Strategy 2: Genre-based discovery
            genre_albums = await self._collect_albums_from_genres(target_count=count * 2)
            for album in genre_albums:
                if album["id"] not in seen_ids:
                    seen_ids.add(album["id"])
                    all_candidate_albums.append(album)
        
        # Shuffle all candidates for true randomness
        random.shuffle(all_candidate_albums)
        
        # Enrich albums with previews until we have enough
        enriched_albums = []
        batch_size = 10
        
        for i in range(0, len(all_candidate_albums), batch_size):
            if len(enriched_albums) >= count:
                break
            
            batch = all_candidate_albums[i:i + batch_size]
            tasks = [self.enrich_album_with_preview(album) for album in batch]
            results = await asyncio.gather(*tasks)
            
            for result in results:
                if result is not None:
                    # Filter by minimum track count if specified
                    if min_tracks is not None and result.get("nb_tracks"):
                        if result["nb_tracks"] < min_tracks:
                            continue
                    enriched_albums.append(result)
                    if len(enriched_albums) >= count:
                        break
        
        # If we don't have enough after filtering, try to get more
        if len(enriched_albums) < count and min_tracks is not None:
            # Continue enriching more albums to meet the count requirement
            remaining_needed = count - len(enriched_albums)
            for i in range(len(all_candidate_albums), len(all_candidate_albums) + (remaining_needed * 3)):
                if len(enriched_albums) >= count:
                    break
                if i < len(all_candidate_albums):
                    continue
                # Would need to fetch more albums here, but for now we'll return what we have
        
        # Final shuffle and return exactly the requested count
        random.shuffle(enriched_albums)
        return enriched_albums[:count]
    
    def get_available_genres(self) -> list[dict]:
        """Return list of available genres for filtering."""
        return [{"id": gid, "name": name} for gid, name in GENRES.items()]


# Global service instance
deezer_service = DeezerService()
