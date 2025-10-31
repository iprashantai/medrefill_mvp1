/**
 * Refill Queue Page - Displays all pending refill requests.
 */
import { Link } from 'react-router-dom'
import { useRefillQueue } from '../hooks/useRefillQueue'
import { Button } from '../components/ui/button'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '../components/ui/table'
import { Loader2 } from 'lucide-react'

export default function RefillQueuePage() {
  const { data: requests, isLoading, error } = useRefillQueue()

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-destructive mb-2">Error</h2>
          <p className="text-muted-foreground">
            Failed to load refill requests. Please try again later.
          </p>
        </div>
      </div>
    )
  }

  return (
    <div className="container mx-auto py-10">
      <div className="mb-6">
        <h1 className="text-3xl font-bold tracking-tight">Refill Queue</h1>
        <p className="text-muted-foreground mt-2">
          Review and approve medication refill requests
        </p>
      </div>

      {requests && requests.length === 0 ? (
        <div className="text-center py-12">
          <p className="text-muted-foreground text-lg">
            No pending refill requests at this time.
          </p>
        </div>
      ) : (
        <div className="border rounded-lg">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Patient Name</TableHead>
                <TableHead>Medication</TableHead>
                <TableHead>AI Recommendation</TableHead>
                <TableHead className="text-right">Action</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {requests?.map((request) => {
                const patientName = request.patient
                  ? `${request.patient.first_name} ${request.patient.last_name}`
                  : 'Unknown Patient'
                const medication = request.protocol
                  ? request.protocol.medication_class
                  : 'Unknown Medication'
                const recommendation = request.ai_decision || 'Pending'

                return (
                  <TableRow key={request.id}>
                    <TableCell className="font-medium">{patientName}</TableCell>
                    <TableCell>{medication}</TableCell>
                    <TableCell>
                      <span
                        className={`font-semibold ${
                          recommendation === 'Deny'
                            ? 'text-destructive'
                            : recommendation === 'Approve'
                            ? 'text-green-600'
                            : 'text-muted-foreground'
                        }`}
                      >
                        {recommendation}
                      </span>
                    </TableCell>
                    <TableCell className="text-right">
                      <Link to={`/request/${request.id}`}>
                        <Button variant="outline" size="sm">
                          Review
                        </Button>
                      </Link>
                    </TableCell>
                  </TableRow>
                )
              })}
            </TableBody>
          </Table>
        </div>
      )}
    </div>
  )
}

