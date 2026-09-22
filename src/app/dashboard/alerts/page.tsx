'use client';

import { useState, useMemo } from 'react';
import { getAlerts } from '@/services/plantService';
import { useApp } from '@/components/AppProvider';
import { StressSeverity } from '@/types/plant';
import Link from 'next/link';
import {
  Bell,
  CheckCircle2,
  AlertTriangle,
  AlertOctagon,
  Info,
  ChevronDown,
  ChevronUp,
  Clock,
  MapPin,
  Eye,
  Target,
  Lightbulb,
  Frown,
} from 'lucide-react';

type FilterTab = 'all' | StressSeverity;

export default function AlertsPage() {
  const allAlerts = getAlerts();
  const { reviewedAlerts, markAlertReviewed } = useApp();
  const [filter, setFilter] = useState<FilterTab>('all');
  const [expandedId, setExpandedId] = useState<string | null>(null);

  const filteredAlerts = useMemo(() => {
    if (filter === 'all') return allAlerts;
    return allAlerts.filter((a) => a.severity === filter);
  }, [allAlerts, filter]);

  const tabs: { key: FilterTab; label: string; count: number }[] = [
    { key: 'all', label: 'All', count: allAlerts.length },
    { key: 'critical', label: 'Critical', count: allAlerts.filter((a) => a.severity === 'critical').length },
    { key: 'high', label: 'High', count: allAlerts.filter((a) => a.severity === 'high').length },
    { key: 'medium', label: 'Medium', count: allAlerts.filter((a) => a.severity === 'medium').length },
    { key: 'low', label: 'Low', count: allAlerts.filter((a) => a.severity === 'low').length },
  ];

  const severityConfig = {
    critical: { bg: 'bg-rose-100', text: 'text-rose-500', border: 'border-rose-200', icon: AlertOctagon },
    high: { bg: 'bg-terracotta-100', text: 'text-terracotta-500', border: 'border-terracotta-200', icon: AlertTriangle },
    medium: { bg: 'bg-warm-100', text: 'text-warm-500', border: 'border-warm-200', icon: AlertTriangle },
    low: { bg: 'bg-sage-100', text: 'text-sage-600', border: 'border-sage-200', icon: Info },
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 rounded-lg bg-sage-100 flex items-center justify-center">
          <Bell className="w-5 h-5 text-sage-600" />
        </div>
        <div>
          <h1 className="text-2xl font-bold text-sage-800">Alerts</h1>
          <p className="text-sage-500 text-sm">{allAlerts.filter((a) => !reviewedAlerts.has(a.id)).length} unreviewed</p>
        </div>
      </div>

      {/* Filter Tabs */}
      <div className="flex flex-wrap gap-2">
        {tabs.map((tab) => (
          <button
            key={tab.key}
            onClick={() => setFilter(tab.key)}
            className={`px-4 py-1.5 rounded-full text-sm font-medium transition-colors ${
              filter === tab.key
                ? 'bg-sage-600 text-white'
                : 'bg-white border border-sage-200 text-sage-600 hover:bg-sage-50'
            }`}
          >
            {tab.label}
            <span className="ml-1.5 opacity-70">({tab.count})</span>
          </button>
        ))}
      </div>

      {/* Alert List */}
      {filteredAlerts.length > 0 ? (
        <div className="space-y-3">
          {filteredAlerts.map((alert) => {
            const config = severityConfig[alert.severity];
            const SeverityIcon = config.icon;
            const isReviewed = reviewedAlerts.has(alert.id);
            const isExpanded = expandedId === alert.id;

            return (
              <div
                key={alert.id}
                className={`bg-white rounded-xl border shadow-sm overflow-hidden transition-all ${
                  isReviewed ? 'border-sage-200 opacity-75' : `border-sage-200`
                }`}
              >
                {/* Alert Header */}
                <div
                  className="p-5 cursor-pointer"
                  onClick={() => setExpandedId(isExpanded ? null : alert.id)}
                >
                  <div className="flex items-start gap-4">
                    {/* Severity Badge */}
                    <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium flex-shrink-0 ${config.bg} ${config.text}`}>
                      <SeverityIcon className="w-3.5 h-3.5" />
                      {alert.severity.toUpperCase()}
                    </span>

                    {/* Content */}
                    <div className="flex-1 min-w-0">
                      <p className="font-medium text-sage-800">{alert.stressLabel}</p>
                      <div className="flex flex-wrap items-center gap-x-4 gap-y-1 mt-1.5 text-sm text-sage-500">
                        <span className="flex items-center gap-1">
                          <MapPin className="w-3.5 h-3.5" />
                          {alert.plantName} — {alert.location}
                        </span>
                        <span className="flex items-center gap-1">
                          <Clock className="w-3.5 h-3.5" />
                          {alert.timestamp}
                        </span>
                        <span className="flex items-center gap-1">
                          <Target className="w-3.5 h-3.5" />
                          {alert.confidence}% confidence
                        </span>
                      </div>
                    </div>

                    {/* Right Side */}
                    <div className="flex items-center gap-2 flex-shrink-0">
                      {isReviewed && (
                        <span className="inline-flex items-center gap-1 px-2 py-1 rounded-full bg-sage-100 text-sage-600 text-xs">
                          <CheckCircle2 className="w-3 h-3" />
                          Reviewed
                        </span>
                      )}
                      {isExpanded ? (
                        <ChevronUp className="w-5 h-5 text-sage-400" />
                      ) : (
                        <ChevronDown className="w-5 h-5 text-sage-400" />
                      )}
                    </div>
                  </div>
                </div>

                {/* Expanded Content */}
                {isExpanded && (
                  <div className="px-5 pb-5 border-t border-sage-100 pt-4">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                      <div className="bg-cream-50 rounded-lg border border-cream-300 p-4">
                        <div className="flex items-center gap-2 mb-2">
                          <Info className="w-4 h-4 text-cream-500" />
                          <p className="text-xs font-semibold text-sage-600 uppercase tracking-wider">
                            What This May Mean
                          </p>
                        </div>
                        <p className="text-sm text-sage-700 leading-relaxed">{alert.meaning}</p>
                      </div>
                      <div className="bg-mint-50 rounded-lg border border-mint-200 p-4">
                        <div className="flex items-center gap-2 mb-2">
                          <Lightbulb className="w-4 h-4 text-mint-500" />
                          <p className="text-xs font-semibold text-sage-600 uppercase tracking-wider">
                            Recommended Action
                          </p>
                        </div>
                        <p className="text-sm text-sage-700 leading-relaxed">{alert.recommendation}</p>
                      </div>
                    </div>

                    <div className="flex items-center gap-3">
                      <Link
                        href={`/dashboard/plants/${alert.plantId}`}
                        className="inline-flex items-center gap-2 px-4 py-2 bg-sage-600 text-white rounded-lg hover:bg-sage-700 transition-colors text-sm font-medium"
                      >
                        <Eye className="w-4 h-4" />
                        View Plant
                      </Link>
                      {!isReviewed && (
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            markAlertReviewed(alert.id);
                          }}
                          className="inline-flex items-center gap-2 px-4 py-2 border border-sage-300 text-sage-700 rounded-lg hover:bg-sage-50 transition-colors text-sm font-medium"
                        >
                          <CheckCircle2 className="w-4 h-4" />
                          Mark as Reviewed
                        </button>
                      )}
                    </div>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      ) : (
        <div className="text-center py-16">
          <Frown className="w-12 h-12 text-sage-300 mx-auto mb-3" />
          <p className="text-sage-500 font-medium">No alerts found</p>
          <p className="text-sage-400 text-sm mt-1">No alerts match the selected filter</p>
        </div>
      )}
    </div>
  );
}
