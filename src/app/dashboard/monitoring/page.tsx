'use client';

import { useState, useEffect } from 'react';
import { getMonitoringDevice } from '@/services/plantService';
import { generateFrequencyData } from '@/data/mockData';
import { WaveformChart } from '@/components/WaveformChart';
import { Activity, Radio, Wifi, Signal, Clock } from 'lucide-react';

export default function MonitoringPage() {
  const device = getMonitoringDevice();
  const frequencyData = generateFrequencyData();
  const [lastSignal, setLastSignal] = useState(3);
  const [signalEvents, setSignalEvents] = useState([
    { time: '10:44:32 AM', event: 'Acoustic burst detected — elevated amplitude', type: 'warning' as const },
    { time: '10:44:28 AM', event: 'Normal signal received', type: 'normal' as const },
    { time: '10:44:21 AM', event: 'Frequency shift observed at 60 kHz', type: 'warning' as const },
    { time: '10:44:15 AM', event: 'Normal signal received', type: 'normal' as const },
    { time: '10:44:08 AM', event: 'Baseline calibration complete', type: 'normal' as const },
  ]);

  // Simulate live signal updates
  useEffect(() => {
    const interval = setInterval(() => {
      setLastSignal((prev) => (prev >= 8 ? 1 : prev + 1));
    }, 1000);
    return () => clearInterval(interval);
  }, []);

  // Simulate new events periodically
  useEffect(() => {
    const interval = setInterval(() => {
      const events = [
        'Normal signal received',
        'Acoustic data captured',
        'Signal amplitude within normal range',
        'Minor frequency variation detected',
        'Data packet processed',
      ];
      const now = new Date();
      const timeStr = now.toLocaleTimeString('en-US', {
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
        hour12: true,
      });
      setSignalEvents((prev) => [
        {
          time: timeStr,
          event: events[Math.floor(Math.random() * events.length)],
          type: Math.random() > 0.8 ? ('warning' as const) : ('normal' as const),
        },
        ...prev.slice(0, 4),
      ]);
    }, 6000);
    return () => clearInterval(interval);
  }, []);

  const maxFreqValue = Math.max(...frequencyData.map((d) => d.value));

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between flex-wrap gap-4">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-sage-100 flex items-center justify-center">
            <Activity className="w-5 h-5 text-sage-600" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-sage-800">Live Monitoring</h1>
            <p className="text-sage-500 text-sm">Real-time ultrasonic signal analysis</p>
          </div>
        </div>

        {/* Status Indicator */}
        <div className="flex items-center gap-2 bg-mint-50 px-4 py-2 rounded-full border border-mint-200">
          <span className="relative flex h-2.5 w-2.5">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-mint-400 opacity-75" />
            <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-mint-500" />
          </span>
          <span className="text-sm font-medium text-mint-600">Monitoring Active</span>
        </div>
      </div>

      {/* Device Info */}
      <div className="bg-white rounded-xl border border-sage-200 p-5 shadow-sm">
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-lg bg-sage-100 flex items-center justify-center">
              <Radio className="w-4 h-4 text-sage-600" />
            </div>
            <div>
              <p className="text-xs text-sage-500">Connected Device</p>
              <p className="font-medium text-sage-800 text-sm">{device.name}</p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-lg bg-mint-100 flex items-center justify-center">
              <Wifi className="w-4 h-4 text-mint-500" />
            </div>
            <div>
              <p className="text-xs text-sage-500">Plants Connected</p>
              <p className="font-medium text-sage-800 text-sm">{device.plantsConnected}</p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-lg bg-warm-100 flex items-center justify-center">
              <Signal className="w-4 h-4 text-warm-500" />
            </div>
            <div>
              <p className="text-xs text-sage-500">Last Signal</p>
              <p className="font-medium text-sage-800 text-sm">{lastSignal} second{lastSignal !== 1 ? 's' : ''} ago</p>
            </div>
          </div>
        </div>
      </div>

      {/* Main Waveform */}
      <div className="bg-white rounded-xl border border-sage-200 p-6 shadow-sm">
        <div className="flex items-center justify-between mb-4">
          <p className="text-xs tracking-wider uppercase font-semibold text-sage-500">
            Ultrasonic Activity
          </p>
          <div className="flex items-center gap-2">
            <span className="relative flex h-2 w-2">
              <span className="animate-signal absolute inline-flex h-full w-full rounded-full bg-sage-400" />
              <span className="relative inline-flex rounded-full h-2 w-2 bg-sage-500" />
            </span>
            <span className="text-xs text-sage-400">Live</span>
          </div>
        </div>
        <WaveformChart height={280} stressLevel="elevated" animated />
        <div className="mt-3 flex items-center gap-2">
          <div className="flex items-center gap-1 text-xs text-sage-400">
            <span className="w-2 h-2 rounded-full bg-sage-400" />
            Normal
          </div>
          <div className="flex items-center gap-1 text-xs text-warm-400">
            <span className="w-2 h-2 rounded-full bg-warm-400" />
            Elevated
          </div>
          <div className="flex items-center gap-1 text-xs text-terracotta-400">
            <span className="w-2 h-2 rounded-full bg-terracotta-400" />
            High
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Frequency Activity */}
        <div className="bg-white rounded-xl border border-sage-200 p-6 shadow-sm">
          <p className="text-xs tracking-wider uppercase font-semibold text-sage-500 mb-4">
            Frequency Activity
          </p>
          <div className="flex items-end gap-2 h-40">
            {frequencyData.map((d, i) => (
              <div key={i} className="flex-1 flex flex-col items-center gap-1">
                <div className="w-full relative" style={{ height: '120px' }}>
                  <div
                    className="absolute bottom-0 w-full rounded-t bg-sage-300 transition-all animate-wave-pulse"
                    style={{
                      height: `${(d.value / maxFreqValue) * 100}%`,
                      animationDelay: `${i * 200}ms`,
                    }}
                  />
                </div>
                <span className="text-[10px] text-sage-400 whitespace-nowrap">{d.freq}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Recent Signal Events */}
        <div className="bg-white rounded-xl border border-sage-200 p-6 shadow-sm">
          <p className="text-xs tracking-wider uppercase font-semibold text-sage-500 mb-4">
            Recent Signal Events
          </p>
          <div className="space-y-3">
            {signalEvents.map((event, i) => (
              <div key={i} className="flex items-start gap-3">
                <div className={`w-2 h-2 rounded-full mt-1.5 flex-shrink-0 ${
                  event.type === 'warning' ? 'bg-warm-400' : 'bg-sage-300'
                }`} />
                <div className="flex-1 min-w-0">
                  <p className="text-sm text-sage-700 truncate">{event.event}</p>
                  <div className="flex items-center gap-1 text-xs text-sage-400 mt-0.5">
                    <Clock className="w-3 h-3" />
                    {event.time}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
