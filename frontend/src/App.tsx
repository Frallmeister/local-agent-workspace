import { useEffect, useState } from 'react'
import { getHealth, type HealthResponse } from './api/health'

type HealthState =
  | { kind: 'loading' }
  | { kind: 'success'; health: HealthResponse }
  | { kind: 'error' }

export default function App() {
  const [state, setState] = useState<HealthState>({ kind: 'loading' })
  const [attempt, setAttempt] = useState(0)

  useEffect(() => {
    const controller = new AbortController()
    setState({ kind: 'loading' })
    getHealth(controller.signal).then(
      (health) => {
        if (!controller.signal.aborted) setState({ kind: 'success', health })
      },
      () => {
        if (!controller.signal.aborted) setState({ kind: 'error' })
      },
    )
    return () => controller.abort()
  }, [attempt])

  return (
    <main>
      <header>
        <p className="eyebrow">Application foundation</p>
        <h1>Local Agent Workspace</h1>
        <p className="intro">Your local assistant, taking shape.</p>
      </header>

      <section className="health-card" aria-labelledby="health-heading">
        <h2 id="health-heading">Backend connection</h2>
        <div role="status" aria-live="polite" aria-atomic="true">
          {state.kind === 'loading' && (
            <p className="status">Checking backend…</p>
          )}
          {state.kind === 'success' && (
            <>
              <p className="status success">Backend connected</p>
              <p>Health status: <strong>{state.health.status}</strong></p>
            </>
          )}
          {state.kind === 'error' && (
            <>
              <p className="status error">Unable to confirm backend health</p>
              <p>Make sure the backend is running, then try again.</p>
            </>
          )}
        </div>
        <button
          type="button"
          disabled={state.kind === 'loading'}
          onClick={() => setAttempt((value) => value + 1)}
        >
          {state.kind === 'loading' ? 'Checking…' : 'Check again'}
        </button>
      </section>

      <p className="scope">This first version checks the backend connection. Assistant features are still in development.</p>
    </main>
  )
}
