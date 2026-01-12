/**
 * Tests for AlbumCrate component.
 * These tests verify the component renders correctly and handles user interactions.
 */
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import AlbumCrate from './AlbumCrate.vue'
import * as api from '../api'

// Mock the API module
vi.mock('../api', () => ({
  fetchGenres: vi.fn(),
  fetchRandomAlbums: vi.fn(),
}))

const mockGenres = [
  { id: 132, name: 'Pop' },
  { id: 152, name: 'Rock' },
  { id: 129, name: 'Jazz' },
]

const mockAlbums = {
  albums: [
    {
      id: 1,
      title: 'Test Album 1',
      artist: 'Artist 1',
      cover_url: 'https://example.com/cover1.jpg',
      preview_url: 'https://example.com/preview1.mp3',
      year: '2024',
      genre: 'Rock',
      deezer_id: 1,
      deezer_link: 'https://deezer.com/album/1',
      nb_tracks: 10,
    },
    {
      id: 2,
      title: 'Test Album 2',
      artist: 'Artist 2',
      cover_url: 'https://example.com/cover2.jpg',
      preview_url: 'https://example.com/preview2.mp3',
      year: '2023',
      genre: 'Jazz',
      deezer_id: 2,
      deezer_link: 'https://deezer.com/album/2',
      nb_tracks: 8,
    },
  ],
  total: 2,
}

describe('AlbumCrate Component', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    vi.mocked(api.fetchGenres).mockResolvedValue(mockGenres)
    vi.mocked(api.fetchRandomAlbums).mockResolvedValue(mockAlbums)
  })

  describe('Initial Loading', () => {
    it('should show loading state initially', () => {
      vi.mocked(api.fetchRandomAlbums).mockImplementation(
        () => new Promise(() => {}) // Never resolves
      )

      const wrapper = mount(AlbumCrate)

      expect(wrapper.find('.loading').exists()).toBe(true)
      expect(wrapper.text()).toContain('Digging through the crates')
    })

    it('should fetch albums on mount', async () => {
      mount(AlbumCrate)
      await flushPromises()

      expect(api.fetchRandomAlbums).toHaveBeenCalledWith(10, undefined)
    })

    it('should fetch genres on mount', async () => {
      mount(AlbumCrate)
      await flushPromises()

      expect(api.fetchGenres).toHaveBeenCalled()
    })
  })

  describe('Album Display', () => {
    it('should display album title after loading', async () => {
      const wrapper = mount(AlbumCrate)
      await flushPromises()

      expect(wrapper.find('.album-title').text()).toBe('Test Album 1')
    })

    it('should display artist name', async () => {
      const wrapper = mount(AlbumCrate)
      await flushPromises()

      expect(wrapper.find('.album-artist').text()).toBe('Artist 1')
    })

    it('should display album year when available', async () => {
      const wrapper = mount(AlbumCrate)
      await flushPromises()

      expect(wrapper.find('.album-year').text()).toBe('2024')
    })

    it('should display album genre when available', async () => {
      const wrapper = mount(AlbumCrate)
      await flushPromises()

      expect(wrapper.find('.album-genre').text()).toBe('Rock')
    })

    it('should display progress indicator', async () => {
      const wrapper = mount(AlbumCrate)
      await flushPromises()

      expect(wrapper.find('.progress-indicator').text()).toBe('1 / 2')
    })
  })

  describe('Navigation', () => {
    it('should have prev button disabled on first album', async () => {
      const wrapper = mount(AlbumCrate)
      await flushPromises()

      const prevBtn = wrapper.find('.prev-btn')
      expect(prevBtn.attributes('disabled')).toBeDefined()
    })

    it('should have next button enabled when more albums exist', async () => {
      const wrapper = mount(AlbumCrate)
      await flushPromises()

      const nextBtn = wrapper.find('.next-btn')
      expect(nextBtn.attributes('disabled')).toBeUndefined()
    })

    it('should navigate to next album when next button clicked', async () => {
      const wrapper = mount(AlbumCrate)
      await flushPromises()

      await wrapper.find('.next-btn').trigger('click')

      expect(wrapper.find('.album-title').text()).toBe('Test Album 2')
      expect(wrapper.find('.progress-indicator').text()).toBe('2 / 2')
    })

    it('should disable next button on last album', async () => {
      const wrapper = mount(AlbumCrate)
      await flushPromises()

      await wrapper.find('.next-btn').trigger('click')

      const nextBtn = wrapper.find('.next-btn')
      expect(nextBtn.attributes('disabled')).toBeDefined()
    })

    it('should enable prev button after navigating forward', async () => {
      const wrapper = mount(AlbumCrate)
      await flushPromises()

      await wrapper.find('.next-btn').trigger('click')

      const prevBtn = wrapper.find('.prev-btn')
      expect(prevBtn.attributes('disabled')).toBeUndefined()
    })
  })

  describe('Shuffle Button', () => {
    it('should have a shuffle button', async () => {
      const wrapper = mount(AlbumCrate)
      await flushPromises()

      expect(wrapper.find('.shuffle-btn').exists()).toBe(true)
      expect(wrapper.find('.shuffle-btn').text()).toContain('Shuffle')
    })

    it('should fetch new albums when shuffle clicked', async () => {
      const wrapper = mount(AlbumCrate)
      await flushPromises()

      vi.mocked(api.fetchRandomAlbums).mockClear()
      await wrapper.find('.shuffle-btn').trigger('click')
      await flushPromises()

      expect(api.fetchRandomAlbums).toHaveBeenCalled()
    })
  })

  describe('Genre Filter', () => {
    it('should have a filter button', async () => {
      const wrapper = mount(AlbumCrate)
      await flushPromises()

      expect(wrapper.find('.filter-btn').exists()).toBe(true)
    })

    it('should show genre filter panel when filter button clicked', async () => {
      const wrapper = mount(AlbumCrate)
      await flushPromises()

      await wrapper.find('.filter-btn').trigger('click')

      expect(wrapper.find('.genre-filter').exists()).toBe(true)
    })

    it('should display all genres in filter panel', async () => {
      const wrapper = mount(AlbumCrate)
      await flushPromises()

      await wrapper.find('.filter-btn').trigger('click')

      const genreChips = wrapper.findAll('.genre-chip')
      expect(genreChips).toHaveLength(3) // Pop, Rock, Jazz
    })

    it('should toggle genre selection when chip clicked', async () => {
      const wrapper = mount(AlbumCrate)
      await flushPromises()

      await wrapper.find('.filter-btn').trigger('click')
      const firstChip = wrapper.find('.genre-chip')
      await firstChip.trigger('click')

      expect(firstChip.classes()).toContain('selected')
    })

    it('should have apply filter button in filter panel', async () => {
      const wrapper = mount(AlbumCrate)
      await flushPromises()

      await wrapper.find('.filter-btn').trigger('click')

      expect(wrapper.find('.apply-filter-btn').exists()).toBe(true)
    })
  })

  describe('Deezer Link', () => {
    it('should have a link to Deezer', async () => {
      const wrapper = mount(AlbumCrate)
      await flushPromises()

      const deezerLink = wrapper.find('.deezer-link')
      expect(deezerLink.exists()).toBe(true)
      expect(deezerLink.attributes('href')).toBe('https://deezer.com/album/1')
    })

    it('should open Deezer link in new tab', async () => {
      const wrapper = mount(AlbumCrate)
      await flushPromises()

      const deezerLink = wrapper.find('.deezer-link')
      expect(deezerLink.attributes('target')).toBe('_blank')
      expect(deezerLink.attributes('rel')).toContain('noopener')
    })
  })

  describe('Error Handling', () => {
    it('should show error message when API fails', async () => {
      vi.mocked(api.fetchRandomAlbums).mockRejectedValue(new Error('API Error'))

      const wrapper = mount(AlbumCrate)
      await flushPromises()

      expect(wrapper.find('.error').exists()).toBe(true)
      expect(wrapper.text()).toContain('Failed to load albums')
    })

    it('should have retry button on error', async () => {
      vi.mocked(api.fetchRandomAlbums).mockRejectedValue(new Error('API Error'))

      const wrapper = mount(AlbumCrate)
      await flushPromises()

      expect(wrapper.find('.retry-btn').exists()).toBe(true)
    })
  })

  describe('Audio Controls', () => {
    it('should have an audio element', async () => {
      const wrapper = mount(AlbumCrate)
      await flushPromises()

      expect(wrapper.find('audio').exists()).toBe(true)
    })

    it('should have play indicator on album card', async () => {
      const wrapper = mount(AlbumCrate)
      await flushPromises()

      expect(wrapper.find('.play-indicator').exists()).toBe(true)
    })
  })
})
