'use client';

import { useState } from 'react';
import { getHealthData, getHistoryEntries } from '@/services/plantService';
import { Clock, TrendingDown } from 'lucide-react';
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';

type TimeRange = '24h' | '7d' | '30d';

const severityColors = {
  critical: 'bg-rose-100 text-rose-500',
  high: 'bg-terracotta-100 text-terracotta-500',
  medium: 'bg-warm-100 text-warm-500',
  low: 'bg-sage-100 text-sage-600',
};

export default function HistoryPage() {
  const [timeRange, setTimeRange] = useState<TimeRange>('7d');
  const chartData = getHealthData(timeRange);
  const historyEntries = getHistoryEntries();

  const rangeOptions: { key: TimeRange; label: string }[] = [
    { key: '24h', label: 'Last 24 hours' },
    { key: '7d', label: 'Last 7 days' },
    { key: '30d', label: 'Last 30 days' },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 rounded-lg bg-sage-100 flex items-center justify-center">
          <Clock className="w-5 h-5 text-sage-600" />
        </div>
        <div>
          <h1 className="text-2xl font-bold text-sage-800">History</h1>
          <p className="text-sage-500 text-sm">Plant health trends and past events</p>
        </div>
      </div>

      {/* Chart Section */}
      <div className="bg-white rounded-xl border border-sage-200 p-6 shadow-sm">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6">
          <p className="text-xs tracking-wider uppercase font-semibold text-sage-500">
            Plant Health Over Time
          </p>
          <div className="flex flex-wrap gap-2">
            {rangeOptions.map((opt) => (
              <button
                key={opt.key}
                onClick={() => setTimeRange(opt.key)}
                className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
                  timeRange === opt.key
                    ? 'bg-sage-600 text-white'
                    : 'bg-sage-50 border border-sage-200 text-sage-600 hover:bg-sage-100'
                }`}
              >
                {opt.label}
              </button>
            ))}
          </div>
        </div>

        <div className="h-[300px]">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={chartData} margin={{ top: 20, right: 20, left: -10, bottom: 10 }}>
              <defs>
                <linearGradient id="healthGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#778c63" stopOpacity={0.45} />
                  <stop offset="95%" stopColor="#778c63" stopOpacity={0.05} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#d4dac9" vertical={false} />
              <XAxis
                dataKey="label"
                tick={{ fill: '#778c63', fontSize: 12, fontWeight: 500 }}
                axisLine={{ stroke: '#d4dac9' }}
                tickLine={false}
              />
              <YAxis
                domain={[50, 100]}
                tick={{ fill: '#778c63', fontSize: 12, fontWeight: 500 }}
                axisLine={false}
                tickLine={false}
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#fff',
                  border: '1px solid #d4dac9',
                  borderRadius: '8px',
                  fontSize: '13px',
                  padding: '8px 12px',
                  boxShadow: '0 2px 6px rgba(0,0,0,0.06)',
                }}
                labelStyle={{ color: '#3d4934', fontWeight: 600 }}
                itemStyle={{ color: '#5d704d', fontWeight: 500 }}
                formatter={(value: number) => [`${value} / 100`, 'Sample Health Score']}
              />
              <Area
                isAnimationActive={false}
                type="monotone"
                dataKey="score"
                stroke="#5d704d"
                strokeWidth={3}
                dot={{ r: 4.5, fill: '#5d704d', stroke: '#fff', strokeWidth: 2 }}
                activeDot={{ r: 7, fill: '#3d4934', stroke: '#fff', strokeWidth: 2 }}
                fill="url(#healthGradient)"
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Historical Events */}
      <div className="bg-white rounded-xl border border-sage-200 shadow-sm overflow-hidden">
        <div className="p-5 border-b border-sage-100">
          <div className="flex items-center gap-2">
            <TrendingDown className="w-4 h-4 text-sage-500" />
            <p className="text-xs tracking-wider uppercase font-semibold text-sage-500">
              Historical Stress Events
            </p>
          </div>
        </div>

        {/* Desktop Table */}
        <div className="hidden md:block overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="bg-sage-50">
                <th className="text-left px-5 py-3 text-xs font-semibold text-sage-500 uppercase tracking-wider">Date</th>
                <th className="text-left px-5 py-3 text-xs font-semibold text-sage-500 uppercase tracking-wider">Plant</th>
                <th className="text-left px-5 py-3 text-xs font-semibold text-sage-500 uppercase tracking-wider">Stress Type</th>
                <th className="text-left px-5 py-3 text-xs font-semibold text-sage-500 uppercase tracking-wider">Severity</th>
                <th className="text-left px-5 py-3 text-xs font-semibold text-sage-500 uppercase tracking-wider">Example Confidence</th>
              </tr>
            </thead>
            <tbody>
              {historyEntries.map((entry, i) => (
                <tr key={i} className="border-t border-sage-100 hover:bg-sage-50/50 transition-colors">
                  <td className="px-5 py-3.5 text-sm text-sage-600">{entry.date}</td>
                  <td className="px-5 py-3.5 text-sm font-medium text-sage-800">{entry.plantName}</td>
                  <td className="px-5 py-3.5 text-sm text-sage-700">{entry.stressLabel}</td>
                  <td className="px-5 py-3.5">
                    <span className={`inline-flex px-2.5 py-0.5 rounded-full text-xs font-medium ${severityColors[entry.severity]}`}>
                      {entry.severity.charAt(0).toUpperCase() + entry.severity.slice(1)}
                    </span>
                  </td>
                  <td className="px-5 py-3.5 text-sm text-sage-700">{entry.confidence}%</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Mobile Cards */}
        <div className="md:hidden divide-y divide-sage-100">
          {historyEntries.map((entry, i) => (
            <div key={i} className="p-4">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium text-sage-800">{entry.plantName}</span>
                <span className="text-xs text-sage-400">{entry.date}</span>
              </div>
              <div className="flex items-center gap-2 flex-wrap">
                <span className="text-sm text-sage-600">{entry.stressLabel}</span>
                <span className={`inline-flex px-2 py-0.5 rounded-full text-xs font-medium ${severityColors[entry.severity]}`}>
                  {entry.severity.charAt(0).toUpperCase() + entry.severity.slice(1)}
                </span>
                <span className="text-xs text-sage-400">{entry.confidence}%</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
