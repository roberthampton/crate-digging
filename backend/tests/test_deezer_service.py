"""
Unit tests for the Deezer service.
Tests the DeezerService class methods and data transformations.
"""
import pytest
from deezer_service import DeezerService, GENRES, GENRE_IDS, SEARCH_TERMS


class TestGenreConstants:
    """Tests for genre-related constants."""
    
    def test_genres_dict_not_empty(self):
        """GENRES dictionary should contain genre mappings."""
        assert len(GENRES) > 0
    
    def test_genre_ids_matches_genres(self):
        """GENRE_IDS list should match keys in GENRES dict."""
        assert set(GENRE_IDS) == set(GENRES.keys())
    
    def test_genres_have_string_names(self):
        """All genre names should be strings."""
        for genre_id, name in GENRES.items():
            assert isinstance(genre_id, int)
            assert isinstance(name, str)
            assert len(name) > 0


class TestSearchTerms:
    """Tests for search term constants."""
    
    def test_search_terms_not_empty(self):
        """SEARCH_TERMS should contain search terms."""
        assert len(SEARCH_TERMS) > 0
    
    def test_search_terms_are_strings(self):
        """All search terms should be non-empty strings."""
        for term in SEARCH_TERMS:
            assert isinstance(term, str)
            assert len(term) > 0


class TestDeezerServiceInit:
    """Tests for DeezerService initialization."""
    
    def test_service_creates_client(self):
        """Service should create an HTTP client on init."""
        service = DeezerService()
        assert service.client is not None
    
    def test_service_has_cache(self):
        """Service should have a cache dictionary."""
        service = DeezerService()
        assert hasattr(service, "_cache")
        assert isinstance(service._cache, dict)


class TestGetAvailableGenres:
    """Tests for get_available_genres method."""
    
    def test_returns_list_of_genres(self):
        """Should return a list of genre dictionaries."""
        service = DeezerService()
        genres = service.get_available_genres()
        
        assert isinstance(genres, list)
        assert len(genres) == len(GENRES)
    
    def test_genre_format(self):
        """Each genre should have id and name keys."""
        service = DeezerService()
        genres = service.get_available_genres()
        
        for genre in genres:
            assert "id" in genre
            assert "name" in genre
    
    def test_genres_match_constants(self):
        """Returned genres should match the GENRES constant."""
        service = DeezerService()
        genres = service.get_available_genres()
        
        genre_dict = {g["id"]: g["name"] for g in genres}
        assert genre_dict == GENRES


@pytest.mark.asyncio
class TestDeezerServiceAsync:
    """Async tests for DeezerService methods."""
    
    async def test_get_genre_artists_returns_list(self):
        """get_genre_artists should return a list."""
        service = DeezerService()
        try:
            artists = await service.get_genre_artists(152)  # Rock
            assert isinstance(artists, list)
        finally:
            await service.close()
    
    async def test_search_albums_returns_list(self):
        """search_albums should return a list."""
        service = DeezerService()
        try:
            albums = await service.search_albums("rock")
            assert isinstance(albums, list)
        finally:
            await service.close()
    
    async def test_get_discovery_albums_returns_albums(self):
        """get_discovery_albums should return album dictionaries."""
        service = DeezerService()
        try:
            albums = await service.get_discovery_albums(count=3)
            assert isinstance(albums, list)
            # Should return up to requested count
            assert len(albums) <= 3
        finally:
            await service.close()
    
    async def test_get_discovery_albums_with_genre_filter(self):
        """get_discovery_albums should accept genre_ids parameter."""
        service = DeezerService()
        try:
            albums = await service.get_discovery_albums(count=3, genre_ids=[129])  # Jazz
            assert isinstance(albums, list)
        finally:
            await service.close()
    
    async def test_enriched_album_has_required_fields(self):
        """Enriched albums should have all required fields."""
        service = DeezerService()
        try:
            albums = await service.get_discovery_albums(count=1)
            if albums:
                album = albums[0]
                required_fields = [
                    "id", "title", "artist", "cover_url", "preview_url",
                    "deezer_id", "deezer_link"
                ]
                for field in required_fields:
                    assert field in album, f"Missing field: {field}"
        finally:
            await service.close()
    
    async def test_service_close(self):
        """Service should be closeable without error."""
        service = DeezerService()
        await service.close()
        # Should not raise an exception


class TestCaching:
    """Tests for caching behavior."""
    
    def test_cache_set_and_get(self):
        """Cache should store and retrieve values."""
        service = DeezerService()
        
        # Set a value
        service._set_cache("test_key", {"data": "test"})
        
        # Get the value
        result = service._get_cache("test_key")
        assert result == {"data": "test"}
    
    def test_cache_miss_returns_none(self):
        """Cache miss should return None."""
        service = DeezerService()
        result = service._get_cache("nonexistent_key")
        assert result is None
