export const fetchPosts = async () => {
  const res = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000'}/posts`);
  if (!res.ok) throw new Error('Failed to fetch posts');
  return res.json();
};

export const createPost = async (postData: any) => {
  const res = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000'}/posts`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(postData),
  });
  if (!res.ok) throw new Error('Failed to create post');
  return res.json();
};

export const updatePost = async (postId: string, postData: any) => {
  const res = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000'}/posts/${postId}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(postData),
  });
  if (!res.ok) throw new Error('Failed to update post');
  return res.json();
};

export const deletePost = async (postId: string) => {
  const res = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000'}/posts/${postId}`, {
    method: 'DELETE',
  });
  if (!res.ok) throw new Error('Failed to delete post');
};

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
  const res = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000'}/generate/bulk`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(request),
  });
  if (!res.ok) throw new Error('Failed to generate posts');
  return res.json();
};