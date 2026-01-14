/**
 * AuthGuard Component
 * Protects routes by redirecting unauthenticated users to login
 */

"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth-client";

interface AuthGuardProps {
  children: React.ReactNode;
}

/**
 * Wrapper component for protected routes.
 *
 * Usage:
 * ```tsx
 * export default function ProtectedPage() {
 *   return (
 *     <AuthGuard>
 *       <YourContent />
 *     </AuthGuard>
 *   );
 * }
 * ```
 *
 * Features:
 * - Redirects to /login if user not authenticated (FR-006, T034)
 * - Shows loading state while checking authentication
 * - Preserves session across browser refreshes (FR-005, T035)
 */
export function AuthGuard({ children }: AuthGuardProps) {
  const router = useRouter();
  const { user, loading } = useAuth();
  const [isMounted, setIsMounted] = useState(false);

  useEffect(() => {
    // Mark as mounted to prevent server/client mismatch
    setIsMounted(true);
  }, []);

  useEffect(() => {
    // Redirect to login if not authenticated
    if (isMounted && !loading && !user) {
      router.push("/login");
    }
  }, [user, loading, router, isMounted]);

  // Show loading state while checking authentication
  if (loading || !isMounted) {
    return (
      <div
        style={{
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
          minHeight: "100vh",
        }}
      >
        <div>Loading...</div>
      </div>
    );
  }

  // Don't render content if not authenticated
  if (!user) {
    return null;
  }

  // Render protected content
  return <>{children}</>;
}
