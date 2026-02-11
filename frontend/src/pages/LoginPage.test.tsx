import { render, screen } from '@testing-library/react'
import { expect, test, describe } from 'vitest'
import LoginPage from './LoginPage'
import { BrowserRouter } from 'react-router-dom'

describe('LoginPage', () => {
  test('renders login form with accessible labels', () => {
    render(
      <BrowserRouter>
        <LoginPage />
      </BrowserRouter>,
    )

    // These assertions will fail if the input is not associated with the label
    expect(screen.getByLabelText(/Email Address/i)).toBeDefined()
    expect(screen.getByLabelText(/Password/i)).toBeDefined()
  })
})
