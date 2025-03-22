// components/ProtectedRoute.tsx
"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useUser } from "@/contexts/UserContext";
import { Loader2 } from "lucide-react";

interface ProtectedRouteProps {
  children: React.ReactNode;
}

export default function ProtectedRoute({ children }: ProtectedRouteProps) {
  const { user, isLoading } = useUser();
  const router = useRouter();

  useEffect(() => {
    // If authentication check is complete and user is not logged in, redirect to login
    if (!isLoading && !user) {
      router.push("/login");
    }
  }, [user, isLoading, router]);

  // Show loading state while checking authentication
  if (isLoading) {
    return (
      <div className="fixed inset-0 flex items-center justify-center bg-white">
        <div className="flex flex-col items-center">
          <Loader2 className="h-10 w-10 text-blue-500 animate-spin mb-4" />
          <p className="text-gray-600">Loading your dashboard...</p>
        </div>
      </div>
    );
  }

  // If user is authenticated, render the children
  if (user) {
    return <>{children}</>;
  }

  // This should not be visible as the user will be redirected
  return null;
}
