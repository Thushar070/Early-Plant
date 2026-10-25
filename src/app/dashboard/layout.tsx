'use client';

import { useApp } from '@/components/AppProvider';
import { Sidebar } from '@/components/Sidebar';
import { useRouter } from 'next/navigation';
import { useEffect } from 'react';

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const { isLoggedIn } = useApp();
  const router = useRouter();

  useEffect(() => {
    if (!isLoggedIn) {
      router.replace('/');
    }
  }, [isLoggedIn, router]);

  if (!isLoggedIn) return null;

  return (
    <div className="min-h-screen bg-sage-50">
      <Sidebar />
      <main className="lg:ml-[260px] pb-20 lg:pb-0">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-6 lg:py-8">
          <aside
            aria-label="Prototype data notice"
            className="mb-6 rounded-lg border border-warm-200 bg-warm-50 px-4 py-3 text-sm text-sage-700"
          >
            <strong>Research prototype.</strong> Plant records, health scores, confidence values, alerts, and charts are sample data. Monitoring events are simulated; no physical sensor or live model inference is connected.
          </aside>
          {children}
        </div>
      </main>
    </div>
  );
}
