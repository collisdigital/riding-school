import { render, screen, waitFor } from '@testing-library/react'
import { expect, test, vi, afterEach } from 'vitest'
import App from './App'

// Mock fetch globally
const mockFetch = vi.fn()
global.fetch = mockFetch

afterEach(() => {
  vi.restoreAllMocks()
})

test('renders riding school tracker title', async () => {
  mockFetch.mockResolvedValue({
    json: () => Promise.resolve({ message: 'Hello World' }),
  })

  render(<App />)
  const titleElement = screen.getByText(/Riding School Tracker/i)
  expect(titleElement).toBeInTheDocument()

  // Wait for the async update to complete
  await waitFor(() => expect(screen.getByText('Hello World')).toBeInTheDocument())
})

test('shows loading message initially', async () => {
  // Use a promise that resolves but we check initial state first
  let resolveFetch: (value: any) => void = () => {}
  mockFetch.mockReturnValue(new Promise((resolve) => {
      resolveFetch = resolve
  }))

  render(<App />)
  const loadingElement = screen.getByText(/Loading.../i)
  expect(loadingElement).toBeInTheDocument()

  // Clean up by resolving the promise so the test can finish cleanly
  resolveFetch({
      json: () => Promise.resolve({ message: 'Done' })
  })

  await waitFor(() => expect(screen.getByText('Done')).toBeInTheDocument())
})
