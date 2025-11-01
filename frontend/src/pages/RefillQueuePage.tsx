/**
 * Enterprise Refill Queue Page - Professional dashboard for Fortune 50 healthcare companies
 */
import { useState, useMemo } from 'react'
import { Link } from 'react-router-dom'
import { useRefillQueue } from '../hooks/useRefillQueue'
import { Button } from '../components/ui/button'
import { Badge } from '../components/ui/badge'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '../components/ui/table'
import { DashboardMetrics } from '../components/DashboardMetrics'
import { QueueFilters } from '../components/QueueFilters'
import { 
  Loader2, 
  ArrowUpDown, 
  Clock, 
  CheckCircle2, 
  XCircle, 
  FileText,
  User,
  Pill,
  TrendingUp
} from 'lucide-react'

export default function RefillQueuePage() {
  const { data: requests, isLoading, error } = useRefillQueue()
  const [activeFilter, setActiveFilter] = useState<'all' | 'approved' | 'denied' | 'mismatches'>('all')
  const [searchQuery, setSearchQuery] = useState('')
  const [sortBy, setSortBy] = useState<'name' | 'medication' | 'decision' | 'date'>('decision')

  // Calculate metrics
  const metrics = useMemo(() => {
    if (!requests) return { totalPending: 0, aiApproved: 0, aiDenied: 0, avgReviewTime: 22, mismatches: 0 }
    
    const totalPending = requests.length
    const aiApproved = requests.filter(r => r.ai_decision === 'Approve').length
    const aiDenied = requests.filter(r => r.ai_decision === 'Deny').length
    const mismatches = requests.filter(r => 
      r.ai_decision === 'Approve' && r.final_decision === 'Deny' ||
      r.ai_decision === 'Deny' && r.final_decision === 'Approve'
    ).length

    return {
      totalPending,
      aiApproved,
      aiDenied,
      avgReviewTime: 22, // Mock average from real usage
      mismatches
    }
  }, [requests])

  // Filter and search requests
  const filteredRequests = useMemo(() => {
    if (!requests) return []

    let filtered = requests

    // Apply category filter
    if (activeFilter === 'approved') {
      filtered = filtered.filter(r => r.ai_decision === 'Approve')
    } else if (activeFilter === 'denied') {
      filtered = filtered.filter(r => r.ai_decision === 'Deny')
    } else if (activeFilter === 'mismatches') {
      filtered = filtered.filter(r => 
        (r.ai_decision === 'Approve' && r.final_decision === 'Deny') ||
        (r.ai_decision === 'Deny' && r.final_decision === 'Approve')
      )
    }

    // Apply search
    if (searchQuery) {
      const query = searchQuery.toLowerCase()
      filtered = filtered.filter(r => {
        const patientName = r.patient 
          ? `${r.patient.first_name} ${r.patient.last_name}`.toLowerCase()
          : ''
        const mrn = r.patient?.mrn.toLowerCase() || ''
        const medication = r.protocol?.medication_class.toLowerCase() || ''
        return patientName.includes(query) || mrn.includes(query) || medication.includes(query)
      })
    }

    // Apply sorting
    filtered = [...filtered].sort((a, b) => {
      switch (sortBy) {
        case 'name':
          const nameA = a.patient ? `${a.patient.first_name} ${a.patient.last_name}` : ''
          const nameB = b.patient ? `${b.patient.first_name} ${b.patient.last_name}` : ''
          return nameA.localeCompare(nameB)
        case 'medication':
          return (a.protocol?.medication_class || '').localeCompare(b.protocol?.medication_class || '')
        case 'decision':
          // Deny first, then Approve
          if (a.ai_decision === 'Deny' && b.ai_decision !== 'Deny') return -1
          if (a.ai_decision !== 'Deny' && b.ai_decision === 'Deny') return 1
          return 0
        case 'date':
          return new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
        default:
          return 0
      }
    })

    return filtered
  }, [requests, activeFilter, searchQuery, sortBy])

  const totalCounts = useMemo(() => {
    if (!requests) return { all: 0, approved: 0, denied: 0, mismatches: 0 }
    return {
      all: requests.length,
      approved: requests.filter(r => r.ai_decision === 'Approve').length,
      denied: requests.filter(r => r.ai_decision === 'Deny').length,
      mismatches: requests.filter(r => 
        (r.ai_decision === 'Approve' && r.final_decision === 'Deny') ||
        (r.ai_decision === 'Deny' && r.final_decision === 'Approve')
      ).length
    }
  }, [requests])

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
        <Card className="w-full max-w-md">
          <CardHeader>
            <CardTitle className="text-destructive">Error Loading Queue</CardTitle>
            <CardDescription>
              Failed to load refill requests. Please try again later.
            </CardDescription>
          </CardHeader>
        </Card>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">
      {/* Header */}
      <div className="bg-white border-b shadow-sm">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-600 to-cyan-600 bg-clip-text text-transparent">
                MedRefills AI
              </h1>
              <p className="text-sm text-muted-foreground mt-1">
                Intelligent Medication Refill Management Platform
              </p>
            </div>
            <div className="flex items-center gap-4">
              <div className="text-right">
                <p className="text-sm text-muted-foreground">Review Queue</p>
                <p className="text-2xl font-bold">{metrics.totalPending} pending</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="container mx-auto px-6 py-8">
        {/* Dashboard Metrics */}
        <div className="mb-8">
          <DashboardMetrics metrics={metrics} />
        </div>

        {/* Queue Filters */}
        <Card className="mb-6">
          <CardHeader>
            <CardTitle>Refill Queue</CardTitle>
            <CardDescription>
              Review and process medication refill requests. Target review time: &lt;30 seconds per case.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <QueueFilters
              activeFilter={activeFilter}
              onFilterChange={setActiveFilter}
              searchQuery={searchQuery}
              onSearchChange={setSearchQuery}
              totalCounts={totalCounts}
            />
          </CardContent>
        </Card>

        {/* Requests Table */}
        {filteredRequests.length === 0 ? (
          <Card>
            <CardContent className="py-12">
              <div className="text-center">
                <FileText className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                <p className="text-lg font-semibold mb-2">No requests found</p>
                <p className="text-muted-foreground">
                  {searchQuery || activeFilter !== 'all'
                    ? 'Try adjusting your filters or search query'
                    : 'No pending refill requests at this time'}
                </p>
              </div>
            </CardContent>
          </Card>
        ) : (
          <Card>
            <CardContent className="p-0">
              <div className="overflow-x-auto">
                <Table>
                  <TableHeader>
                    <TableRow className="bg-slate-50">
                      <TableHead>
                        <Button
                          variant="ghost"
                          size="sm"
                          className="h-8 -ml-3"
                          onClick={() => setSortBy(sortBy === 'name' ? 'name' : 'name')}
                        >
                          <User className="mr-2 h-4 w-4" />
                          Patient
                          <ArrowUpDown className="ml-2 h-3 w-3" />
                        </Button>
                      </TableHead>
                      <TableHead>
                        <Button
                          variant="ghost"
                          size="sm"
                          className="h-8 -ml-3"
                          onClick={() => setSortBy('medication')}
                        >
                          <Pill className="mr-2 h-4 w-4" />
                          Medication Class
                          <ArrowUpDown className="ml-2 h-3 w-3" />
                        </Button>
                      </TableHead>
                      <TableHead>
                        <Button
                          variant="ghost"
                          size="sm"
                          className="h-8 -ml-3"
                          onClick={() => setSortBy('decision')}
                        >
                          AI Recommendation
                          <ArrowUpDown className="ml-2 h-3 w-3" />
                        </Button>
                      </TableHead>
                      <TableHead>Confidence</TableHead>
                      <TableHead>Status</TableHead>
                      <TableHead>Created</TableHead>
                      <TableHead className="text-right">Action</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {filteredRequests.map((request) => {
                      const patientName = request.patient
                        ? `${request.patient.first_name} ${request.patient.last_name}`
                        : 'Unknown Patient'
                      const mrn = request.patient?.mrn || 'N/A'
                      const medication = request.protocol?.medication_class || 'Unknown Medication'
                      const recommendation = request.ai_decision || 'Pending'
                      const confidence = request.ai_confidence !== null 
                        ? `${Math.round(request.ai_confidence)}%` 
                        : 'N/A'

                      return (
                        <TableRow key={request.id} className="hover:bg-slate-50/50">
                          <TableCell>
                            <div>
                              <div className="font-semibold">{patientName}</div>
                              <div className="text-xs text-muted-foreground">MRN: {mrn}</div>
                            </div>
                          </TableCell>
                          <TableCell>
                            <div className="flex items-center gap-2">
                              <Pill className="h-4 w-4 text-blue-600" />
                              <span className="font-medium">{medication}</span>
                            </div>
                          </TableCell>
                          <TableCell>
                            <div className="flex items-center gap-2">
                              {recommendation === 'Deny' ? (
                                <XCircle className="h-4 w-4 text-red-600" />
                              ) : recommendation === 'Approve' ? (
                                <CheckCircle2 className="h-4 w-4 text-green-600" />
                              ) : (
                                <Clock className="h-4 w-4 text-yellow-600" />
                              )}
                              <Badge
                                variant={
                                  recommendation === 'Deny'
                                    ? 'destructive'
                                    : recommendation === 'Approve'
                                    ? 'success'
                                    : 'warning'
                                }
                              >
                                {recommendation}
                              </Badge>
                            </div>
                          </TableCell>
                          <TableCell>
                            <div className="flex items-center gap-1">
                              <TrendingUp className="h-3 w-3 text-muted-foreground" />
                              <span className="text-sm">{confidence}</span>
                            </div>
                          </TableCell>
                          <TableCell>
                            <Badge variant="outline">
                              {request.status.replace('_', ' ')}
                            </Badge>
                          </TableCell>
                          <TableCell>
                            <span className="text-xs text-muted-foreground">
                              {new Date(request.created_at).toLocaleDateString()}
                            </span>
                          </TableCell>
                          <TableCell className="text-right">
                            <Link to={`/request/${request.id}`}>
                              <Button variant="default" size="sm">
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
            </CardContent>
          </Card>
        )}

        {/* Summary Footer */}
        <Card className="mt-6 bg-gradient-to-r from-blue-50 to-cyan-50 border-blue-200">
          <CardContent className="py-4">
            <div className="flex items-center justify-between text-sm">
              <div className="flex items-center gap-6">
                <div>
                  <span className="text-muted-foreground">Showing </span>
                  <span className="font-semibold">{filteredRequests.length}</span>
                  <span className="text-muted-foreground"> of </span>
                  <span className="font-semibold">{totalCounts.all}</span>
                  <span className="text-muted-foreground"> requests</span>
                </div>
                <div className="flex items-center gap-2">
                  <Clock className="h-4 w-4 text-muted-foreground" />
                  <span className="text-muted-foreground">
                    Est. completion time: {Math.ceil(filteredRequests.length * 0.5)} minutes
                  </span>
                </div>
              </div>
              {filteredRequests.length > 0 && (
                <Button variant="outline" size="sm">
                  Batch Review Selected
                </Button>
              )}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
