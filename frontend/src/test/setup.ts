/**
 * Test setup file for Vitest.
 *
 * This file runs before each test file and sets up
 * the testing environment and utilities.
 */

// Import Vitest globals
import { vi, beforeEach, afterEach } from 'vitest'

// Import React Testing Library
import '@testing-library/jest-dom/vitest'

// Mock window.matchMedia for CSS media queries
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: (query: string) => {
    return {
      matches: false,
      media: query,
      onchange: null,
      addListener: () => {},
      removeListener: () => {},
      addEventListener: () => {},
      removeEventListener: () => {},
      dispatchEvent: () => false,
    }
  },
})

// Mock IntersectionObserver for scroll detection
Object.defineProperty(window, 'IntersectionObserver', {
  writable: true,
  value: class IntersectionObserver {
    root: Element | null
    rootMargin: string
    thresholds: number[]
    constructor(callback: Function) {
      this.root = null
      this.rootMargin = ''
      this.thresholds = [0]
    }
    observe() {}
    unobserve() {}
    disconnect() {}
  },
})

// Mock ResizeObserver for size detection
Object.defineProperty(window, 'ResizeObserver', {
  writable: true,
  value: class ResizeObserver {
    constructor(callback: Function) {}
    observe() {}
    unobserve() {}
    disconnect() {}
  },
})

// Mock localStorage
const localStorageMock = {
  getItem: vi.fn(),
  setItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn(),
}
global.localStorage = localStorageMock

// Mock console methods to reduce noise in tests
const originalConsole = { ...console }
beforeEach(() => {
  console.log = vi.fn()
  console.error = vi.fn()
  console.warn = vi.fn()
  console.info = vi.fn()
})

afterEach(() => {
  console.log = originalConsole.log
  console.error = originalConsole.error
  console.warn = originalConsole.warn
  console.info = originalConsole.info
  vi.clearAllMocks()
})

// Cleanup after each test (React Testing Library)
import { cleanup } from '@testing-library/react'
afterEach(() => {
  cleanup()
})
