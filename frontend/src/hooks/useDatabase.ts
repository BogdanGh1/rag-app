import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { createDatabase, deleteDatabase, getDatabases, updateDatabase } from '../api/databases'

export function useDatabase() {
  const queryClient = useQueryClient()

  const databasesQuery = useQuery({
    queryKey: ['databases'],
    queryFn: getDatabases,
  })

  const createMutation = useMutation({
    mutationFn: createDatabase,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['databases'] }),
  })

  const updateMutation = useMutation({
    mutationFn: updateDatabase,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['databases'] }),
  })

  const deleteMutation = useMutation({
    mutationFn: deleteDatabase,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['databases'] }),
  })

  return {
    databases: databasesQuery.data ?? [],
    isLoading: databasesQuery.isLoading,
    createDatabase: createMutation.mutateAsync,
    isCreating: createMutation.isPending,
    createError: createMutation.error,
    updateDatabase: updateMutation.mutateAsync,
    isUpdating: updateMutation.isPending,
    updateError: updateMutation.error,
    deleteDatabase: deleteMutation.mutate,
    isDeleting: deleteMutation.isPending,
  }
}
