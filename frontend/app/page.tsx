'use client';

import { useState, useEffect } from 'react';
import ReviewQueue from '@/components/ReviewQueue';
import BulkGenerateButton from '@/components/BulkGenerateButton';
import AnalyticsPanel from '@/components/AnalyticsPanel';
import { fetchPosts } from '@/lib/api';

export default function Home() {
  const [posts, setPosts] = useState([]);

  useEffect(() => {
    fetchPostsData();
  }, []);

  const fetchPostsData = async () => {
    try {
      const data = await fetchPosts();
      setPosts(data);
    } catch (err) {
      console.error('Failed to fetch posts:', err);
    }
  };

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-4">Social Autopilot Dashboard</h1>
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <BulkGenerateButton onGenerate={fetchPosts} />
          <ReviewQueue posts={posts} onUpdate={fetchPosts} />
        </div>
        <div>
          <AnalyticsPanel />
        </div>
      </div>
    </div>
  );
}