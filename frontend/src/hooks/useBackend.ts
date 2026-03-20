import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { getBackends, setActiveBackend } from '../api/backends'

export function useBackend() {
  const queryClient = useQueryClient()

  const backendsQuery = useQuery({
    queryKey: ['backends'],
    queryFn: getBackends,
  })

  const switchMutation = useMutation({
    mutationFn: setActiveBackend,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['backends'] }),
  })

  return {
    backends: backendsQuery.data?.backends ?? [],
    activeBackend: backendsQuery.data?.active ?? '',
    isLoading: backendsQuery.isLoading,
    switchBackend: switchMutation.mutate,
    isSwitching: switchMutation.isPending,
  }
}
