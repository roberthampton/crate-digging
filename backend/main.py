import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

from deezer_service import deezer_service


class Album(BaseModel):
    id: int
    title: str
    artist: str
    cover_url: str
    preview_url: str
    year: Optional[str] = None
    genre: Optional[str] = None
    deezer_id: int
    deezer_link: Optional[str] = None
    nb_tracks: Optional[int] = None


class AlbumCollection(BaseModel):
    albums: list[Album]
    total: int


class Genre(BaseModel):
    id: int
    name: str


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    yield
    # Shutdown
    await deezer_service.close()


app = FastAPI(
    title="Crate Digging API",
    description="API for virtual crate digging music discovery powered by Deezer",
    version="2.0.0",
    lifespan=lifespan
)

# CORS origins - allow localhost for dev and any Vercel preview/production URLs
cors_origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

# Add frontend URL from environment if set
frontend_url = os.environ.get("FRONTEND_URL")
if frontend_url:
    cors_origins.append(frontend_url)

# Allow all Vercel preview deployments
cors_origins.append("https://*.vercel.app")

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {
        "message": "Welcome to Crate Digging API",
        "version": "2.0.0",
        "data_source": "Deezer"
    }


@app.get("/genres", response_model=list[Genre])
def get_genres():
    """Get available genres for filtering."""
    return deezer_service.get_available_genres()


@app.get("/albums/random", response_model=AlbumCollection)
async def get_random_albums(
    count: int = Query(default=10, ge=1, le=30),
    genres: Optional[str] = Query(default=None, description="Comma-separated genre IDs to filter by")
):
    """Get a random selection of albums for crate digging from Deezer."""
    genre_ids = None
    if genres:
        try:
            genre_ids = [int(g.strip()) for g in genres.split(",") if g.strip()]
        except ValueError:
            pass
    
    albums = await deezer_service.get_discovery_albums(count=count, genre_ids=genre_ids)
    
    return AlbumCollection(
        albums=[Album(**album) for album in albums],
        total=len(albums)
    )


@app.get("/albums/chart", response_model=AlbumCollection)
async def get_chart_albums(
    count: int = Query(default=20, ge=1, le=50)
):
    """Get current chart albums from Deezer."""
    raw_albums = await deezer_service.get_chart_albums(limit=count)
    
    # Enrich with previews
    enriched = []
    for album in raw_albums[:count]:
        enriched_album = await deezer_service.enrich_album_with_preview(album)
        if enriched_album.get("preview_url"):
            enriched.append(enriched_album)
    
    return AlbumCollection(
        albums=[Album(**album) for album in enriched],
        total=len(enriched)
    )


@app.get("/albums/search", response_model=AlbumCollection)
async def search_albums(
    q: str = Query(..., min_length=1, description="Search query"),
    count: int = Query(default=20, ge=1, le=50)
):
    """Search for albums on Deezer."""
    raw_albums = await deezer_service.search_albums(query=q, limit=count)
    
    # Enrich with previews
    enriched = []
    for album in raw_albums[:count]:
        enriched_album = await deezer_service.enrich_album_with_preview(album)
        if enriched_album.get("preview_url"):
            enriched.append(enriched_album)
    
    return AlbumCollection(
        albums=[Album(**album) for album in enriched],
        total=len(enriched)
    )


@app.get("/albums/{album_id}")
async def get_album(album_id: int):
    """Get a specific album by Deezer ID."""
    album = await deezer_service.get_album_details(album_id)
    if album is None:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Album not found")
    
    enriched = await deezer_service.enrich_album_with_preview(album)
    return Album(**enriched)
