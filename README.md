# Crate Digging 📦🎵

A virtual crate digging experience for music discovery. Browse through a collection of albums, preview real tracks as you flip through, and discover your next favorite music.

## Features

- **Real Music Data**: Powered by the Deezer API with real album artwork and metadata
- **30-Second Previews**: Play actual track previews from each album
- **Random Discovery**: Each page load presents a fresh, randomized collection from various genres
- **Swipe Navigation**: Drag albums or use arrow keys to browse through the crate
- **Vinyl Animation**: Watch the vinyl slide out and spin when playing
- **Direct Links**: Open albums on Deezer to listen to the full tracks

## Tech Stack

- **Frontend**: Vue 3 with TypeScript, Vite
- **Backend**: FastAPI with Python
- **Data Source**: Deezer Public API (no authentication required)

## Getting Started

### Prerequisites

- Python 3.10+
- Node.js 20+
- npm

### Backend Setup

```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

The API will be available at http://localhost:8000

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

The app will be available at http://localhost:5173

## API Endpoints

- `GET /` - Health check and API info
- `GET /albums/random?count=20` - Get random albums for crate digging
- `GET /albums/chart?count=20` - Get current chart albums
- `GET /albums/search?q=query&count=20` - Search for albums
- `GET /albums/{id}` - Get a specific album by Deezer ID

## Controls

- **Click** album cover: Play/pause 30-second preview
- **Arrow keys**: Navigate between albums
- **Space**: Toggle play/pause
- **Drag**: Swipe through albums
- **Shuffle button**: Load new random selection
- **Listen on Deezer**: Open full album on Deezer

## Data Sources

Albums are sourced from:
- Deezer chart albums
- Random artists from various genres (Pop, Rock, Hip-Hop, Jazz, Electronic, R&B, Alternative, Metal, Folk, Soul, Classical, World, Indie, and more)

Preview tracks are 30-second MP3 clips provided directly by Deezer's API.

## Project Structure

```
crate-digging/
├── backend/
│   ├── main.py           # FastAPI application
│   ├── deezer_service.py # Deezer API integration with caching
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   └── AlbumCrate.vue  # Main crate digging component
│   │   ├── App.vue
│   │   ├── api.ts        # API client
│   │   ├── types.ts      # TypeScript types
│   │   └── style.css     # Global styles
│   └── package.json
└── README.md
```

## Caching

The backend implements in-memory caching with a 1-hour TTL to:
- Reduce API calls to Deezer
- Improve response times
- Avoid rate limiting

## Attribution

Music data and previews provided by [Deezer](https://www.deezer.com).
