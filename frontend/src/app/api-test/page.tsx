"use client";

import { useState } from "react";

interface TestResult {
  success: boolean;
  data?: any;
  error?: string;
}

export default function ApiTestPage() {
  const [testResult, setTestResult] = useState<TestResult | null>(null);
  const [loading, setLoading] = useState(false);

  const testApiConnection = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/health');
      const data = await response.json();
      setTestResult({ success: true, data });
    } catch (error) {
      setTestResult({ success: false, error: error.message });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-4 max-w-2xl mx-auto">
      <h1 className="text-2xl font-bold mb-4">API Connection Test</h1>

      <div className="mb-4">
        <button
          onClick={testApiConnection}
          disabled={loading}
          className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded disabled:opacity-50"
        >
          {loading ? 'Testing...' : 'Test API Connection'}
        </button>
      </div>

      {testResult && (
        <div className={`p-4 rounded ${testResult.success ? 'bg-green-100' : 'bg-red-100'}`}>
          <h2 className="text-lg font-semibold mb-2">Test Result:</h2>
          <pre className="whitespace-pre-wrap">
            {JSON.stringify(testResult, null, 2)}
          </pre>
        </div>
      )}

      <div className="mt-6 bg-yellow-50 p-4 rounded border border-yellow-200">
        <h3 className="font-semibold mb-2">Important:</h3>
        <p>
          For your frontend to work properly, you need to ensure your backend API is accessible.
          If API calls are failing, check that:
        </p>
        <ul className="list-disc pl-5 mt-2">
          <li>Your backend is deployed and publicly accessible</li>
          <li>The NEXT_PUBLIC_API_URL environment variable is set correctly</li>
          <li>Your backend allows CORS requests from your frontend domain</li>
        </ul>
      </div>
    </div>
  );
}