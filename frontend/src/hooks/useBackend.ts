import { useQuery } from '@tanstack/react-query'
import { getBackends } from '../api/backends'

export function useBackend() {
  const backendsQuery = useQuery({
    queryKey: ['backends'],
    queryFn: getBackends,
  })

  return {
    backends: backendsQuery.data ?? [],
    isLoading: backendsQuery.isLoading,
  }
}
