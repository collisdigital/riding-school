import { render, screen, waitFor } from '@testing-library/react'
import { expect, test, describe, vi, beforeEach } from 'vitest'
import DashboardPage from './DashboardPage'
import { BrowserRouter } from 'react-router-dom'
import axios from 'axios'

vi.mock('axios')
const mockedAxios = axios as unknown as { get: ReturnType<typeof vi.fn>, post: ReturnType<typeof vi.fn> }

describe('DashboardPage', () => {
  beforeEach(() => {
    mockedAxios.get.mockImplementation((url: string) => {
        if (url === '/api/auth/me') return Promise.resolve({ data: { school: { name: 'Test School' } } })
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

    // Wait for data to load
    await waitFor(() => expect(screen.getByText('Test School')).toBeInTheDocument())

    // Check for accessible labels - this should fail initially
    expect(screen.getByLabelText(/Rider First Name/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/Rider Last Name/i)).toBeInTheDocument()
  })
})
