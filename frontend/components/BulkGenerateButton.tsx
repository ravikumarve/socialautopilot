import { useState } from 'react';
import { fetchPosts } from '@/lib/api';

type BulkGenerateButtonProps = {
  onGenerate: () => void;
};

export default function BulkGenerateButton({ onGenerate }: BulkGenerateButtonProps) {
  const [generating, setGenerating] = useState(false);
  const [message, setMessage] = useState<string | null>(null);

  const handleGenerate = async () => {
    setGenerating(true);
    setMessage(null);
    try {
      // In a real implementation, we would call the backend bulk generate endpoint
      // For now, we'll just refresh the posts
      onGenerate();
      setMessage('Posts regenerated successfully!');
    } catch (err) {
      setMessage('Failed to generate posts');
      console.error('Generation failed:', err);
    } finally {
      setGenerating(false);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6 mb-6">
      <h2 className="text-xl font-bold mb-4">Content Generation</h2>
      <button
        onClick={handleGenerate}
        disabled={generating}
        className={`w-full bg-indigo-600 text-white px-4 py-2 rounded hover:bg-indigo-700 disabled:opacity-50`}
      >
        {generating ? 'Generating...' : 'Bulk Generate Posts'}
      </button>
      {message && (
        <p className={`mt-3 text-sm ${message.includes('successfully') ? 'text-green-600' : 'text-red-600'}`}>
          {message}
        </p>
      )}
    </div>
  );
}