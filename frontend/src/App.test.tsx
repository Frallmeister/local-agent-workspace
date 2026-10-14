import { StrictMode } from 'react'
import { act, cleanup, fireEvent, render, screen } from '@testing-library/react'
import { afterEach, expect, test, vi } from 'vitest'
import App from './App'

afterEach(() => {
  cleanup()
  vi.unstubAllGlobals()
})

test('shows loading and disables retry until the health request succeeds', async () => {
  let complete!: (response: Response) => void
  vi.stubGlobal('fetch', vi.fn(() => new Promise<Response>((resolve) => {
    complete = resolve
  })))

  render(<App />)
  expect(screen.getByRole('status').textContent).toContain('Checking backend')
  expect((screen.getByRole('button') as HTMLButtonElement).disabled).toBe(true)

  await act(async () => { complete(Response.json({ status: 'ok' })) })

  expect(screen.getByRole('status').textContent).toContain('Backend connected')
  expect(screen.getByRole('status').textContent).toContain('Health status: ok')
  expect((screen.getByRole('button', { name: 'Check again' }) as HTMLButtonElement).disabled).toBe(false)
})

test.each([
  ['network failure', () => Promise.reject(new TypeError('offline'))],
  ['HTTP failure', () => Promise.resolve(new Response('', { status: 503 }))],
  ['invalid health response', () => Promise.resolve(Response.json({ status: 'wrong' }))],
])('shows a useful error for %s and recovers on retry', async (_label, fail) => {
  const fetchMock = vi.fn().mockImplementationOnce(fail)
    .mockResolvedValueOnce(Response.json({ status: 'ok' }))
  vi.stubGlobal('fetch', fetchMock)

  render(<App />)
  await screen.findByText('Unable to confirm backend health')
  expect(screen.getByText('Make sure the backend is running, then try again.')).toBeDefined()

  fireEvent.click(screen.getByRole('button', { name: 'Check again' }))

  await screen.findByText('Backend connected')
  expect(fetchMock).toHaveBeenCalledTimes(2)
  expect(fetchMock.mock.calls[0][0]).toBe('/api/health')
})

test('ignores the cancelled StrictMode request when its response arrives late', async () => {
  const requests: { signal: AbortSignal; resolve: (response: Response) => void }[] = []
  vi.stubGlobal('fetch', vi.fn((_url: string, options: RequestInit) => (
    new Promise<Response>((resolve) => {
      requests.push({ signal: options.signal as AbortSignal, resolve })
    })
  )))

  const { unmount } = render(<StrictMode><App /></StrictMode>)
  expect(requests).toHaveLength(2)
  expect(requests[0].signal.aborted).toBe(true)

  await act(async () => { requests[1].resolve(Response.json({ status: 'ok' })) })
  expect(screen.getByText('Backend connected')).toBeDefined()

  await act(async () => { requests[0].resolve(new Response('', { status: 503 })) })
  expect(screen.queryByText('Unable to confirm backend health')).toBeNull()
  expect(screen.getByText('Backend connected')).toBeDefined()

  unmount()
  expect(requests[1].signal.aborted).toBe(true)
})
