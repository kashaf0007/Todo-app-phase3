'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { isAuthenticated, getAuthToken, getCurrentUser } from '@/lib/auth-client';
import RagChatImproved from './RagChatImproved'; // Adjust the import path as needed

export default function AuthenticatedRagChat() {
  const [isAuthorized, setIsAuthorized] = useState<boolean | null>(null);
  const router = useRouter();

  useEffect(() => {
    // Check authentication status
    if (!isAuthenticated()) {
      // Redirect to login if not authenticated
      router.push('/login');
      return;
    }

    // If authenticated, allow the chat component to render
    setIsAuthorized(true);
  }, [router]);

  if (isAuthorized === null) {
    // Still checking auth status
    return (
      <div className="flex justify-center items-center h-full">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  if (!isAuthorized) {
    // Redirecting to login
    return null;
  }

  // User is authorized, render the chat component
  return <RagChatImproved />;
}