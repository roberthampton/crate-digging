export interface Album {
  id: number;
  title: string;
  artist: string;
  cover_url: string;
  preview_url: string;
  year: string | null;
  genre: string | null; // Deprecated - use genres instead
  genres: string[] | null; // All genres for the album
  deezer_id: number;
  deezer_link: string | null;
  nb_tracks: number | null;
}

export interface AlbumCollection {
  albums: Album[];
  total: number;
}

export interface Genre {
  id: number;
  name: string;
}
