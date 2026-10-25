'use client';

import { getDashboardSummary, getFeaturedPlants } from '@/services/plantService';
import { SummaryCard } from '@/components/SummaryCard';
import { PlantCard } from '@/components/PlantCard';
import { HealthScoreRing } from '@/components/HealthScoreRing';
import { useApp } from '@/components/AppProvider';
import {
  Leaf,
  HeartPulse,
  AlertTriangle,
  Bell,
  ChevronRight,
  Info,
  Lightbulb,
  Eye,
  CheckCircle2,
} from 'lucide-react';
import Link from 'next/link';

export default function DashboardPage() {
  const summary = getDashboardSummary();
  const featuredPlants = getFeaturedPlants();
  const { reviewedAlerts, markAlertReviewed } = useApp();

  const isTomatoReviewed = reviewedAlerts.has('alert-2');

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-sage-800">Good Morning</h1>
        <p className="text-sage-500 mt-1">Here&apos;s your plant health overview</p>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <SummaryCard
          title="Plants Monitored"
          value={summary.plantsMonitored}
          icon={<Leaf className="w-5 h-5" />}
          color="sage"
        />
        <SummaryCard
          title="Healthy Plants"
          value={summary.healthyPlants}
          icon={<HeartPulse className="w-5 h-5" />}
          color="mint"
        />
        <SummaryCard
          title="Under Stress"
          value={summary.plantsUnderStress}
          icon={<AlertTriangle className="w-5 h-5" />}
          color="warm"
        />
        <SummaryCard
          title="Critical Alerts"
          value={summary.criticalAlerts}
          icon={<Bell className="w-5 h-5" />}
          color="rose"
        />
      </div>

      {/* Prominent Stress Alert Experience */}
      {!isTomatoReviewed ? (
        <div className="bg-terracotta-50/70 border-2 border-terracotta-200 rounded-xl p-6 shadow-sm transition-all">
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-4 border-b border-terracotta-200/80">
            <div className="flex items-center gap-3">
              <span className="p-2.5 rounded-xl bg-terracotta-100 text-terracotta-600 flex-shrink-0">
                <AlertTriangle className="w-6 h-6" />
              </span>
              <div>
                <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold bg-terracotta-200 text-terracotta-700 uppercase tracking-wider mb-1">
                  Sample Alert
                </span>
                <h3 className="text-lg font-bold text-sage-900">
                  Example: drought-stress label for Tomato Plant 04
                </h3>
              </div>
            </div>

            <div className="flex flex-wrap items-center gap-x-4 gap-y-1 text-xs sm:text-sm text-sage-700 bg-white/70 px-3.5 py-2 rounded-lg border border-terracotta-100">
              <div>
                <span className="text-sage-500 font-medium">Example confidence: </span>
                <span className="font-bold text-sage-800">87%</span>
              </div>
              <span className="text-sage-300 hidden sm:inline">•</span>
              <div>
                <span className="text-sage-500 font-medium">Severity: </span>
                <span className="font-bold text-terracotta-600">High</span>
              </div>
              <span className="text-sage-300 hidden sm:inline">•</span>
              <div>
                <span className="text-sage-500 font-medium">Location: </span>
                <span className="font-bold text-sage-800">Greenhouse A</span>
              </div>
              <span className="text-sage-300 hidden sm:inline">•</span>
              <div>
                <span className="text-sage-500 font-medium">Detected: </span>
                <span className="text-sage-700">12 minutes ago</span>
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 my-4">
            <div className="bg-white/80 rounded-lg p-4 border border-terracotta-100">
              <p className="text-xs uppercase tracking-wider font-semibold text-sage-600 mb-1.5 flex items-center gap-1.5">
                <Info className="w-3.5 h-3.5 text-terracotta-500" />
                What This May Mean
              </p>
              <p className="text-sm text-sage-700 leading-relaxed">
                &ldquo;The plant is showing an acoustic pattern associated with water stress.&rdquo;
              </p>
            </div>
            <div className="bg-white/80 rounded-lg p-4 border border-terracotta-100">
              <p className="text-xs uppercase tracking-wider font-semibold text-sage-600 mb-1.5 flex items-center gap-1.5">
                <Lightbulb className="w-3.5 h-3.5 text-mint-600" />
                Recommended Action
              </p>
              <p className="text-sm text-sage-700 leading-relaxed">
                &ldquo;Check soil moisture around the plant and verify irrigation.&rdquo;
              </p>
            </div>
          </div>

          <div className="flex flex-wrap items-center gap-3 pt-2">
            <Link
              href="/dashboard/plants/tomato-04"
              className="inline-flex items-center gap-2 px-5 py-2.5 bg-sage-600 hover:bg-sage-700 text-white rounded-lg font-medium text-sm transition-colors shadow-sm"
            >
              <Eye className="w-4 h-4" />
              View Plant
            </Link>
            <button
              onClick={() => markAlertReviewed('alert-2')}
              className="inline-flex items-center gap-2 px-5 py-2.5 bg-white border border-sage-300 hover:bg-sage-50 text-sage-700 rounded-lg font-medium text-sm transition-colors"
            >
              <CheckCircle2 className="w-4 h-4 text-sage-500" />
              Mark as Reviewed
            </button>
          </div>
        </div>
      ) : (
        <div className="bg-mint-50/80 border border-mint-200 rounded-xl p-4 flex items-center justify-between text-sm">
          <div className="flex items-center gap-2 text-mint-700">
            <CheckCircle2 className="w-4 h-4" />
            <span>Tomato Plant 04 alert has been marked as reviewed.</span>
          </div>
          <Link
            href="/dashboard/alerts"
            className="text-sage-600 hover:text-sage-800 font-medium underline text-xs"
          >
            View all alerts
          </Link>
        </div>
      )}

      {/* Overall Plant Health */}
      <div className="bg-white rounded-xl border border-sage-200 p-6 shadow-sm">
        <p className="text-xs tracking-wider uppercase font-semibold text-sage-500 mb-6">
          Overall Plant Health
        </p>
        <div className="flex flex-col sm:flex-row items-center gap-6">
          <HealthScoreRing score={summary.overallHealthScore} size={160} />
          <div>
            <div className="flex items-center gap-2 mb-2">
              <span className="text-lg font-semibold text-sage-800">Status:</span>
              <span className="inline-flex items-center px-3 py-1 rounded-full bg-mint-100 text-mint-500 text-sm font-medium">
                {summary.overallStatus}
              </span>
            </div>
            <p className="text-sage-500 text-sm leading-relaxed max-w-md">
              Your plants are generally healthy. A few plants are showing signs of stress that may need attention. 
              Regular monitoring helps detect issues early.
            </p>
          </div>
        </div>
      </div>

      {/* My Plants */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-sage-800">My Plants</h2>
          <Link
            href="/dashboard/plants"
            className="flex items-center gap-1 text-sm text-sage-500 hover:text-sage-700 transition-colors"
          >
            View All
            <ChevronRight className="w-4 h-4" />
          </Link>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {featuredPlants.map((plant) => (
            <PlantCard key={plant.id} plant={plant} />
          ))}
        </div>
      </div>
    </div>
  );
}
