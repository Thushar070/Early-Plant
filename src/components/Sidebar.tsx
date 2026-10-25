'use client';

import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import { LayoutDashboard, Leaf, Activity, Bell, Clock, Settings, Sprout, LogOut, Info, FlaskConical } from 'lucide-react';
import { useApp } from './AppProvider';

const navItems = [
  { name: 'Overview', href: '/dashboard', icon: LayoutDashboard },
  { name: 'My Plants', href: '/dashboard/plants', icon: Leaf },
  { name: 'Monitoring', href: '/dashboard/monitoring', icon: Activity },
  { name: 'Alerts', href: '/dashboard/alerts', icon: Bell },
  { name: 'History', href: '/dashboard/history', icon: Clock },
  { name: 'Research', href: '/dashboard/research', icon: FlaskConical },
  { name: 'Settings', href: '/dashboard/settings', icon: Settings },
];

export function Sidebar() {
  const pathname = usePathname();
  const router = useRouter();
  const { logout } = useApp();

  const handleLogout = () => {
    logout();
    router.push('/');
  };

  return (
    <>
      {/* Mobile Top Header Bar */}
      <div className="lg:hidden flex items-center justify-between px-4 py-3 bg-white border-b border-sage-200 sticky top-0 z-20">
        <div className="flex items-center gap-2">
          <div className="bg-sage-100 p-1.5 rounded-lg">
            <Sprout className="w-5 h-5 text-sage-600" />
          </div>
          <span className="text-sage-800 font-bold text-base">PlantSense AI</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-mint-500 animate-pulse" />
          <span className="text-xs text-sage-600 font-medium">Node 01 Online</span>
        </div>
      </div>

      {/* Desktop Sidebar */}
      <div className="hidden lg:flex fixed inset-y-0 left-0 w-[260px] bg-white border-r border-sage-200 flex-col z-20">
        <div className="flex items-center gap-3 px-6 h-20 border-b border-sage-100 shrink-0">
          <div className="bg-sage-100 p-2 rounded-lg">
            <Sprout className="w-6 h-6 text-sage-600" />
          </div>
          <span className="text-sage-800 font-bold text-xl">PlantSense AI</span>
        </div>

        <nav className="flex-1 px-4 py-6 space-y-1 overflow-y-auto">
          {navItems.map((item) => {
            const isActive =
              item.href === '/dashboard'
                ? pathname === '/dashboard'
                : pathname.startsWith(item.href);
            const Icon = item.icon;
            return (
              <Link
                key={item.name}
                href={item.href}
                className={`flex items-center gap-3 px-3 py-3 rounded-md transition-colors border-l-[3px] ${
                  isActive
                    ? 'bg-sage-100 text-sage-700 border-sage-500 font-medium'
                    : 'text-sage-600 hover:bg-sage-50 hover:text-sage-700 border-transparent'
                }`}
              >
                <Icon className="w-5 h-5" />
                {item.name}
              </Link>
            );
          })}
        </nav>

        <div className="p-4 border-t border-sage-200 space-y-2 shrink-0">
          <Link
            href="/dashboard/settings"
            className="flex items-center gap-3 px-3 py-2 w-full text-sage-600 hover:bg-sage-50 rounded-md transition-colors text-left text-sm"
          >
            <Info className="w-5 h-5" />
            About PlantSense
          </Link>
          <button
            onClick={handleLogout}
            className="flex items-center gap-3 px-3 py-2 w-full text-terracotta-600 hover:bg-terracotta-50 rounded-md transition-colors text-left text-sm font-medium"
          >
            <LogOut className="w-5 h-5" />
            Sign Out
          </button>
        </div>
      </div>

      {/* Mobile Bottom Navigation */}
      <div className="lg:hidden fixed bottom-0 left-0 right-0 bg-white border-t border-sage-200 z-20 flex justify-around items-center h-16 px-2">
        {navItems.map((item) => {
          const isActive =
            item.href === '/dashboard'
              ? pathname === '/dashboard'
              : pathname.startsWith(item.href);
          const Icon = item.icon;
          return (
            <Link
              key={item.name}
              href={item.href}
              className={`flex flex-col items-center justify-center w-full h-full space-y-1 ${
                isActive ? 'text-sage-700' : 'text-sage-500'
              }`}
            >
              <Icon className={`w-5 h-5 ${isActive ? 'text-sage-600' : ''}`} />
              <span className="text-[10px] font-medium truncate w-full text-center px-1">
                {item.name}
              </span>
            </Link>
          );
        })}
      </div>
    </>
  );
}
