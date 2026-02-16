import { render, screen, waitFor } from '@testing-library/react'
import { expect, test, describe, vi, beforeEach } from 'vitest'
import DashboardPage from './DashboardPage'
import { BrowserRouter } from 'react-router-dom'
import axios from 'axios'

vi.mock('axios')
const mockedAxios = axios as unknown as {
  get: ReturnType<typeof vi.fn>
  post: ReturnType<typeof vi.fn>
}

describe('DashboardPage', () => {
  beforeEach(() => {
    mockedAxios.get.mockImplementation((url: string) => {
      if (url === '/api/riders/') return Promise.resolve({ data: [] })
      return Promise.reject(new Error('not found'))
    })
    mockedAxios.post.mockResolvedValue({ data: {} })
  })

  test('renders add rider form with accessible labels', async () => {
    render(
      <BrowserRouter>
        <DashboardPage />
      </BrowserRouter>,
    )

    // Wait for initial load
    await waitFor(() => expect(screen.getByText('Total Riders')).toBeInTheDocument())

    // Check for accessible labels
    expect(screen.getByLabelText(/Rider First Name/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/Rider Last Name/i)).toBeInTheDocument()
  })
})
