import type { AlbumCollection, Genre } from './types';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export async function fetchGenres(): Promise<Genre[]> {
  const response = await fetch(`${API_BASE}/genres`);
  if (!response.ok) {
    throw new Error('Failed to fetch genres');
  }
  return response.json();
}

export async function fetchRandomAlbums(
  count: number = 10, 
  genreIds?: number[],
  minTracks?: number
): Promise<AlbumCollection> {
  let url = `${API_BASE}/albums/random?count=${count}`;
  if (genreIds && genreIds.length > 0) {
    url += `&genres=${genreIds.join(',')}`;
  }
  if (minTracks !== undefined && minTracks > 0) {
    url += `&min_tracks=${minTracks}`;
  }
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error('Failed to fetch albums');
  }
  return response.json();
}
