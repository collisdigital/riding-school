import { render, screen } from '@testing-library/react'
import { expect, test } from 'vitest'
import App from './App'

test('renders riding school tracker title', () => {
  render(<App />)
  const titleElement = screen.getByText(/Riding School Tracker/i)
  expect(titleElement).toBeDefined()
})

test('shows loading message initially', () => {
  render(<App />)
  const loadingElement = screen.getByText(/Loading.../i)
  expect(loadingElement).toBeDefined()
})
