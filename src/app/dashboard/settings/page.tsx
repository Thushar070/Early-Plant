'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useApp } from '@/components/AppProvider';
import {
  getDefaultSettings,
  getMonitoringDevice,
  getStressTypes,
  getHowItWorksSteps,
} from '@/services/plantService';
import { NotificationSettings } from '@/types/plant';
import {
  Settings,
  User,
  Bell,
  Activity,
  Cpu,
  Info,
  Sprout,
  Radio,
  Brain,
  ScanSearch,
  BellRing,
  Droplets,
  Thermometer,
  ShieldAlert,
  FlaskConical,
  Bug,
  LogOut,
  ChevronDown,
  ChevronUp,
} from 'lucide-react';

const stressIcons: Record<string, React.ReactNode> = {
  droplets: <Droplets className="w-5 h-5" />,
  thermometer: <Thermometer className="w-5 h-5" />,
  'shield-alert': <ShieldAlert className="w-5 h-5" />,
  'flask-conical': <FlaskConical className="w-5 h-5" />,
  bug: <Bug className="w-5 h-5" />,
};

const howItWorksIcons: Record<string, React.ReactNode> = {
  sprout: <Sprout className="w-5 h-5" />,
  radio: <Radio className="w-5 h-5" />,
  brain: <Brain className="w-5 h-5" />,
  'scan-search': <ScanSearch className="w-5 h-5" />,
  'bell-ring': <BellRing className="w-5 h-5" />,
};

function Toggle({ checked, onChange }: { checked: boolean; onChange: () => void }) {
  return (
    <button
      onClick={onChange}
      className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
        checked ? 'bg-sage-500' : 'bg-sage-200'
      }`}
    >
      <span
        className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform shadow-sm ${
          checked ? 'translate-x-6' : 'translate-x-1'
        }`}
      />
    </button>
  );
}

export default function SettingsPage() {
  const router = useRouter();
  const {
    notifications,
    toggleNotification,
    monitoringInterval,
    setMonitoringInterval,
    logout,
  } = useApp();

  const defaultSettings = getDefaultSettings();
  const device = getMonitoringDevice();
  const stressTypesData = getStressTypes();
  const howItWorksData = getHowItWorksSteps();

  const [showStressTypes, setShowStressTypes] = useState(false);
  const [showHowItWorks, setShowHowItWorks] = useState(false);

  const intervals = ['15s', '30s', '1m', '5m'];

  const handleLogout = () => {
    logout();
    router.push('/');
  };

  return (
    <div className="space-y-6 max-w-2xl">
      {/* Header */}
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 rounded-lg bg-sage-100 flex items-center justify-center">
          <Settings className="w-5 h-5 text-sage-600" />
        </div>
        <div>
          <h1 className="text-2xl font-bold text-sage-800">Settings</h1>
          <p className="text-sage-500 text-sm">Manage your preferences</p>
        </div>
      </div>

      {/* Profile */}
      <div className="bg-white rounded-xl border border-sage-200 p-6 shadow-sm">
        <div className="flex items-center gap-3 mb-4">
          <User className="w-4 h-4 text-sage-500" />
          <p className="text-xs tracking-wider uppercase font-semibold text-sage-500">Profile</p>
        </div>
        <div className="flex items-center gap-4">
          <div className="w-12 h-12 rounded-full bg-sage-200 flex items-center justify-center text-sage-600 font-bold text-lg">
            {defaultSettings.name.charAt(0)}
          </div>
          <div>
            <p className="font-medium text-sage-800">{defaultSettings.name}</p>
            <p className="text-sm text-sage-500">{defaultSettings.email}</p>
          </div>
        </div>
      </div>

      {/* Notification Preferences */}
      <div className="bg-white rounded-xl border border-sage-200 p-6 shadow-sm">
        <div className="flex items-center gap-3 mb-5">
          <Bell className="w-4 h-4 text-sage-500" />
          <p className="text-xs tracking-wider uppercase font-semibold text-sage-500">
            Notification Preferences
          </p>
        </div>
        <div className="space-y-4">
          {([
            { key: 'stressAlerts' as keyof NotificationSettings, label: 'Stress Alerts', desc: 'Get notified when stress is detected' },
            { key: 'criticalAlerts' as keyof NotificationSettings, label: 'Critical Alerts', desc: 'Get notified for critical severity events' },
            { key: 'dailySummary' as keyof NotificationSettings, label: 'Daily Summary', desc: 'Receive a daily health overview' },
          ]).map((item) => (
            <div key={item.key} className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-sage-800">{item.label}</p>
                <p className="text-xs text-sage-400 mt-0.5">{item.desc}</p>
              </div>
              <Toggle
                checked={notifications[item.key]}
                onChange={() => toggleNotification(item.key)}
              />
            </div>
          ))}
        </div>
      </div>

      {/* Monitoring Preferences */}
      <div className="bg-white rounded-xl border border-sage-200 p-6 shadow-sm">
        <div className="flex items-center gap-3 mb-5">
          <Activity className="w-4 h-4 text-sage-500" />
          <p className="text-xs tracking-wider uppercase font-semibold text-sage-500">
            Monitoring Preferences
          </p>
        </div>
        <div>
          <p className="text-sm text-sage-700 mb-3">Monitoring Interval</p>
          <div className="flex flex-wrap gap-2">
            {intervals.map((val) => (
              <button
                key={val}
                onClick={() => setMonitoringInterval(val)}
                className={`px-4 py-1.5 rounded-lg text-sm font-medium transition-colors ${
                  monitoringInterval === val
                    ? 'bg-sage-600 text-white'
                    : 'bg-sage-50 border border-sage-200 text-sage-600 hover:bg-sage-100'
                }`}
              >
                {val}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Device Information */}
      <div className="bg-white rounded-xl border border-sage-200 p-6 shadow-sm">
        <div className="flex items-center gap-3 mb-5">
          <Cpu className="w-4 h-4 text-sage-500" />
          <p className="text-xs tracking-wider uppercase font-semibold text-sage-500">
            Device Information
          </p>
        </div>
        <div className="flex items-center justify-between">
          <div>
            <p className="font-medium text-sage-800">{device.name}</p>
            <p className="text-sm text-sage-500">{device.plantsConnected} plants connected</p>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-mint-500" />
            <span className="text-sm text-mint-600 font-medium">Connected</span>
          </div>
        </div>
      </div>

      {/* Stress Types Reference (Collapsible) */}
      <div className="bg-white rounded-xl border border-sage-200 shadow-sm overflow-hidden">
        <button
          onClick={() => setShowStressTypes(!showStressTypes)}
          className="w-full flex items-center justify-between p-6 hover:bg-sage-50 transition-colors"
        >
          <div className="flex items-center gap-3">
            <Info className="w-4 h-4 text-sage-500" />
            <p className="text-xs tracking-wider uppercase font-semibold text-sage-500">
              Stress Types Reference
            </p>
          </div>
          {showStressTypes ? (
            <ChevronUp className="w-5 h-5 text-sage-400" />
          ) : (
            <ChevronDown className="w-5 h-5 text-sage-400" />
          )}
        </button>
        {showStressTypes && (
          <div className="px-6 pb-6 space-y-4">
            {stressTypesData.map((st) => (
              <div key={st.type} className="flex items-start gap-3 p-3 bg-sage-50 rounded-lg">
                <div className="w-9 h-9 rounded-lg bg-sage-200 flex items-center justify-center text-sage-600 flex-shrink-0">
                  {stressIcons[st.icon] || <Info className="w-5 h-5" />}
                </div>
                <div>
                  <p className="font-medium text-sage-800 text-sm">{st.label}</p>
                  <p className="text-xs text-sage-500 mt-0.5 leading-relaxed">{st.description}</p>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* How It Works (Collapsible) */}
      <div className="bg-white rounded-xl border border-sage-200 shadow-sm overflow-hidden">
        <button
          onClick={() => setShowHowItWorks(!showHowItWorks)}
          className="w-full flex items-center justify-between p-6 hover:bg-sage-50 transition-colors"
        >
          <div className="flex items-center gap-3">
            <Sprout className="w-4 h-4 text-sage-500" />
            <p className="text-xs tracking-wider uppercase font-semibold text-sage-500">
              How PlantSense AI Works
            </p>
          </div>
          {showHowItWorks ? (
            <ChevronUp className="w-5 h-5 text-sage-400" />
          ) : (
            <ChevronDown className="w-5 h-5 text-sage-400" />
          )}
        </button>
        {showHowItWorks && (
          <div className="px-6 pb-6">
            <div className="space-y-4">
              {howItWorksData.map((step) => (
                <div key={step.step} className="flex items-start gap-4">
                  <div className="flex-shrink-0 w-8 h-8 rounded-full bg-sage-200 flex items-center justify-center text-sage-600 font-bold text-sm">
                    {step.step}
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <div className="text-sage-500">
                        {howItWorksIcons[step.icon] || <Info className="w-4 h-4" />}
                      </div>
                      <p className="font-medium text-sage-800 text-sm">{step.title}</p>
                    </div>
                    <p className="text-xs text-sage-500 leading-relaxed">{step.description}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* About */}
      <div className="bg-white rounded-xl border border-sage-200 p-6 shadow-sm">
        <div className="flex items-center gap-3 mb-4">
          <Sprout className="w-4 h-4 text-sage-500" />
          <p className="text-xs tracking-wider uppercase font-semibold text-sage-500">About</p>
        </div>
        <div>
          <p className="font-semibold text-sage-800">PlantSense AI</p>
          <p className="text-sm text-sage-500 mt-0.5">Early Plant Stress Detection Using Ultrasonic Signals</p>
          <p className="text-xs text-sage-400 mt-2">Version 1.0.0 — Research & Innovation</p>
        </div>
      </div>

      {/* Sign Out */}
      <button
        onClick={handleLogout}
        className="w-full flex items-center justify-center gap-2 px-4 py-3 bg-terracotta-50 border border-terracotta-200 text-terracotta-500 rounded-xl hover:bg-terracotta-100 transition-colors font-medium"
      >
        <LogOut className="w-4 h-4" />
        Sign Out
      </button>

      <div className="h-4" />
    </div>
  );
}
