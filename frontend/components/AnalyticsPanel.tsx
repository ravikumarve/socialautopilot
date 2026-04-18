import { useEffect, useState } from 'react';

type AnalyticsPanelProps = {};

export default function AnalyticsPanel() {
  const [insights, setInsights] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchInsights();
  }, []);

  const fetchInsights = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000'}/analytics/insights`);
      if (!res.ok) throw new Error('Failed to fetch insights');
      const data = await res.json();
      setInsights(data);
    } catch (err) {
      setError('Failed to load insights');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6">
        <h2 className="text-xl font-bold mb-4">Analytics Insights</h2>
        <p className="text-gray-500">Loading insights...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6">
        <h2 className="text-xl font-bold mb-4">Analytics Insights</h2>
        <p className="text-red-600">{error}</p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h2 className="text-xl font-bold mb-4">Analytics Insights</h2>
      {!insights ? (
        <p className="text-gray-500">No data available</p>
      ) : (
        <div className="space-y-4">
          <div className="text-sm">
            <p><strong>Total Posts:</strong> {insights.total_posts}</p>
            <p><strong>Approved Posts:</strong> {insights.approved_posts}</p>
            <p><strong>Rejected Posts:</strong> {insights.rejected_posts}</p>
            <p><strong>Approval Rate:</strong> {(insights.approval_rate * 100).toFixed(1)}%</p>
          </div>
          <div className="mt-4 p-3 bg-blue-50 rounded">
            <p className="font-medium mb-2">Key Insight:</p>
            <p>{insights.insight}</p>
          </div>
        </div>
      )}
    </div>
  );
}