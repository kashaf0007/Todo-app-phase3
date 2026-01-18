'use client';

import { useState, useEffect } from 'react';
import axios from 'axios';

export default function TestApiConnection() {
  const [connectionStatus, setConnectionStatus] = useState<string>('Checking...');
  const [apiResponse, setApiResponse] = useState<any>(null);

  useEffect(() => {
    const testConnection = async () => {
      try {
        const apiUrl = process.env.NEXT_PUBLIC_API_URL;
        if (!apiUrl) {
          setConnectionStatus('API URL not configured');
          return;
        }

        console.log('Testing connection to:', `${apiUrl}/health`);
        
        const response = await axios.get(`${apiUrl}/health`, {
          timeout: 10000, // 10 second timeout
        });
        
        setApiResponse(response.data);
        setConnectionStatus('Connected successfully');
      } catch (error) {
        console.error('Connection test failed:', error);
        setConnectionStatus(`Connection failed: ${error}`);
      }
    };

    testConnection();
  }, []);

  return (
    <div className="p-4 bg-gray-100 rounded-lg">
      <h3 className="font-bold mb-2">API Connection Test</h3>
      <p>Status: {connectionStatus}</p>
      {apiResponse && (
        <pre className="mt-2 text-sm bg-white p-2 rounded">
          {JSON.stringify(apiResponse, null, 2)}
        </pre>
      )}
    </div>
  );
}