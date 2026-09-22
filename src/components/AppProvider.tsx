'use client';

import React, { createContext, useContext, useState, useCallback } from 'react';
import type { NotificationSettings } from '@/types/plant';

interface AppContextType {
  isLoggedIn: boolean;
  login: () => void;
  logout: () => void;
  reviewedAlerts: Set<string>;
  markAlertReviewed: (id: string) => void;
  notifications: NotificationSettings;
  toggleNotification: (key: keyof NotificationSettings) => void;
  monitoringInterval: string;
  setMonitoringInterval: (val: string) => void;
}

const AppContext = createContext<AppContextType | null>(null);

export function useApp() {
  const ctx = useContext(AppContext);
  if (!ctx) throw new Error('useApp must be used within AppProvider');
  return ctx;
}

export function AppProvider({ children }: { children: React.ReactNode }) {
  const [isLoggedIn, setIsLoggedIn] = useState(true);
  const [reviewedAlerts, setReviewedAlerts] = useState<Set<string>>(new Set(['alert-5']));
  const [notifications, setNotifications] = useState<NotificationSettings>({
    stressAlerts: true,
    criticalAlerts: true,
    dailySummary: false,
  });
  const [monitoringInterval, setMonitoringInterval] = useState('30s');

  const login = useCallback(() => setIsLoggedIn(true), []);
  const logout = useCallback(() => setIsLoggedIn(false), []);

  const markAlertReviewed = useCallback((id: string) => {
    setReviewedAlerts((prev) => new Set(prev).add(id));
  }, []);

  const toggleNotification = useCallback((key: keyof NotificationSettings) => {
    setNotifications((prev) => ({ ...prev, [key]: !prev[key] }));
  }, []);

  return (
    <AppContext.Provider
      value={{
        isLoggedIn,
        login,
        logout,
        reviewedAlerts,
        markAlertReviewed,
        notifications,
        toggleNotification,
        monitoringInterval,
        setMonitoringInterval,
      }}
    >
      {children}
    </AppContext.Provider>
  );
}
