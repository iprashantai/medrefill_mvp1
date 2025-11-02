/**
 * Dashboard Header - Displays live metrics and analytics for the refill queue.
 */
import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';

interface DashboardHeaderProps {
  totalPending: number;
  aiApproved: number;
  aiDenied: number;
}

const DashboardHeader: React.FC<DashboardHeaderProps> = ({ totalPending, aiApproved, aiDenied }) => {
  return (
    <header className="bg-white rounded-lg shadow p-4 mb-4">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold">AI MedRefill Mission Control</h1>
          <p className="text-sm text-muted-foreground">Real-time dashboard for clinical review</p>
        </div>
        <div className="flex gap-4">
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium">Total Pending</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{totalPending}</div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium">AI Approved</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-green-600">{aiApproved}</div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium">AI Denied</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-red-600">{aiDenied}</div>
            </CardContent>
          </Card>
        </div>
      </div>
    </header>
  );
};

export default DashboardHeader;
