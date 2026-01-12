/**
 * Tests for TypeScript type definitions.
 * These tests verify that our types are correctly structured.
 */
import { describe, it, expect } from 'vitest'
import type { Album, AlbumCollection, Genre } from './types'

describe('Type Definitions', () => {
  describe('Album type', () => {
    it('should accept a valid album object', () => {
      const album: Album = {
        id: 1,
        title: 'Test Album',
        artist: 'Test Artist',
        cover_url: 'https://example.com/cover.jpg',
        preview_url: 'https://example.com/preview.mp3',
        year: '2024',
        genre: 'Rock',
        deezer_id: 12345,
        deezer_link: 'https://deezer.com/album/12345',
        nb_tracks: 12,
      }

      expect(album.id).toBe(1)
      expect(album.title).toBe('Test Album')
      expect(album.artist).toBe('Test Artist')
      expect(album.cover_url).toBe('https://example.com/cover.jpg')
      expect(album.preview_url).toBe('https://example.com/preview.mp3')
    })

    it('should accept null for optional fields', () => {
      const album: Album = {
        id: 1,
        title: 'Test Album',
        artist: 'Test Artist',
        cover_url: 'https://example.com/cover.jpg',
        preview_url: 'https://example.com/preview.mp3',
        year: null,
        genre: null,
        deezer_id: 12345,
        deezer_link: null,
        nb_tracks: null,
      }

      expect(album.year).toBeNull()
      expect(album.genre).toBeNull()
      expect(album.deezer_link).toBeNull()
      expect(album.nb_tracks).toBeNull()
    })
  })

  describe('AlbumCollection type', () => {
    it('should accept a valid album collection', () => {
      const collection: AlbumCollection = {
        albums: [
          {
            id: 1,
            title: 'Test Album',
            artist: 'Test Artist',
            cover_url: 'https://example.com/cover.jpg',
            preview_url: 'https://example.com/preview.mp3',
            year: '2024',
            genre: 'Rock',
            deezer_id: 12345,
            deezer_link: 'https://deezer.com/album/12345',
            nb_tracks: 12,
          },
        ],
        total: 1,
      }

      expect(collection.albums).toHaveLength(1)
      expect(collection.total).toBe(1)
    })

    it('should accept empty albums array', () => {
      const collection: AlbumCollection = {
        albums: [],
        total: 0,
      }

      expect(collection.albums).toHaveLength(0)
      expect(collection.total).toBe(0)
    })
  })

  describe('Genre type', () => {
    it('should accept a valid genre object', () => {
      const genre: Genre = {
        id: 152,
        name: 'Rock',
      }

      expect(genre.id).toBe(152)
      expect(genre.name).toBe('Rock')
    })
  })
})
