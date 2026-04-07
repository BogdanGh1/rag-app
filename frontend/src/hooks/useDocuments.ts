import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { deleteDocument, getDocuments, uploadDocuments } from '../api/documents'

export function useDocuments(dbId: string) {
  const queryClient = useQueryClient()

  const documentsQuery = useQuery({
    queryKey: ['documents', dbId],
    queryFn: () => getDocuments(dbId),
    enabled: !!dbId,
    staleTime: 1000 * 60 * 5, // treat cached data as fresh for 5 minutes
  })

  const uploadMutation = useMutation({
    mutationFn: (files: File[]) => uploadDocuments({ files, dbId }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['documents', dbId] }),
  })

  const deleteMutation = useMutation({
    mutationFn: (documentId: string) => deleteDocument({ documentId, dbId }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['documents', dbId] }),
  })

  return {
    documents: documentsQuery.data ?? [],
    isLoading: documentsQuery.isLoading,
    uploadFiles: uploadMutation.mutate,
    isUploading: uploadMutation.isPending,
    uploadError: uploadMutation.error,
    deleteDocument: deleteMutation.mutate,
    isDeleting: deleteMutation.isPending,
  }
}
