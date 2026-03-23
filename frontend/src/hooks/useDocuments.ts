import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { deleteDocument, getDocuments, uploadDocuments } from '../api/documents'

export function useDocuments(backend: string) {
  const queryClient = useQueryClient()

  const documentsQuery = useQuery({
    queryKey: ['documents', backend],
    queryFn: () => getDocuments(backend),
  })

  const uploadMutation = useMutation({
    mutationFn: (files: File[]) => uploadDocuments({ files, backend }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['documents', backend] }),
  })

  const deleteMutation = useMutation({
    mutationFn: (documentId: string) => deleteDocument({ documentId, backend }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['documents', backend] }),
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
