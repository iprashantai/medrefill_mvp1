/**
 * API service for communicating with the MedRefills backend.
 */
import axios from 'axios'

const API_BASE_URL = (import.meta.env?.VITE_API_URL as string) || 'http://localhost:8000'

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Types
export interface RefillRequest {
  id: number
  patient_id: number
  protocol_id: number
  status: string
  ai_decision: string | null
  ai_reason: string | null
  ai_confidence: number | null
  final_decision: string | null
  reviewed_by: string | null
  reviewed_at: string | null
  created_at: string
  updated_at: string
  patient: {
    id: number
    mrn: string
    first_name: string
    last_name: string
    date_of_birth: string
  } | null
  protocol: {
    id: number
    medication_class: string
    max_months_since_visit: number | null
    max_a1c_value: number | null
    require_recent_a1c: number | null
  } | null
}

export interface ProtocolCheck {
  protocol: string
  emr_data: string
  status: string
}

export interface RefillDetailData {
  request: RefillRequest
  patient_data: {
    mrn: string
    first_name: string
    last_name: string
    dob: string
  }
  clinical_data: {
    last_visit_date: string
    labs: {
      A1c: {
        value: number
        date: string
      }
    }
  }
  protocols_checked: ProtocolCheck[]
}

export interface ReviewPayload {
  decision: 'Approve' | 'Deny'
  user_id: string
}

/**
 * Get all refill requests pending human review.
 */
export async function getRefillQueue(): Promise<RefillRequest[]> {
  const response = await apiClient.get<RefillRequest[]>('/api/v1/refill-queue')
  return response.data
}

/**
 * Get detailed information about a specific refill request.
 */
export async function getRefillDetail(requestId: string): Promise<RefillDetailData> {
  const response = await apiClient.get<RefillDetailData>(`/api/v1/refill-request/${requestId}`)
  return response.data
}

/**
 * Submit a review decision for a refill request.
 */
export async function postReview(
  requestId: string,
  decision: 'Approve' | 'Deny',
  userId: string = 'clinical_staff_member'
): Promise<RefillRequest> {
  const payload: ReviewPayload = {
    decision,
    user_id: userId,
  }
  const response = await apiClient.post<RefillRequest>(
    `/api/v1/refill-request/${requestId}/review`,
    payload
  )
  return response.data
}

