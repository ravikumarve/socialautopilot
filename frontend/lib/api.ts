const BASE_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';

// ─── Existing Functions ───────────────────────────────────────────────────────

export const fetchPosts = async () => {
  const res = await fetch(`${BASE_URL}/posts`);
  if (!res.ok) throw new Error('Failed to fetch posts');
  return res.json();
};

export const createPost = async (postData: Record<string, unknown>) => {
  const res = await fetch(`${BASE_URL}/posts`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(postData),
  });
  if (!res.ok) throw new Error('Failed to create post');
  return res.json();
};

export const updatePost = async (postId: string, postData: Record<string, unknown>) => {
  const res = await fetch(`${BASE_URL}/posts/${postId}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(postData),
  });
  if (!res.ok) throw new Error('Failed to update post');
  return res.json();
};

export const deletePost = async (postId: string) => {
  const res = await fetch(`${BASE_URL}/posts/${postId}`, {
    method: 'DELETE',
  });
  if (!res.ok) throw new Error('Failed to delete post');
};

// ─── Bulk Generation ──────────────────────────────────────────────────────────

export type BulkGenerateRequest = {
  platform: 'twitter' | 'linkedin' | 'threads';
  brand_voice: string;
  post_history?: string[];
  days_ahead?: number;
  model?: 'gemini' | 'claude' | 'nim';
};

export type GeneratedPost = {
  id: number;
  platform: string;
  content: string;
  brand_voice: string;
  topic: string;
  status: string;
  scheduled_at: string;
};

export const bulkGeneratePosts = async (request: BulkGenerateRequest): Promise<GeneratedPost[]> => {
  const res = await fetch(`${BASE_URL}/generate/bulk`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(request),
  });
  if (!res.ok) throw new Error('Failed to generate posts');
  return res.json();
};

// ─── Export Functions ─────────────────────────────────────────────────────────

export type ExportFormat = 'csv' | 'json';

interface ExportPostsParams {
  format: ExportFormat;
  status?: string;
  platform?: string;
}

interface ExportScheduleParams {
  platform?: string;
  daysAhead?: number;
}

/**
 * Export posts as a downloadable file (CSV or JSON).
 * Returns a Blob that can be turned into a browser download.
 */
export const exportPosts = async (
  format: ExportFormat,
  status?: string,
  platform?: string
): Promise<Blob> => {
  const params = new URLSearchParams();
  params.set('format', format);
  if (status) params.set('status', status);
  if (platform) params.set('platform', platform);

  const res = await fetch(`${BASE_URL}/export/posts?${params.toString()}`);
  if (!res.ok) throw new Error('Failed to export posts');
  return res.blob();
};

/**
 * Export the posting schedule as a CSV file.
 * Returns a Blob that can be turned into a browser download.
 */
export const exportSchedule = async (
  platform?: string,
  daysAhead?: number
): Promise<Blob> => {
  const params = new URLSearchParams();
  if (platform) params.set('platform', platform);
  if (daysAhead !== undefined) params.set('days_ahead', String(daysAhead));

  const res = await fetch(`${BASE_URL}/export/schedule?${params.toString()}`);
  if (!res.ok) throw new Error('Failed to export schedule');
  return res.blob();
};

export interface AnalyticsExport {
  overview: {
    total_posts: number;
    approval_rate: number;
    platform_distribution: Record<string, number>;
    status_breakdown: Record<string, number>;
  };
  feedback_analysis: {
    total_feedback: number;
    platform_insights: Record<string, { approval_rate: number; total_actions: number }>;
    topic_insights: Record<string, { approval_rate: number; total_actions: number }>;
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
  generated_at: string;
}

/**
 * Export analytics data as JSON.
 * Returns parsed JSON (not a Blob) since analytics is consumed programmatically.
 */
export const exportAnalytics = async (days?: number): Promise<AnalyticsExport> => {
  const params = new URLSearchParams();
  if (days !== undefined) params.set('days', String(days));

  const res = await fetch(`${BASE_URL}/export/analytics?${params.toString()}`);
  if (!res.ok) throw new Error('Failed to export analytics');
  return res.json();
};
