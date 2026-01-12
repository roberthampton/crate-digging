"""
API endpoint tests for Crate Digging backend.
Tests the FastAPI endpoints to ensure they return correct responses.
"""
import pytest
from fastapi.testclient import TestClient
from main import app


client = TestClient(app)


class TestRootEndpoint:
    """Tests for the root endpoint."""
    
    def test_root_returns_welcome_message(self):
        """Root endpoint should return a welcome message with version info."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
        assert "data_source" in data
        assert data["data_source"] == "Deezer"


class TestGenresEndpoint:
    """Tests for the /genres endpoint."""
    
    def test_genres_returns_list(self):
        """Genres endpoint should return a list of genres."""
        response = client.get("/genres")
        assert response.status_code == 200
        genres = response.json()
        assert isinstance(genres, list)
        assert len(genres) > 0
    
    def test_genres_have_required_fields(self):
        """Each genre should have id and name fields."""
        response = client.get("/genres")
        genres = response.json()
        for genre in genres:
            assert "id" in genre
            assert "name" in genre
            assert isinstance(genre["id"], int)
            assert isinstance(genre["name"], str)
    
    def test_genres_contains_expected_genres(self):
        """Genres list should contain common music genres."""
        response = client.get("/genres")
        genres = response.json()
        genre_names = [g["name"] for g in genres]
        
        expected_genres = ["Rock", "Jazz", "Pop", "Hip-Hop", "Electronic"]
        for expected in expected_genres:
            assert expected in genre_names, f"Expected genre '{expected}' not found"


class TestRandomAlbumsEndpoint:
    """Tests for the /albums/random endpoint."""
    
    def test_random_albums_returns_albums(self):
        """Random albums endpoint should return album data."""
        response = client.get("/albums/random?count=5")
        assert response.status_code == 200
        data = response.json()
        assert "albums" in data
        assert "total" in data
    
    def test_random_albums_default_count(self):
        """Default count should be 10 albums."""
        response = client.get("/albums/random")
        assert response.status_code == 200
        data = response.json()
        # Should return up to 10 albums (may be less if API has issues)
        assert data["total"] <= 10
    
    def test_random_albums_respects_count_parameter(self):
        """Count parameter should limit the number of albums returned."""
        response = client.get("/albums/random?count=3")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] <= 3
    
    def test_random_albums_count_validation(self):
        """Count parameter should be validated (1-30)."""
        # Too high
        response = client.get("/albums/random?count=100")
        assert response.status_code == 422  # Validation error
        
        # Too low
        response = client.get("/albums/random?count=0")
        assert response.status_code == 422
    
    def test_random_albums_have_required_fields(self):
        """Each album should have all required fields."""
        response = client.get("/albums/random?count=3")
        data = response.json()
        
        required_fields = [
            "id", "title", "artist", "cover_url", "preview_url",
            "deezer_id", "deezer_link"
        ]
        
        for album in data["albums"]:
            for field in required_fields:
                assert field in album, f"Missing field: {field}"
    
    def test_random_albums_have_preview_urls(self):
        """All returned albums should have valid preview URLs."""
        response = client.get("/albums/random?count=5")
        data = response.json()
        
        for album in data["albums"]:
            assert album["preview_url"], "Preview URL should not be empty"
            assert album["preview_url"].startswith("http"), "Preview URL should be a valid URL"
    
    def test_random_albums_with_genre_filter(self):
        """Genre filter should be accepted as a parameter."""
        # Test with single genre (Jazz = 129)
        response = client.get("/albums/random?count=5&genres=129")
        assert response.status_code == 200
        data = response.json()
        assert "albums" in data
    
    def test_random_albums_with_multiple_genres(self):
        """Multiple genres can be specified as comma-separated values."""
        # Rock (152) and Metal (464)
        response = client.get("/albums/random?count=5&genres=152,464")
        assert response.status_code == 200
        data = response.json()
        assert "albums" in data


class TestAlbumCollectionSchema:
    """Tests for the album collection response schema."""
    
    def test_album_collection_structure(self):
        """Album collection should have albums array and total count."""
        response = client.get("/albums/random?count=3")
        data = response.json()
        
        assert isinstance(data["albums"], list)
        assert isinstance(data["total"], int)
        assert data["total"] == len(data["albums"])


class TestAlbumSchema:
    """Tests for individual album schema."""
    
    def test_album_optional_fields(self):
        """Albums may have optional fields that can be null."""
        response = client.get("/albums/random?count=5")
        data = response.json()
        
        optional_fields = ["year", "genre", "nb_tracks"]
        
        for album in data["albums"]:
            for field in optional_fields:
                # Field should exist but can be None
                assert field in album
    
    def test_album_deezer_link_format(self):
        """Deezer link should be a valid Deezer URL."""
        response = client.get("/albums/random?count=3")
        data = response.json()
        
        for album in data["albums"]:
            if album["deezer_link"]:
                assert "deezer.com" in album["deezer_link"]
    
    def test_album_cover_url_format(self):
        """Cover URL should be a valid image URL."""
        response = client.get("/albums/random?count=3")
        data = response.json()
        
        for album in data["albums"]:
            assert album["cover_url"].startswith("http")
            assert "dzcdn.net" in album["cover_url"] or "deezer.com" in album["cover_url"]
