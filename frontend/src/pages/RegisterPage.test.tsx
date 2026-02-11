import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { expect, test, vi, beforeEach, type Mocked } from 'vitest'
import { BrowserRouter } from 'react-router-dom'
import RegisterPage from './RegisterPage'
import axios from 'axios'

vi.mock('axios')
const mockedAxios = axios as Mocked<typeof axios>

// Helper to check if an element is axios error mock compatible
mockedAxios.isAxiosError.mockImplementation((payload: any) => {
  return payload && payload.isAxiosError === true
})

const renderRegisterPage = () => {
  return render(
    <BrowserRouter>
      <RegisterPage />
    </BrowserRouter>,
  )
}

beforeEach(() => {
  vi.clearAllMocks()
})

test('renders registration form and password requirements', () => {
  renderRegisterPage()
  expect(screen.getByText(/Create your account/i)).toBeInTheDocument()
  expect(screen.getByText(/At least 8 characters/i)).toBeInTheDocument()
  expect(screen.getByText(/At least one uppercase letter/i)).toBeInTheDocument()
  expect(screen.getByText(/At least one digit/i)).toBeInTheDocument()
  expect(screen.getByText(/At least one special character/i)).toBeInTheDocument()
})

test('updates password requirement indicators as user types', async () => {
  renderRegisterPage()

  const passwordInput = screen.getByLabelText(/Password/i)

  // Initially all should be in gray/inactive state
  expect(screen.getByText(/At least 8 characters/i)).toHaveClass('text-gray-500')

  fireEvent.change(passwordInput, { target: { value: 'Short1!' } })
  expect(screen.getByText(/At least 8 characters/i)).toHaveClass('text-gray-500')
  expect(screen.getByText(/At least one uppercase letter/i)).toHaveClass('text-green-600')
  expect(screen.getByText(/At least one digit/i)).toHaveClass('text-green-600')
  expect(screen.getByText(/At least one special character/i)).toHaveClass('text-green-600')

  fireEvent.change(passwordInput, { target: { value: 'LongEnough1!' } })
  expect(screen.getByText(/At least 8 characters/i)).toHaveClass('text-green-600')
})

test('handles 422 error response from backend', async () => {
  mockedAxios.post.mockRejectedValueOnce({
    isAxiosError: true,
    response: {
      status: 422,
      data: {
        detail: [{ msg: 'Password must be at least 8 characters long' }],
      },
    },
  })

  renderRegisterPage()

  fireEvent.change(screen.getByLabelText(/First Name/i), { target: { value: 'Test' } })
  fireEvent.change(screen.getByLabelText(/Last Name/i), { target: { value: 'User' } })
  fireEvent.change(screen.getByLabelText(/Email Address/i), {
    target: { value: 'test@example.com' },
  })
  fireEvent.change(screen.getByLabelText(/Password/i), { target: { value: 'weak' } })

  fireEvent.click(screen.getByRole('button', { name: /Create Account/i }))

  await waitFor(() => {
    expect(screen.getByText(/Password must be at least 8 characters long/i)).toBeInTheDocument()
  })
})

test('successfully registers and redirects', async () => {
  mockedAxios.post.mockResolvedValueOnce({ data: { id: '123' } }) // Register
  mockedAxios.post.mockResolvedValueOnce({ data: { access_token: 'fake-token' } }) // Login

  renderRegisterPage()

  fireEvent.change(screen.getByLabelText(/First Name/i), { target: { value: 'Test' } })
  fireEvent.change(screen.getByLabelText(/Last Name/i), { target: { value: 'User' } })
  fireEvent.change(screen.getByLabelText(/Email Address/i), {
    target: { value: 'test@example.com' },
  })
  fireEvent.change(screen.getByLabelText(/Password/i), { target: { value: 'StrongPass1!' } })

  fireEvent.click(screen.getByRole('button', { name: /Create Account/i }))

  await waitFor(() => {
    expect(mockedAxios.post).toHaveBeenCalledWith('/api/auth/register', expect.anything())
    expect(mockedAxios.post).toHaveBeenCalledWith('/api/auth/login', expect.anything())
  })
})
