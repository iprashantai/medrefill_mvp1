/**
 * Main App component with routing and React Query setup.
 * Enterprise-grade MedRefills AI platform.
 */
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import RefillQueuePage from './pages/RefillQueuePage'
import RefillDetailPage from './pages/RefillDetailPage'

// Create a query client with enterprise-grade configuration
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
      staleTime: 30000, // 30 seconds
    },
  },
})

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<RefillQueuePage />} />
          <Route path="/request/:requestId" element={<RefillDetailPage />} />
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  )
}

export default App
