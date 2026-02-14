import { render, screen, waitFor, fireEvent } from '@testing-library/react'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import RidersPage from '../pages/RidersPage'
import { BrowserRouter } from 'react-router-dom'
import axios from 'axios'

// Mock Axios
vi.mock('axios')

// Mock window.confirm
const confirmSpy = vi.spyOn(window, 'confirm')

describe('RidersPage', () => {
  const mockRiders = [
    {
      id: 'rider-1',
      user_id: 'user-1',
      first_name: 'John',
      last_name: 'Doe',
      email: 'john@example.com',
      height_cm: 180,
      weight_kg: 75,
      date_of_birth: '1990-01-01',
      school_id: 'school-1',
    },
    {
      id: 'rider-2',
      user_id: 'user-2',
      first_name: 'Jane',
      last_name: 'Smith',
      email: null,
      height_cm: 165,
      weight_kg: 60,
      date_of_birth: '2010-05-05',
      school_id: 'school-1',
    },
  ]

  beforeEach(() => {
    vi.clearAllMocks()
    vi.mocked(axios.get).mockResolvedValue({ data: mockRiders })
    confirmSpy.mockReturnValue(true)
  })

  it('renders riders list correctly', async () => {
    render(
      <BrowserRouter>
        <RidersPage />
      </BrowserRouter>,
    )

    await waitFor(() => {
      expect(screen.getByText('John Doe')).toBeDefined()
      expect(screen.getByText('Jane Smith')).toBeDefined()
    })

    expect(screen.getByText('john@example.com')).toBeDefined()
  })

  it('opens add rider modal', async () => {
    render(
      <BrowserRouter>
        <RidersPage />
      </BrowserRouter>,
    )

    await waitFor(() => expect(screen.getByText('Add Rider')).toBeDefined())

    fireEvent.click(screen.getByText('Add Rider'))

    expect(screen.getByText('Add New Rider')).toBeDefined()
  })

  it('opens edit rider modal', async () => {
    render(
      <BrowserRouter>
        <RidersPage />
      </BrowserRouter>,
    )

    await waitFor(() => expect(screen.getByText('John Doe')).toBeDefined())

    // Find edit button (using title attribute from lucide icon wrapper button)
    const editBtns = screen.getAllByTitle('Edit')
    fireEvent.click(editBtns[0])

    expect(screen.getByText('Edit Rider')).toBeDefined()
    // Should populate values
    expect(screen.getByDisplayValue('John') as HTMLInputElement).toBeDefined()
  })

  it('deletes a rider', async () => {
    vi.mocked(axios.delete).mockResolvedValue({ data: {} })

    render(
      <BrowserRouter>
        <RidersPage />
      </BrowserRouter>,
    )

    await waitFor(() => expect(screen.getByText('John Doe')).toBeDefined())

    const deleteBtns = screen.getAllByTitle('Delete')
    fireEvent.click(deleteBtns[0])

    expect(confirmSpy).toHaveBeenCalled()
    expect(axios.delete).toHaveBeenCalledWith('/api/riders/rider-1')
  })
})
