/**
 * Dashboard Metrics Component - KPI Cards for enterprise healthcare dashboard
 */
import { Card, CardContent, CardHeader, CardTitle } from './ui/card'
import { TrendingUp, Clock, CheckCircle2, XCircle, AlertCircle } from 'lucide-react'

interface MetricsData {
  totalPending: number
  aiApproved: number
  aiDenied: number
  avgReviewTime: number
  mismatches: number
}

interface DashboardMetricsProps {
  metrics: MetricsData
}

export function DashboardMetrics({ metrics }: DashboardMetricsProps) {
  const { totalPending, aiApproved, aiDenied, avgReviewTime, mismatches } = metrics

  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-5">
      <Card className="border-l-4 border-l-blue-600">
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Total Pending</CardTitle>
          <AlertCircle className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">{totalPending}</div>
          <p className="text-xs text-muted-foreground">Require review</p>
        </CardContent>
      </Card>

      <Card className="border-l-4 border-l-green-600">
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">AI Approved</CardTitle>
          <CheckCircle2 className="h-4 w-4 text-green-600" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold text-green-600">{aiApproved}</div>
          <p className="text-xs text-muted-foreground">
            {totalPending > 0 ? Math.round((aiApproved / totalPending) * 100) : 0}% of total
          </p>
        </CardContent>
      </Card>

      <Card className="border-l-4 border-l-red-600">
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">AI Denied</CardTitle>
          <XCircle className="h-4 w-4 text-red-600" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold text-red-600">{aiDenied}</div>
          <p className="text-xs text-muted-foreground">
            {totalPending > 0 ? Math.round((aiDenied / totalPending) * 100) : 0}% of total
          </p>
        </CardContent>
      </Card>

      <Card className="border-l-4 border-l-yellow-600">
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Mismatches</CardTitle>
          <AlertCircle className="h-4 w-4 text-yellow-600" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold text-yellow-600">{mismatches}</div>
          <p className="text-xs text-muted-foreground">Require attention</p>
        </CardContent>
      </Card>

      <Card className="border-l-4 border-l-purple-600">
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Avg Review Time</CardTitle>
          <Clock className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">{avgReviewTime}s</div>
          <p className="text-xs text-muted-foreground">
            <TrendingUp className="inline h-3 w-3 mr-1" />
            Target: &lt;30s
          </p>
        </CardContent>
      </Card>
    </div>
  )
}

