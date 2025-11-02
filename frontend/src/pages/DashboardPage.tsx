import React, { useState, useMemo } from 'react';
import QueuePanel from '../components/QueuePanel';
import DetailPanel from '../components/DetailPanel';
import DashboardHeader from '../components/DashboardHeader';
import { useRefillQueue } from '../hooks/useRefillQueue';

const DashboardPage: React.FC = () => {
  const [selectedRequestId, setSelectedRequestId] = useState<string | null>(null);
  const { data: requests } = useRefillQueue();

  const metrics = useMemo(() => {
    if (!requests) return { totalPending: 0, aiApproved: 0, aiDenied: 0 };
    
    const totalPending = requests.length;
    const aiApproved = requests.filter(r => r.ai_decision === 'Approve').length;
    const aiDenied = requests.filter(r => r.ai_decision === 'Deny').length;

    return { totalPending, aiApproved, aiDenied };
  }, [requests]);

  return (
    <div className="h-screen w-screen bg-slate-100 p-4 flex flex-col gap-4">
      <DashboardHeader {...metrics} />
      <main className="flex-grow grid grid-cols-12 gap-4">
        <div className="col-span-5 bg-white rounded-lg shadow">
          <QueuePanel onSelectRequest={setSelectedRequestId} />
        </div>
        <div className="col-span-7 bg-white rounded-lg shadow">
          {selectedRequestId ? (
            <DetailPanel requestId={selectedRequestId} />
          ) : (
            <div className="flex items-center justify-center h-full">
              <p className="text-muted-foreground">Select a request to view details</p>
            </div>
          )}
        </div>
      </main>
    </div>
  );
};

export default DashboardPage;
