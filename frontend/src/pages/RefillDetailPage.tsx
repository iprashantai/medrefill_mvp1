/**
 * Refill Detail Page - HITL dashboard for reviewing a single refill request.
 */
import { useParams } from 'react-router-dom'
import { useRefillDetail, useReviewRefill } from '../hooks/useRefillQueue'
import { Button } from '../components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '../components/ui/table'
import { Separator } from '../components/ui/separator'
import { Loader2 } from 'lucide-react'

export default function RefillDetailPage() {
  const { requestId } = useParams<{ requestId: string }>()
  const { data: detailData, isLoading, error } = useRefillDetail(requestId || '')
  const reviewMutation = useReviewRefill()

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    )
  }

  if (error || !detailData) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-destructive mb-2">Error</h2>
          <p className="text-muted-foreground">
            Failed to load refill request details. Please try again later.
          </p>
        </div>
      </div>
    )
  }

  const { request, patient_data, protocols_checked } = detailData
  const patientName = `${patient_data.first_name} ${patient_data.last_name}`
  const medication = request.protocol?.medication_class || 'Unknown Medication'
  const aiDecision = request.ai_decision || 'Pending'
  const aiReason = request.ai_reason || 'No reason provided'
  const aiConfidence = request.ai_confidence !== null ? `${Math.round(request.ai_confidence)}%` : 'N/A'

  const handleApprove = () => {
    if (requestId) {
      reviewMutation.mutate({
        requestId,
        decision: 'Approve',
        userId: 'clinical_staff_member',
      })
    }
  }

  const handleDeny = () => {
    if (requestId) {
      reviewMutation.mutate({
        requestId,
        decision: 'Deny',
        userId: 'clinical_staff_member',
      })
    }
  }

  return (
    <div className="container mx-auto py-10">
      <div className="mb-6">
        <h1 className="text-3xl font-bold tracking-tight">Refill Request Review</h1>
        <p className="text-muted-foreground mt-2">
          Review AI recommendation and make final decision
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        {/* Left Column: AI Recommendation */}
        <Card>
          <CardHeader>
            <CardTitle>AI Recommendation</CardTitle>
            <CardDescription>Automated protocol analysis results</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <p className="text-sm font-medium text-muted-foreground mb-1">Decision</p>
              <p
                className={`text-2xl font-bold ${
                  aiDecision === 'Deny'
                    ? 'text-destructive'
                    : aiDecision === 'Approve'
                    ? 'text-green-600'
                    : 'text-muted-foreground'
                }`}
              >
                {aiDecision.toUpperCase()}
              </p>
            </div>
            <Separator />
            <div>
              <p className="text-sm font-medium text-muted-foreground mb-1">Confidence</p>
              <p className="text-lg font-semibold">{aiConfidence}</p>
            </div>
            <Separator />
            <div>
              <p className="text-sm font-medium text-muted-foreground mb-2">Reason</p>
              <p className="text-sm">{aiReason}</p>
            </div>
          </CardContent>
        </Card>

        {/* Right Column: Protocol & EMR Data */}
        <Card>
          <CardHeader>
            <CardTitle>Protocol & EMR Data</CardTitle>
            <CardDescription>Patient information and protocol checks</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <p className="text-sm font-medium text-muted-foreground mb-1">Patient</p>
              <p className="font-semibold">{patientName}</p>
              <p className="text-sm text-muted-foreground">
                DOB: {new Date(patient_data.dob).toLocaleDateString()} | MRN: {patient_data.mrn}
              </p>
            </div>
            <Separator />
            <div>
              <p className="text-sm font-medium text-muted-foreground mb-1">Medication</p>
              <p className="font-semibold">{medication}</p>
            </div>
            <Separator />
            <div>
              <p className="text-sm font-medium text-muted-foreground mb-2">Protocol Checks</p>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Protocol</TableHead>
                    <TableHead>EMR Data</TableHead>
                    <TableHead className="text-right">Status</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {protocols_checked.map((check, index) => (
                    <TableRow key={index}>
                      <TableCell className="font-medium">{check.protocol}</TableCell>
                      <TableCell>{check.emr_data}</TableCell>
                      <TableCell className="text-right">
                        <span
                          className={
                            check.status.includes('✅')
                              ? 'text-green-600 font-semibold'
                              : 'text-destructive font-semibold'
                          }
                        >
                          {check.status}
                        </span>
                      </TableCell>
                    </TableRow>
                  ))}
                  {protocols_checked.length === 0 && (
                    <TableRow>
                      <TableCell colSpan={3} className="text-center text-muted-foreground">
                        No protocol checks available
                      </TableCell>
                    </TableRow>
                  )}
                </TableBody>
              </Table>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Action Bar */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex justify-end gap-4">
            <Button
              variant="destructive"
              size="lg"
              onClick={handleDeny}
              disabled={reviewMutation.isPending}
            >
              {reviewMutation.isPending ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Processing...
                </>
              ) : (
                'Deny Refill'
              )}
            </Button>
            <Button
              size="lg"
              onClick={handleApprove}
              disabled={reviewMutation.isPending}
              className="bg-green-600 hover:bg-green-700"
            >
              {reviewMutation.isPending ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Processing...
                </>
              ) : (
                'Approve Refill'
              )}
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

