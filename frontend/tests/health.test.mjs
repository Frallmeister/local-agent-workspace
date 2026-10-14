import assert from 'node:assert/strict'
import { test } from 'node:test'
import { getHealth } from '../src/api/health.ts'

test('returns validated health data from the relative API URL', async (t) => {
  t.mock.method(globalThis, 'fetch', async (url, options) => {
    assert.equal(url, '/api/health')
    assert.equal(options.headers.Accept, 'application/json')
    assert.ok(options.signal instanceof AbortSignal)
    return Response.json({ status: 'ok' })
  })
  assert.deepEqual(await getHealth(), { status: 'ok' })
})

for (const data of [null, [], 'ok', {}, { status: 1 }, { status: 'error' }]) {
  test(`rejects an invalid response: ${JSON.stringify(data)}`, async (t) => {
    t.mock.method(globalThis, 'fetch', async () => Response.json(data))
    await assert.rejects(getHealth(), /unexpected health response/)
  })
}

test('rejects non-success HTTP responses', async (t) => {
  t.mock.method(globalThis, 'fetch', async () => new Response('', { status: 503 }))
  await assert.rejects(getHealth(), /HTTP 503/)
})

test('rejects malformed JSON', async (t) => {
  t.mock.method(globalThis, 'fetch', async () => new Response('not JSON'))
  await assert.rejects(getHealth(), SyntaxError)
})

test('propagates network failure', async (t) => {
  t.mock.method(globalThis, 'fetch', async () => { throw new TypeError('offline') })
  await assert.rejects(getHealth(), /offline/)
})

test('combines caller cancellation with a bounded timeout', async (t) => {
  const controller = new AbortController()
  const timeout = new AbortController()
  t.mock.method(AbortSignal, 'timeout', (milliseconds) => {
    assert.equal(milliseconds, 5000)
    return timeout.signal
  })
  t.mock.method(globalThis, 'fetch', async (_url, options) => {
    timeout.abort(new DOMException('Timed out', 'TimeoutError'))
    assert.equal(options.signal.aborted, true)
    throw options.signal.reason
  })
  await assert.rejects(getHealth(controller.signal), { name: 'TimeoutError' })
})

test('honors an already cancelled caller', async (t) => {
  const controller = new AbortController()
  controller.abort()
  t.mock.method(globalThis, 'fetch', async (_url, options) => {
    assert.equal(options.signal.aborted, true)
    throw options.signal.reason
  })
  await assert.rejects(getHealth(controller.signal), { name: 'AbortError' })
})
