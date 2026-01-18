// pages/api-test.tsx
'use client';

import { useState } from 'react';
import axios from 'axios';
import { getAuthToken, getCurrentUser } from '@/lib/auth-client';

export default function ApiTestPage() {
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const testApi = async () => {
    setLoading(true);
    try {
      // Check auth status
      const token = getAuthToken();
      const user = getCurrentUser();

      console.log('Current token:', token);
      console.log('Current user:', user);

      if (!token) {
        setResult({ error: 'No authentication token found. Please log in first.' });
        setLoading(false);
        return;
      }

      if (!user) {
        setResult({ error: 'No user data found. Please log in first.' });
        setLoading(false);
        return;
      }

      // Test the health endpoint
      const response = await axios.get(`${process.env.NEXT_PUBLIC_API_URL}/health`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      setResult({
        healthCheck: response.data,
        userId: user.id,
        tokenPresent: !!token
      });
    } catch (error) {
      console.error('API test error:', error);
      setResult({ error: error.message });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">API Test Page</h1>
      <button
        onClick={testApi}
        disabled={loading}
        className="bg-blue-500 text-white px-4 py-2 rounded disabled:opacity-50"
      >
        {loading ? 'Testing...' : 'Test API Connection'}
      </button>

      {result && (
        <div className="mt-4 p-4 bg-gray-100 rounded">
          <h2 className="font-bold mb-2">Result:</h2>
          <pre>{JSON.stringify(result, null, 2)}</pre>
        </div>
      )}
    </div>
  );
}