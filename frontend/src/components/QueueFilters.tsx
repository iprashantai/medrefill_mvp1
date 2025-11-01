/**
 * Queue Filters Component - Advanced filtering for refill queue
 */
import { Button } from './ui/button'
import { Badge } from './ui/badge'
import { Tabs, TabsList, TabsTrigger } from './ui/tabs'
import { Filter, Search } from 'lucide-react'

interface QueueFiltersProps {
  activeFilter: 'all' | 'approved' | 'denied' | 'mismatches'
  onFilterChange: (filter: 'all' | 'approved' | 'denied' | 'mismatches') => void
  searchQuery: string
  onSearchChange: (query: string) => void
  totalCounts: {
    all: number
    approved: number
    denied: number
    mismatches: number
  }
}

export function QueueFilters({
  activeFilter,
  onFilterChange,
  searchQuery,
  onSearchChange,
  totalCounts,
}: QueueFiltersProps) {
  return (
    <div className="space-y-4">
      <div className="flex items-center gap-4">
        <div className="relative flex-1 max-w-sm">
          <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
          <input
            type="text"
            placeholder="Search by patient name, MRN, or medication..."
            value={searchQuery}
            onChange={(e) => onSearchChange(e.target.value)}
            className="w-full rounded-md border border-input bg-background pl-8 pr-4 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
          />
        </div>
        <Button variant="outline" size="sm">
          <Filter className="mr-2 h-4 w-4" />
          Advanced Filters
        </Button>
      </div>

      <Tabs value={activeFilter} onValueChange={(v) => onFilterChange(v as any)}>
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="all" className="relative">
            All Requests
            <Badge variant="secondary" className="ml-2">
              {totalCounts.all}
            </Badge>
          </TabsTrigger>
          <TabsTrigger value="approved" className="relative">
            AI Approved
            <Badge variant="success" className="ml-2">
              {totalCounts.approved}
            </Badge>
          </TabsTrigger>
          <TabsTrigger value="denied" className="relative">
            AI Denied
            <Badge variant="destructive" className="ml-2">
              {totalCounts.denied}
            </Badge>
          </TabsTrigger>
          <TabsTrigger value="mismatches" className="relative">
            Mismatches
            <Badge variant="warning" className="ml-2">
              {totalCounts.mismatches}
            </Badge>
          </TabsTrigger>
        </TabsList>
      </Tabs>
    </div>
  )
}

