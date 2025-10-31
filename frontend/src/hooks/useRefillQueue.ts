/**
 * React Query hooks for refill requests.
 */
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import * as api from '../services/api'

/**
 * Hook to fetch the refill queue.
 */
export function useRefillQueue() {
  return useQuery({
    queryKey: ['refill-queue'],
    queryFn: api.getRefillQueue,
    refetchInterval: 30000, // Refetch every 30 seconds
  })
}

/**
 * Hook to fetch detailed refill request data.
 */
export function useRefillDetail(requestId: string) {
  return useQuery({
    queryKey: ['refill-detail', requestId],
    queryFn: () => api.getRefillDetail(requestId),
    enabled: !!requestId,
  })
}

/**
 * Hook to submit a review decision.
 */
export function useReviewRefill() {
  const queryClient = useQueryClient()
  const navigate = useNavigate()

  return useMutation({
    mutationFn: ({ requestId, decision, userId }: { requestId: string; decision: 'Approve' | 'Deny'; userId?: string }) =>
      api.postReview(requestId, decision, userId),
    onSuccess: () => {
      // Invalidate and refetch the queue
      queryClient.invalidateQueries({ queryKey: ['refill-queue'] })
      // Navigate back to queue
      navigate('/')
    },
  })
}

