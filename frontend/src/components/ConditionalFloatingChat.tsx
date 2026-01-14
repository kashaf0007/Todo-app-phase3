"use client";

import { ReactNode, useEffect } from 'react';
import { usePathname } from 'next/navigation';
import { useAuth } from '@/lib/auth-client';
import { useRouter } from 'next/navigation';
import FloatingChatButton from '@/components/FloatingChatButtonNew';

interface ConditionalFloatingChatProps {
  children: ReactNode;
}

export default function ConditionalFloatingChat({ children }: ConditionalFloatingChatProps) {
  const pathname = usePathname();
  const { user, loading } = useAuth();
  const router = useRouter();

  // Don't show on login/signup pages
  const shouldShowChatButton = pathname && !pathname.includes('/login') && !pathname.includes('/signup');

  // Redirect to login if not authenticated and not on public pages
  useEffect(() => {
    if (!loading && !user && shouldShowChatButton) {
      router.push('/login');
    }
  }, [user, loading, router, shouldShowChatButton]);

  // Show loading while checking auth status
  if (loading && shouldShowChatButton) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-indigo-500"></div>
      </div>
    );
  }

  // If not authenticated and on protected route, don't render anything (redirect will happen)
  if (!user && shouldShowChatButton) {
    return null;
  }

  return (
    <div className="relative min-h-screen">
      {children}
      {shouldShowChatButton && <FloatingChatButton />}
    </div>
  );
}