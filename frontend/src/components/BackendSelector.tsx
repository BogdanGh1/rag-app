import { useBackend } from '../hooks/useBackend'

export function BackendSelector() {
  const { backends, isLoading, switchBackend, isSwitching } = useBackend()

  if (isLoading) {
    return <div className="text-sm text-gray-500">Loading backends...</div>
  }

  return (
    <div className="flex items-center gap-3">
      <span className="text-sm font-medium text-gray-700">Backend:</span>
      <div className="flex gap-1.5">
        {backends.map(backend => (
          <button
            key={backend.name}
            onClick={() => switchBackend(backend.name)}
            disabled={isSwitching || backend.active}
            className={`px-3 py-1.5 rounded-md text-sm font-medium transition-colors ${
              backend.active
                ? 'bg-blue-600 text-white cursor-default'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            } disabled:opacity-60`}
          >
            {backend.name}
          </button>
        ))}
      </div>
    </div>
  )
}
