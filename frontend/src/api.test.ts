/**
 * Tests for API client functions.
 * These tests verify the API module correctly constructs requests and handles responses.
 */
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { fetchGenres, fetchRandomAlbums } from './api'

// Mock fetch globally
const mockFetch = vi.fn()
global.fetch = mockFetch

describe('API Client', () => {
  beforeEach(() => {
    mockFetch.mockReset()
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  describe('fetchGenres', () => {
    it('should fetch genres from the correct endpoint', async () => {
      const mockGenres = [
        { id: 132, name: 'Pop' },
        { id: 152, name: 'Rock' },
      ]
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockGenres),
      })

      await fetchGenres()

      expect(mockFetch).toHaveBeenCalledWith('http://localhost:8000/genres')
    })

    it('should return genres array on success', async () => {
      const mockGenres = [
        { id: 132, name: 'Pop' },
        { id: 152, name: 'Rock' },
      ]
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockGenres),
      })

      const result = await fetchGenres()

      expect(result).toEqual(mockGenres)
    })

    it('should throw error on failed response', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 500,
      })

      await expect(fetchGenres()).rejects.toThrow('Failed to fetch genres')
    })
  })

  describe('fetchRandomAlbums', () => {
    const mockAlbumCollection = {
      albums: [
        {
          id: 1,
          title: 'Test Album',
          artist: 'Test Artist',
          cover_url: 'https://example.com/cover.jpg',
          preview_url: 'https://example.com/preview.mp3',
          year: '2024',
          genre: 'Rock',
          deezer_id: 1,
          deezer_link: 'https://deezer.com/album/1',
          nb_tracks: 10,
        },
      ],
      total: 1,
    }

    it('should fetch albums with default count', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockAlbumCollection),
      })

      await fetchRandomAlbums()

      expect(mockFetch).toHaveBeenCalledWith(
        'http://localhost:8000/albums/random?count=10'
      )
    })

    it('should fetch albums with custom count', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockAlbumCollection),
      })

      await fetchRandomAlbums(5)

      expect(mockFetch).toHaveBeenCalledWith(
        'http://localhost:8000/albums/random?count=5'
      )
    })

    it('should include genre IDs in request when provided', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockAlbumCollection),
      })

      await fetchRandomAlbums(10, [129, 152])

      expect(mockFetch).toHaveBeenCalledWith(
        'http://localhost:8000/albums/random?count=10&genres=129,152'
      )
    })

    it('should not include genres param when array is empty', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockAlbumCollection),
      })

      await fetchRandomAlbums(10, [])

      expect(mockFetch).toHaveBeenCalledWith(
        'http://localhost:8000/albums/random?count=10'
      )
    })

    it('should return album collection on success', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockAlbumCollection),
      })

      const result = await fetchRandomAlbums()

      expect(result).toEqual(mockAlbumCollection)
      expect(result.albums).toHaveLength(1)
      expect(result.total).toBe(1)
    })

    it('should throw error on failed response', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 500,
      })

      await expect(fetchRandomAlbums()).rejects.toThrow('Failed to fetch albums')
    })
  })
})
