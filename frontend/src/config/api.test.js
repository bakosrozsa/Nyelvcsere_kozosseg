import { describe, expect, it } from 'vitest'

import { API_BASE_URL } from './api'

describe('API config', () => {
  it('exposes a non-empty API base URL', () => {
    expect(typeof API_BASE_URL).toBe('string')
    expect(API_BASE_URL.length).toBeGreaterThan(0)
  })
})
