'use client';

import { useState, useRef } from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import ClientNavigation from '../components/ClientNavigation';
import TaskEditPageClient from '../components/TaskEditPageClient';
import FloatingChatButton from '../components/FloatingChatButtonNew';

export default function AppProviderWithTaskEdit() {
  const queryClientRef = useRef<QueryClient | null>(null);

  if (!queryClientRef.current) {
    queryClientRef.current = new QueryClient({
      defaultOptions: {
        queries: {
          staleTime: 5000, // 5 seconds
          retry: 1,
        },
      },
    });
  }

  return (
    <QueryClientProvider client={queryClientRef.current}>
      <div className="app-container relative">
        <ClientNavigation />
        <main>
          <TaskEditPageClient />
        </main>
        <FloatingChatButton />
      </div>
    </QueryClientProvider>
  );
}