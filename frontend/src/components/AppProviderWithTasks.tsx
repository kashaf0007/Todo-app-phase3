'use client';

import { useState, useRef, ReactNode } from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import ClientNavigation from '../components/ClientNavigation';
import TasksPageClient from '../components/TasksPageClient';
import FloatingChatButton from '../components/FloatingChatButtonNew';

export default function AppProviderWithTasks() {
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
      <div className="app-container min-h-screen flex flex-col relative">
        <ClientNavigation />
        <main className="flex-grow">
          <TasksPageClient />
        </main>
        <FloatingChatButton />
      </div>
    </QueryClientProvider>
  );
}