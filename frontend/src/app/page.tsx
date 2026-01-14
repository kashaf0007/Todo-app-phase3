/**
 * Landing Page
 * Redirects based on authentication status
 */

"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth-client";

export default function HomePage() {
  const router = useRouter();
  const { user, loading } = useAuth();
  const [isMounted, setIsMounted] = useState(false);

  useEffect(() => {
    // Mark as mounted to prevent server/client mismatch
    setIsMounted(true);
  }, []);

  useEffect(() => {
    if (isMounted && !loading) {
      if (user) {
        // User authenticated - redirect to tasks
        router.push("/tasks");
      } else {
        // User not authenticated - redirect to login
        router.push("/login");
      }
    }
  }, [user, loading, router, isMounted]);

  // Show loading while checking authentication
  return (
    <div className="task-list-loading">
      <div>Loading...</div>
    </div>
  );
}