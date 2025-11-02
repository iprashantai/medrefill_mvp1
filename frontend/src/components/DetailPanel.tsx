/**
 * Detail Panel - A dense, feature-rich view of a single refill request.
 */
import React from 'react';
import { useRefillDetail, useReviewRefill } from '../hooks/useRefillQueue';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from './ui/table';
import { Separator } from './ui/separator';
import { Loader2, CheckCircle2, XCircle, Activity, FileText, TrendingUp, Clock as ClockIcon } from 'lucide-react';

interface DetailPanelProps {
  requestId: string;
}

const DetailPanel: React.FC<DetailPanelProps> = ({ requestId }) => {
  const { data: detailData, isLoading, error } = useRefillDetail(requestId);
  const reviewMutation = useReviewRefill();

  if (isLoading) {
    return <div className="flex items-center justify-center h-full"><Loader2 className="h-8 w-8 animate-spin text-primary" /></div>;
  }

  if (error || !detailData) {
    return (
      <Card className="m-4">
        <CardHeader>
          <CardTitle className="text-destructive">Error</CardTitle>
          <CardDescription>Failed to load refill request details. Please select another request.</CardDescription>
        </CardHeader>
      </Card>
    );
  }

  const { request, patient_data, protocols_checked } = detailData;
  const patientName = `${patient_data.first_name} ${patient_data.last_name}`;
  const aiDecision = request.ai_decision || 'Pending';
  const aiReason = request.ai_reason || 'No reason provided';
  const aiConfidence = request.ai_confidence !== null ? `${Math.round(request.ai_confidence)}%` : 'N/A';

  const handleApprove = () => {
    reviewMutation.mutate({ requestId, decision: 'Approve', userId: 'clinical_staff_member' });
  };

  const handleDeny = () => {
    reviewMutation.mutate({ requestId, decision: 'Deny', userId: 'clinical_staff_member' });
  };

  return (
    <div className="flex flex-col h-full p-4 gap-4 overflow-y-auto">
      {/* Header */}
      <div className="flex justify-between items-start">
        <div>
          <h2 className="text-2xl font-bold">{patientName}</h2>
          <p className="text-sm text-muted-foreground">MRN: {patient_data.mrn} | DOB: {new Date(patient_data.dob).toLocaleDateString()}</p>
        </div>
        <div className="text-right">
          <Badge variant={aiDecision === 'Approve' ? 'success' : 'destructive'} className="text-lg px-4 py-2">
            AI: {aiDecision.toUpperCase()}
          </Badge>
        </div>
      </div>

      {/* AI Recommendation */}
      <Card className="border-l-4 border-l-blue-600">
        <CardHeader>
          <CardTitle className="text-xl flex items-center gap-2"><Activity className="h-5 w-5 text-blue-600" />AI Recommendation</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <p className="text-sm font-medium text-muted-foreground mb-1">Confidence</p>
              <p className="text-2xl font-bold text-blue-600 flex items-center gap-2"><TrendingUp className="h-5 w-5" />{aiConfidence}</p>
            </div>
            <div>
              <p className="text-sm font-medium text-muted-foreground mb-1">Status</p>
              <p className="text-lg font-semibold flex items-center gap-2"><ClockIcon className="h-5 w-5" />{request.status.replace('_', ' ')}</p>
            </div>
          </div>
          <Separator />
          <div>
            <p className="text-sm font-semibold text-muted-foreground mb-1">AI Reasoning</p>
            <p className="text-sm p-2 bg-slate-50 rounded-md border">{aiReason}</p>
          </div>
        </CardContent>
      </Card>

      {/* Protocol Checks */}
      <Card>
        <CardHeader>
          <CardTitle className="text-xl flex items-center gap-2"><FileText className="h-5 w-5" />Protocol Compliance</CardTitle>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Requirement</TableHead>
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
                    <Badge variant={check.status.includes('✅') ? 'success' : 'destructive'}>{check.status}</Badge>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      {/* Decision Actions */}
      <Card>
        <CardHeader>
          <CardTitle>Final Decision</CardTitle>
          <CardDescription>Make your clinical determination.</CardDescription>
        </CardHeader>
        <CardContent className="grid grid-cols-2 gap-4">
          <Button className="bg-green-600 hover:bg-green-700 text-white" size="lg" onClick={handleApprove} disabled={reviewMutation.isPending}>
            <CheckCircle2 className="mr-2 h-5 w-5" />Approve
          </Button>
          <Button variant="destructive" size="lg" onClick={handleDeny} disabled={reviewMutation.isPending}>
            <XCircle className="mr-2 h-5 w-5" />Deny
          </Button>
        </CardContent>
      </Card>
    </div>
  );
};

export default DetailPanel;