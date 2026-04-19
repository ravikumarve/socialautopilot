'use client';

import ReviewQueue from '@/components/ReviewQueue';
import BulkGenerateButton from '@/components/BulkGenerateButton';
import AnalyticsPanel from '@/components/AnalyticsPanel';
import ExportButton from '@/components/ExportButton';
import usePolling from '@/lib/usePolling';
import { fetchPosts } from '@/lib/api';

type Post = {
  id: number;
  platform: string;
  content: string;
  status: string;
  brand_voice: string;
  topic: string;
};

export default function Home() {
  const { data: posts, loading, error, refetch } = usePolling<Post[]>(fetchPosts, 5000);

  return (
    <div className="p-6">
      {/* Dashboard Header */}
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Social Autopilot Dashboard</h1>
          {loading && (
            <p className="mt-1 text-sm text-gray-500">Loading posts…</p>
          )}
          {error && (
            <p className="mt-1 text-sm text-red-600" role="alert">
              {error}
            </p>
          )}
          {!loading && posts && (
            <p className="mt-1 text-sm text-gray-500">
              {posts.length} post{posts.length !== 1 ? 's' : ''} in queue • Auto-refreshing
            </p>
          )}
        </div>
        <ExportButton />
      </div>

      {/* Main Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <BulkGenerateButton onGenerate={refetch} />
          <ReviewQueue posts={posts ?? []} onUpdate={refetch} />
        </div>
        <div>
          <AnalyticsPanel />
        </div>
      </div>
    </div>
  );
}
