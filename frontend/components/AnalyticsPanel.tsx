import { useEffect, useState } from 'react';

type AnalyticsPanelProps = {};

interface AnalyticsData {
  health_score: string;
  health_description: string;
  overview: {
    total_posts: number;
    approval_rate: number;
    platform_distribution: Record<string, number>;
    status_breakdown: Record<string, number>;
  };
  feedback_analysis: {
    total_feedback: number;
    platform_insights: Record<string, any>;
    topic_insights: Record<string, any>;
  };
  performance_trends: {
    trend_analysis: {
      direction: string;
      change_percentage: number;
    };
  };
  recommendations: {
    top_performing_topics: Array<{ topic: string; approval_rate: number }>;
    strategic_recommendations: Array<{
      type: string;
      priority: string;
      insight: string;
      action: string;
    }>;
  };
  next_steps: string[];
}

export default function AnalyticsPanel() {
  const [analyticsData, setAnalyticsData] = useState<AnalyticsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'overview' | 'feedback' | 'trends' | 'recommendations'>('overview');

  useEffect(() => {
    fetchAnalytics();
  }, []);

  const fetchAnalytics = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000'}/analytics/insights`);
      if (!res.ok) throw new Error('Failed to fetch analytics');
      const data = await res.json();
      setAnalyticsData(data);
    } catch (err) {
      setError('Failed to load analytics data');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const getHealthScoreColor = (score: string) => {
    switch (score) {
      case 'excellent': return 'bg-green-100 text-green-800';
      case 'good': return 'bg-blue-100 text-blue-800';
      case 'fair': return 'bg-yellow-100 text-yellow-800';
      case 'poor': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high': return 'bg-red-100 text-red-800';
      case 'medium': return 'bg-yellow-100 text-yellow-800';
      case 'low': return 'bg-green-100 text-green-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6">
        <h2 className="text-xl font-bold mb-4">📊 Analytics Dashboard</h2>
        <div className="flex items-center justify-center py-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6">
        <h2 className="text-xl font-bold mb-4">📊 Analytics Dashboard</h2>
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-red-600">{error}</p>
          <button
            onClick={fetchAnalytics}
            className="mt-2 px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  if (!analyticsData) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6">
        <h2 className="text-xl font-bold mb-4">📊 Analytics Dashboard</h2>
        <p className="text-gray-500">No analytics data available</p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-bold">📊 Analytics Dashboard</h2>
        <button
          onClick={fetchAnalytics}
          className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 text-sm"
        >
          Refresh
        </button>
      </div>

      {/* Health Score */}
      <div className={`mb-6 p-4 rounded-lg ${getHealthScoreColor(analyticsData.health_score)}`}>
        <div className="flex items-center justify-between">
          <div>
            <p className="font-semibold text-lg">Health Score: {analyticsData.health_score.toUpperCase()}</p>
            <p className="text-sm opacity-90">{analyticsData.health_description}</p>
          </div>
          <div className="text-3xl font-bold">
            {analyticsData.overview.approval_rate.toFixed(1)}%
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200 mb-4">
        <nav className="flex space-x-4">
          {['overview', 'feedback', 'trends', 'recommendations'].map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab as any)}
              className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${
                activeTab === tab
                  ? 'border-blue-600 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              {tab.charAt(0).toUpperCase() + tab.slice(1)}
            </button>
          ))}
        </nav>
      </div>

      {/* Tab Content */}
      <div className="space-y-4">
        {activeTab === 'overview' && (
          <div className="space-y-4">
            {/* Overview Stats */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="bg-blue-50 p-4 rounded-lg">
                <p className="text-sm text-gray-600">Total Posts</p>
                <p className="text-2xl font-bold text-blue-600">{analyticsData.overview.total_posts}</p>
              </div>
              <div className="bg-green-50 p-4 rounded-lg">
                <p className="text-sm text-gray-600">Approval Rate</p>
                <p className="text-2xl font-bold text-green-600">{analyticsData.overview.approval_rate.toFixed(1)}%</p>
              </div>
              <div className="bg-purple-50 p-4 rounded-lg">
                <p className="text-sm text-gray-600">Total Feedback</p>
                <p className="text-2xl font-bold text-purple-600">{analyticsData.feedback_analysis.total_feedback}</p>
              </div>
              <div className="bg-orange-50 p-4 rounded-lg">
                <p className="text-sm text-gray-600">Active Platforms</p>
                <p className="text-2xl font-bold text-orange-600">{Object.keys(analyticsData.overview.platform_distribution).length}</p>
              </div>
            </div>

            {/* Platform Distribution */}
            <div className="bg-gray-50 p-4 rounded-lg">
              <h3 className="font-semibold mb-3">Platform Distribution</h3>
              <div className="space-y-2">
                {Object.entries(analyticsData.overview.platform_distribution).map(([platform, count]) => (
                  <div key={platform} className="flex items-center justify-between">
                    <span className="capitalize">{platform}</span>
                    <span className="font-semibold">{count} posts</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Status Breakdown */}
            <div className="bg-gray-50 p-4 rounded-lg">
              <h3 className="font-semibold mb-3">Status Breakdown</h3>
              <div className="space-y-2">
                {Object.entries(analyticsData.overview.status_breakdown).map(([status, count]) => (
                  <div key={status} className="flex items-center justify-between">
                    <span className="capitalize">{status}</span>
                    <span className="font-semibold">{count} posts</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {activeTab === 'feedback' && (
          <div className="space-y-4">
            {/* Platform Insights */}
            <div className="bg-gray-50 p-4 rounded-lg">
              <h3 className="font-semibold mb-3">Platform Performance</h3>
              <div className="space-y-3">
                {Object.entries(analyticsData.feedback_analysis.platform_insights).map(([platform, insights]) => (
                  <div key={platform} className="border-l-4 border-blue-500 pl-4">
                    <div className="flex items-center justify-between">
                      <span className="font-semibold capitalize">{platform}</span>
                      <span className={`px-2 py-1 rounded text-xs ${
                        insights.approval_rate >= 70 ? 'bg-green-100 text-green-800' :
                        insights.approval_rate >= 50 ? 'bg-yellow-100 text-yellow-800' :
                        'bg-red-100 text-red-800'
                      }`}>
                        {insights.approval_rate.toFixed(1)}% approval
                      </span>
                    </div>
                    <p className="text-sm text-gray-600 mt-1">
                      {insights.total_actions} total actions
                    </p>
                  </div>
                ))}
              </div>
            </div>

            {/* Topic Insights */}
            <div className="bg-gray-50 p-4 rounded-lg">
              <h3 className="font-semibold mb-3">Topic Performance</h3>
              <div className="space-y-3">
                {Object.entries(analyticsData.feedback_analysis.topic_insights).slice(0, 5).map(([topic, insights]) => (
                  <div key={topic} className="border-l-4 border-green-500 pl-4">
                    <div className="flex items-center justify-between">
                      <span className="font-semibold">{topic}</span>
                      <span className={`px-2 py-1 rounded text-xs ${
                        insights.approval_rate >= 70 ? 'bg-green-100 text-green-800' :
                        insights.approval_rate >= 50 ? 'bg-yellow-100 text-yellow-800' :
                        'bg-red-100 text-red-800'
                      }`}>
                        {insights.approval_rate.toFixed(1)}% approval
                      </span>
                    </div>
                    <p className="text-sm text-gray-600 mt-1">
                      {insights.total_actions} total actions
                    </p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {activeTab === 'trends' && (
          <div className="space-y-4">
            {/* Trend Analysis */}
            <div className={`p-4 rounded-lg ${
              analyticsData.performance_trends.trend_analysis.direction === 'improving' ? 'bg-green-50' :
              analyticsData.performance_trends.trend_analysis.direction === 'declining' ? 'bg-red-50' :
              'bg-gray-50'
            }`}>
              <h3 className="font-semibold mb-2">Performance Trend</h3>
              <div className="flex items-center space-x-4">
                <span className={`text-2xl font-bold ${
                  analyticsData.performance_trends.trend_analysis.direction === 'improving' ? 'text-green-600' :
                  analyticsData.performance_trends.trend_analysis.direction === 'declining' ? 'text-red-600' :
                  'text-gray-600'
                }`}>
                  {analyticsData.performance_trends.trend_analysis.direction === 'improving' ? '↑' :
                   analyticsData.performance_trends.trend_analysis.direction === 'declining' ? '↓' : '→'}
                  {Math.abs(analyticsData.performance_trends.trend_analysis.change_percentage)}%
                </span>
                <span className="text-gray-600">
                  {analyticsData.performance_trends.trend_analysis.direction === 'improving' ? 'Improving' :
                   analyticsData.performance_trends.trend_analysis.direction === 'declining' ? 'Declining' : 'Stable'}
                </span>
              </div>
            </div>

            {/* Next Steps */}
            <div className="bg-blue-50 p-4 rounded-lg">
              <h3 className="font-semibold mb-3">Recommended Next Steps</h3>
              <ul className="space-y-2">
                {analyticsData.next_steps.map((step, index) => (
                  <li key={index} className="flex items-start">
                    <span className="text-blue-600 mr-2">•</span>
                    <span className="text-sm">{step}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        )}

        {activeTab === 'recommendations' && (
          <div className="space-y-4">
            {/* Top Performing Topics */}
            <div className="bg-gray-50 p-4 rounded-lg">
              <h3 className="font-semibold mb-3">🏆 Top Performing Topics</h3>
              <div className="space-y-2">
                {analyticsData.recommendations.top_performing_topics.map((topic, index) => (
                  <div key={index} className="flex items-center justify-between bg-white p-3 rounded">
                    <span className="font-medium">{topic.topic}</span>
                    <span className="text-green-600 font-semibold">{topic.approval_rate.toFixed(1)}%</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Strategic Recommendations */}
            <div className="bg-gray-50 p-4 rounded-lg">
              <h3 className="font-semibold mb-3">💡 Strategic Recommendations</h3>
              <div className="space-y-3">
                {analyticsData.recommendations.strategic_recommendations.map((rec, index) => (
                  <div key={index} className="bg-white p-4 rounded border-l-4 border-blue-500">
                    <div className="flex items-center justify-between mb-2">
                      <span className="font-medium capitalize">{rec.type.replace('_', ' ')}</span>
                      <span className={`px-2 py-1 rounded text-xs ${getPriorityColor(rec.priority)}`}>
                        {rec.priority}
                      </span>
                    </div>
                    <p className="text-sm text-gray-600 mb-2">{rec.insight}</p>
                    <p className="text-sm font-medium text-blue-600">{rec.action}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}