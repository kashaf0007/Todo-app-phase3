'use client';

import dynamic from 'next/dynamic';
import { Suspense } from 'react';
import { useRouter } from 'next/navigation';

// Dynamically import the improved chat component with no SSR
const ImprovedChatComponent = dynamic(() => import('@/components/ImprovedChatComponent'), {
  ssr: false,
  loading: () => (
    <div className="flex justify-center items-center h-screen">
      <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-indigo-500"></div>
    </div>
  )
});

export default function ChatPage() {
  return (
    <div className="min-h-screen bg-gray-50">
      <Suspense fallback={
        <div className="flex justify-center items-center h-screen">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-indigo-500"></div>
        </div>
      }>
        <ImprovedChatComponent />
      </Suspense>
    </div>
  );
}