1/**
 * Queue Panel - A dense and interactive queue of refill requests.
 */
import { useState, useMemo } from 'react';
import { useRefillQueue } from '../hooks/useRefillQueue';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from './ui/card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from './ui/table';
import { QueueFilters } from './QueueFilters';
import { Loader2 } from 'lucide-react';

interface QueuePanelProps {
  onSelectRequest: (requestId: string) => void;
}

const QueuePanel: React.FC<QueuePanelProps> = ({ onSelectRequest }) => {
  const { data: requests, isLoading, error } = useRefillQueue();
  const [activeFilter, setActiveFilter] = useState<'all' | 'approved' | 'denied' | 'mismatches'>('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [sortBy] = useState<'name' | 'medication' | 'decision' | 'date'>('decision');

  const filteredRequests = useMemo(() => {
    if (!requests) return [];

    let filtered = requests;

    if (activeFilter === 'approved') {
      filtered = filtered.filter(r => r.ai_decision === 'Approve');
    } else if (activeFilter === 'denied') {
      filtered = filtered.filter(r => r.ai_decision === 'Deny');
    }

    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      filtered = filtered.filter(r => {
        const patientName = r.patient ? `${r.patient.first_name} ${r.patient.last_name}`.toLowerCase() : '';
        const mrn = r.patient?.mrn.toLowerCase() || '';
        const medication = r.protocol?.medication_class.toLowerCase() || '';
        return patientName.includes(query) || mrn.includes(query) || medication.includes(query);
      });
    }

    filtered = [...filtered].sort((a, b) => {
      switch (sortBy) {
        case 'name':
          const nameA = a.patient ? `${a.patient.first_name} ${a.patient.last_name}` : '';
          const nameB = b.patient ? `${b.patient.first_name} ${b.patient.last_name}` : '';
          return nameA.localeCompare(nameB);
        case 'medication':
          return (a.protocol?.medication_class || '').localeCompare(b.protocol?.medication_class || '');
        case 'decision':
          if (a.ai_decision === 'Deny' && b.ai_decision !== 'Deny') return -1;
          if (a.ai_decision !== 'Deny' && b.ai_decision === 'Deny') return 1;
          return 0;
        case 'date':
          return new Date(b.created_at).getTime() - new Date(a.created_at).getTime();
        default:
          return 0;
      }
    });

    return filtered;
  }, [requests, activeFilter, searchQuery, sortBy]);

  const totalCounts = useMemo(() => {
    if (!requests) return { all: 0, approved: 0, denied: 0, mismatches: 0 };
    return {
      all: requests.length,
      approved: requests.filter(r => r.ai_decision === 'Approve').length,
      denied: requests.filter(r => r.ai_decision === 'Deny').length,
      mismatches: 0, // This will be recalculated or removed
    };
  }, [requests]);

  if (isLoading) {
    return <div className="flex items-center justify-center h-full"><Loader2 className="h-8 w-8 animate-spin text-primary" /></div>;
  }

  if (error) {
    return (
      <Card className="m-4">
        <CardHeader>
          <CardTitle className="text-destructive">Error Loading Queue</CardTitle>
          <CardDescription>Failed to load refill requests. Please try again later.</CardDescription>
        </CardHeader>
      </Card>
    );
  }

  return (
    <div className="flex flex-col h-full">
      <CardHeader>
        <CardTitle>Refill Queue</CardTitle>
        <CardDescription>Select a request to begin review.</CardDescription>
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
      <div className="flex-grow overflow-y-auto">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Patient</TableHead>
              <TableHead>Medication</TableHead>
              <TableHead>AI Decision</TableHead>
              <TableHead>Action</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {filteredRequests.map((request) => (
              <TableRow key={request.id} onClick={() => onSelectRequest(request.id.toString())} className="cursor-pointer hover:bg-slate-50">
                <TableCell>
                  <div>
                    <div className="font-semibold">{request.patient ? `${request.patient.first_name} ${request.patient.last_name}` : 'Unknown Patient'}</div>
                    <div className="text-xs text-muted-foreground">MRN: {request.patient?.mrn || 'N/A'}</div>
                  </div>
                </TableCell>
                <TableCell>{request.protocol?.medication_class}</TableCell>
                <TableCell>
                  <Badge variant={request.ai_decision === 'Approve' ? 'success' : 'destructive'}>
                    {request.ai_decision}
                  </Badge>
                </TableCell>
                <TableCell>
                  <Button variant="outline" size="sm">View</Button>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>
    </div>
  );
};

export default QueuePanel;