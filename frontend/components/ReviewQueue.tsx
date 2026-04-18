import { useState } from 'react';
import { updatePost } from '@/lib/api';

type Post = {
  id: number;
  platform: string;
  content: string;
  status: string;
  brand_voice: string;
  topic: string;
};

type ReviewQueueProps = {
  posts: Post[];
  onUpdate: () => void;
};

export default function ReviewQueue({ posts, onUpdate }: ReviewQueueProps) {
  const [editingPostId, setEditingPostId] = useState<number | null>(null);
  const [editedContent, setEditedContent] = useState('');

  const handleApprove = async (postId: number) => {
    try {
      await updatePost(postId.toString(), { status: 'approved' });
      onUpdate();
    } catch (err) {
      console.error('Failed to approve post:', err);
    }
  };

  const handleReject = async (postId: number) => {
    try {
      await updatePost(postId.toString(), { status: 'rejected' });
      onUpdate();
    } catch (err) {
      console.error('Failed to reject post:', err);
    }
  };

  const handleEdit = (postId: number, content: string) => {
    setEditingPostId(postId);
    setEditedContent(content);
  };

  const handleSaveEdit = async (postId: number) => {
    try {
      await updatePost(postId.toString(), { content: editedContent, status: 'draft' });
      setEditingPostId(null);
      onUpdate();
    } catch (err) {
      console.error('Failed to save edit:', err);
    }
  };

  const handleCancelEdit = () => {
    setEditingPostId(null);
    setEditedContent('');
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h2 className="text-xl font-bold mb-4">Review Queue</h2>
      {posts.length === 0 ? (
        <p className="text-gray-500">No posts awaiting review</p>
      ) : (
        <div className="space-y-4">
          {posts.map((post) => (
            <div key={post.id} className="border rounded-lg p-4">
              {!editingPostId || editingPostId !== post.id ? (
                <>
                  <p className="text-sm text-gray-600 mb-2">
                    Platform: {post.platform} | Topic: {post.topic}
                  </p>
                  <p className="mb-3">{post.content}</p>
                  <div className="flex space-x-3">
                    <button
                      onClick={() => handleApprove(post.id)}
                      className="bg-green-500 text-white px-3 py-1 rounded hover:bg-green-600"
                    >
                      Approve
                    </button>
                    <button
                      onClick={() => handleReject(post.id)}
                      className="bg-red-500 text-white px-3 py-1 rounded hover:bg-red-600"
                    >
                      Reject
                    </button>
                    <button
                      onClick={() => handleEdit(post.id, post.content)}
                      className="bg-blue-500 text-white px-3 py-1 rounded hover:bg-blue-600"
                    >
                      Edit
                    </button>
                  </div>
                </>
              ) : (
                <>
                  <textarea
                    value={editedContent}
                    onChange={(e) => setEditedContent(e.target.value)}
                    className="w-full mb-3 h-32 p-2 border rounded"
                    placeholder="Edit post content..."
                  />
                  <div className="flex space-x-3">
                    <button
                      onClick={() => handleSaveEdit(post.id)}
                      className="bg-green-500 text-white px-3 py-1 rounded hover:bg-green-600"
                    >
                      Save
                    </button>
                    <button
                      onClick={handleCancelEdit}
                      className="bg-gray-500 text-white px-3 py-1 rounded hover:bg-gray-600"
                    >
                      Cancel
                    </button>
                  </div>
                </>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}