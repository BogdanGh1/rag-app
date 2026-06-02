import { useQuery } from '@tanstack/react-query'
import { getModels } from '../api/models'

export function useModels() {
  const query = useQuery({
    queryKey: ['models'],
    queryFn: getModels,
  })

  return {
    models: query.data ?? [],
    isLoading: query.isLoading,
  }
}
