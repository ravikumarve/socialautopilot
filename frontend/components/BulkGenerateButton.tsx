'use client';

import { useState } from 'react';
import { bulkGeneratePosts, type GeneratedPost } from '@/lib/api';

type BulkGenerateButtonProps = {
  onGenerate?: () => void;
};

type GenerationConfig = {
  platform: 'twitter' | 'linkedin' | 'threads';
  brand_voice: string;
  days_ahead: number;
  model?: 'gemini' | 'claude' | 'nim';
  post_history?: string[];
};

export default function BulkGenerateButton({ onGenerate }: BulkGenerateButtonProps) {
  const [isConfigOpen, setIsConfigOpen] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);
  const [generatedPosts, setGeneratedPosts] = useState<GeneratedPost[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [expandedPostId, setExpandedPostId] = useState<number | null>(null);

  const [config, setConfig] = useState<GenerationConfig>({
    platform: 'twitter',
    brand_voice: '',
    days_ahead: 7,
    model: 'gemini',
    post_history: [],
  });

  const [postHistoryText, setPostHistoryText] = useState('');

  const handleConfigChange = (field: keyof GenerationConfig, value: any) => {
    setConfig((prev) => ({ ...prev, [field]: value }));
  };

  const handleGenerate = async () => {
    if (!config.brand_voice.trim()) {
      setError('Please enter a brand voice');
      return;
    }

    setIsGenerating(true);
    setError(null);
    setGeneratedPosts([]);

    try {
      // Parse post history if provided
      const postHistoryArray = postHistoryText.trim()
        ? postHistoryText.split('\n').filter((line) => line.trim())
        : undefined;

      const request = {
        ...config,
        post_history: postHistoryArray,
      };

      const posts = await bulkGeneratePosts(request);
      setGeneratedPosts(posts);
      setIsConfigOpen(false);

      // Refresh the review queue
      if (onGenerate) {
        onGenerate();
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to generate posts');
      console.error('Bulk generation error:', err);
    } finally {
      setIsGenerating(false);
    }
  };

  const togglePostExpansion = (postId: number) => {
    setExpandedPostId(expandedPostId === postId ? null : postId);
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const getPlatformIcon = (platform: string) => {
    switch (platform) {
      case 'twitter':
        return '🐦';
      case 'linkedin':
        return '💼';
      case 'threads':
        return '🧵';
      default:
        return '📱';
    }
  };

  const getPlatformColor = (platform: string) => {
    switch (platform) {
      case 'twitter':
        return 'bg-blue-50 border-blue-200';
      case 'linkedin':
        return 'bg-blue-50 border-blue-200';
      case 'threads':
        return 'bg-purple-50 border-purple-200';
      default:
        return 'bg-gray-50 border-gray-200';
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6 mb-6">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-bold">Bulk Generate Posts</h2>
        <button
          onClick={() => setIsConfigOpen(!isConfigOpen)}
          className="bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700 transition-colors focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2"
          aria-expanded={isConfigOpen}
          aria-controls="bulk-config-form"
        >
          {isConfigOpen ? 'Cancel' : 'Configure & Generate'}
        </button>
      </div>

      {error && (
        <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg" role="alert">
          <p className="text-red-800 font-medium">Error</p>
          <p className="text-red-700 text-sm">{error}</p>
        </div>
      )}

      {isConfigOpen && (
        <div id="bulk-config-form" className="space-y-6">
          {/* Platform Selector */}
          <div>
            <label htmlFor="platform" className="block text-sm font-medium text-gray-700 mb-2">
              Platform
            </label>
            <select
              id="platform"
              value={config.platform}
              onChange={(e) => handleConfigChange('platform', e.target.value as any)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              aria-describedby="platform-description"
            >
              <option value="twitter">Twitter/X</option>
              <option value="linkedin">LinkedIn</option>
              <option value="threads">Threads</option>
            </select>
            <p id="platform-description" className="mt-1 text-sm text-gray-500">
              Select the social media platform for generated posts
            </p>
          </div>

          {/* Brand Voice Input */}
          <div>
            <label htmlFor="brand-voice" className="block text-sm font-medium text-gray-700 mb-2">
              Brand Voice <span className="text-red-500">*</span>
            </label>
            <input
              id="brand-voice"
              type="text"
              value={config.brand_voice}
              onChange={(e) => handleConfigChange('brand_voice', e.target.value)}
              placeholder="e.g., Professional, Casual, Witty"
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              aria-required="true"
              aria-describedby="brand-voice-description"
            />
            <p id="brand-voice-description" className="mt-1 text-sm text-gray-500">
              Describe the tone and style for your posts
            </p>
          </div>

          {/* Days Ahead Slider */}
          <div>
            <label htmlFor="days-ahead" className="block text-sm font-medium text-gray-700 mb-2">
              Days Ahead: {config.days_ahead}
            </label>
            <div className="flex items-center space-x-4">
              <input
                id="days-ahead"
                type="range"
                min="1"
                max="30"
                value={config.days_ahead}
                onChange={(e) => handleConfigChange('days_ahead', parseInt(e.target.value))}
                className="flex-1 h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer focus:outline-none focus:ring-2 focus:ring-indigo-500"
                aria-describedby="days-ahead-description"
              />
              <input
                type="number"
                min="1"
                max="30"
                value={config.days_ahead}
                onChange={(e) => handleConfigChange('days_ahead', parseInt(e.target.value) || 1)}
                className="w-20 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                aria-label="Days ahead number input"
              />
            </div>
            <p id="days-ahead-description" className="mt-1 text-sm text-gray-500">
              Number of days to generate posts for (1-30)
            </p>
          </div>

          {/* Model Selector */}
          <div>
            <label htmlFor="model" className="block text-sm font-medium text-gray-700 mb-2">
              AI Model (Optional)
            </label>
            <select
              id="model"
              value={config.model || ''}
              onChange={(e) => handleConfigChange('model', e.target.value as any)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              aria-describedby="model-description"
            >
              <option value="">Default</option>
              <option value="gemini">Gemini</option>
              <option value="claude">Claude</option>
              <option value="nim">NVIDIA NIM</option>
            </select>
            <p id="model-description" className="mt-1 text-sm text-gray-500">
              Select the AI model for content generation
            </p>
          </div>

          {/* Post History Input */}
          <div>
            <label htmlFor="post-history" className="block text-sm font-medium text-gray-700 mb-2">
              Post History (Optional)
            </label>
            <textarea
              id="post-history"
              value={postHistoryText}
              onChange={(e) => setPostHistoryText(e.target.value)}
              placeholder="Paste your last 30 posts here (one per line) for better context..."
              rows={5}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent resize-none"
              aria-describedby="post-history-description"
            />
            <p id="post-history-description" className="mt-1 text-sm text-gray-500">
              Provide your recent posts for better personalization (one per line)
            </p>
          </div>

          {/* Generate Button */}
          <button
            onClick={handleGenerate}
            disabled={isGenerating || !config.brand_voice.trim()}
            className="w-full bg-indigo-600 text-white px-6 py-3 rounded-lg hover:bg-indigo-700 transition-colors disabled:bg-gray-400 disabled:cursor-not-allowed focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2"
            aria-busy={isGenerating}
          >
            {isGenerating ? (
              <span className="flex items-center justify-center">
                <svg
                  className="animate-spin -ml-1 mr-3 h-5 w-5 text-white"
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 24 24"
                  aria-hidden="true"
                >
                  <circle
                    className="opacity-25"
                    cx="12"
                    cy="12"
                    r="10"
                    stroke="currentColor"
                    strokeWidth="4"
                  />
                  <path
                    className="opacity-75"
                    fill="currentColor"
                    d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                  />
                </svg>
                Generating Posts...
              </span>
            ) : (
              `Generate ${config.days_ahead} Post${config.days_ahead > 1 ? 's' : ''}`
            )}
          </button>
        </div>
      )}

      {/* Generated Posts Results */}
      {generatedPosts.length > 0 && (
        <div className="mt-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900">
              Generated Posts ({generatedPosts.length})
            </h3>
            <div className="flex items-center space-x-2">
              <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                {generatedPosts.filter((p) => p.status === 'draft').length} Draft
              </span>
              <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                {generatedPosts.filter((p) => p.status === 'approved').length} Approved
              </span>
            </div>
          </div>

          <div className="space-y-4">
            {generatedPosts.map((post) => (
              <div
                key={post.id}
                className={`border rounded-lg p-4 ${getPlatformColor(post.platform)} transition-all hover:shadow-md`}
              >
                <div className="flex items-start justify-between mb-3">
                  <div className="flex items-center space-x-3">
                    <span className="text-2xl" aria-hidden="true">
                      {getPlatformIcon(post.platform)}
                    </span>
                    <div>
                      <p className="font-medium text-gray-900 capitalize">{post.platform}</p>
                      <p className="text-sm text-gray-600">
                        Topic: {post.topic || 'N/A'}
                      </p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="text-sm text-gray-600">
                      Scheduled: {formatDate(post.scheduled_at)}
                    </p>
                    <span
                      className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${
                        post.status === 'draft'
                          ? 'bg-yellow-100 text-yellow-800'
                          : post.status === 'approved'
                          ? 'bg-green-100 text-green-800'
                          : 'bg-red-100 text-red-800'
                      }`}
                    >
                      {post.status}
                    </span>
                  </div>
                </div>

                <div className="relative">
                  <p
                    className={`text-gray-700 ${
                      expandedPostId === post.id ? '' : 'line-clamp-3'
                    }`}
                  >
                    {post.content}
                  </p>
                  {post.content.length > 150 && (
                    <button
                      onClick={() => togglePostExpansion(post.id)}
                      className="mt-2 text-indigo-600 hover:text-indigo-800 text-sm font-medium focus:outline-none focus:underline"
                      aria-expanded={expandedPostId === post.id}
                      aria-controls={`post-content-${post.id}`}
                    >
                      {expandedPostId === post.id ? 'Show less' : 'Show more'}
                    </button>
                  )}
                </div>

                <div className="mt-3 pt-3 border-t border-gray-200">
                  <p className="text-xs text-gray-500">
                    Brand Voice: {post.brand_voice} • ID: {post.id}
                  </p>
                </div>
              </div>
            ))}
          </div>

          <div className="mt-4 p-4 bg-green-50 border border-green-200 rounded-lg">
            <p className="text-green-800 text-sm">
              ✅ Successfully generated {generatedPosts.length} post{generatedPosts.length > 1 ? 's' : ''}! 
              Check the Review Queue below to approve or edit them.
            </p>
          </div>
        </div>
      )}

      {isGenerating && (
        <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
          <div className="flex items-center space-x-3">
            <svg
              className="animate-spin h-5 w-5 text-blue-600"
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
              aria-hidden="true"
            >
              <circle
                className="opacity-25"
                cx="12"
                cy="12"
                r="10"
                stroke="currentColor"
                strokeWidth="4"
              />
              <path
                className="opacity-75"
                fill="currentColor"
                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
              />
            </svg>
            <p className="text-blue-800 text-sm">
              Generating {config.days_ahead} post{config.days_ahead > 1 ? 's' : ''} for {config.platform}...
            </p>
          </div>
        </div>
      )}
    </div>
  );
}
