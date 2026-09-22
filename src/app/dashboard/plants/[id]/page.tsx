'use client';

import { useParams, useRouter } from 'next/navigation';
import { getPlantById, getAlerts } from '@/services/plantService';
import { useApp } from '@/components/AppProvider';
import { WaveformChart } from '@/components/WaveformChart';
import { HealthScoreRing } from '@/components/HealthScoreRing';
import {
  MapPin,
  ArrowLeft,
  AlertTriangle,
  Shield,
  Clock,
  CheckCircle2,
  Info,
  Lightbulb,
  AlertOctagon,
  Bell,
} from 'lucide-react';

export default function PlantDetailPage() {
  const params = useParams();
  const router = useRouter();
  const { reviewedAlerts, markAlertReviewed } = useApp();

  const plantId = params.id as string;
  const plant = getPlantById(plantId);

  if (!plant) {
    return (
      <div className="text-center py-20">
        <div className="w-16 h-16 bg-sage-100 rounded-full flex items-center justify-center mx-auto mb-4">
          <Info className="w-8 h-8 text-sage-400" />
        </div>
        <h2 className="text-xl font-semibold text-sage-800 mb-2">Plant Not Found</h2>
        <p className="text-sage-500 mb-6">The plant you&apos;re looking for doesn&apos;t exist.</p>
        <button
          onClick={() => router.push('/dashboard/plants')}
          className="inline-flex items-center gap-2 px-4 py-2 bg-sage-600 text-white rounded-lg hover:bg-sage-700 transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
          Back to Plants
        </button>
      </div>
    );
  }

  // Find matching alert for this plant
  const alerts = getAlerts();
  const matchingAlert = alerts.find((a) => a.plantId === plant.id);
  const isReviewed = matchingAlert ? reviewedAlerts.has(matchingAlert.id) : true;

  const severityColors = {
    critical: 'bg-rose-100 text-rose-600 border-rose-200',
    high: 'bg-terracotta-100 text-terracotta-600 border-terracotta-200',
    medium: 'bg-warm-100 text-warm-600 border-warm-200',
    low: 'bg-sage-100 text-sage-700 border-sage-200',
  };

  const stressLevel: 'normal' | 'elevated' | 'high' =
    plant.status === 'critical' ? 'high' : plant.status === 'stressed' ? 'elevated' : 'normal';

  const observationDotColors = {
    normal: 'bg-sage-400',
    warning: 'bg-warm-400',
    alert: 'bg-terracotta-400',
  };

  return (
    <div className="space-y-6">
      {/* Back Navigation & Breadcrumb */}
      <div className="flex items-center justify-between">
        <button
          onClick={() => router.push('/dashboard/plants')}
          className="flex items-center gap-2 text-sage-500 hover:text-sage-700 transition-colors text-sm font-medium"
        >
          <ArrowLeft className="w-4 h-4" />
          Back to Plants
        </button>
        <div className="flex items-center gap-2">
          <button
            onClick={() => router.push('/dashboard/alerts')}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-white border border-sage-200 hover:bg-sage-50 text-sage-700 rounded-lg text-xs font-medium transition-colors"
          >
            <Bell className="w-3.5 h-3.5 text-sage-500" />
            View Alerts
          </button>
          <button
            onClick={() => router.push('/dashboard/history')}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-white border border-sage-200 hover:bg-sage-50 text-sage-700 rounded-lg text-xs font-medium transition-colors"
          >
            <Clock className="w-3.5 h-3.5 text-sage-500" />
            View History
          </button>
        </div>
      </div>

      {/* Plant Header */}
      <div className="bg-white rounded-xl border border-sage-200 p-6 shadow-sm">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div className="flex items-center gap-4">
            <div className={`w-14 h-14 rounded-xl flex items-center justify-center text-3xl shadow-xs ${
              plant.status === 'critical' ? 'bg-rose-100' : plant.status === 'stressed' ? 'bg-warm-100' : 'bg-mint-100'
            }`}>
              {plant.icon}
            </div>
            <div>
              <h1 className="text-2xl font-bold text-sage-800">{plant.name}</h1>
              <div className="flex flex-wrap items-center gap-x-4 gap-y-1 text-sage-500 mt-1 text-sm">
                <span className="flex items-center gap-1.5">
                  <MapPin className="w-4 h-4 text-sage-400" />
                  {plant.location}
                </span>
                <span>•</span>
                <span className="flex items-center gap-1.5">
                  <span className="text-sage-400">Status:</span>
                  <span className={`font-semibold ${
                    plant.status === 'critical'
                      ? 'text-rose-600'
                      : plant.status === 'stressed'
                        ? 'text-terracotta-600'
                        : 'text-mint-600'
                  }`}>
                    {plant.stress?.label ? `${plant.stress.label} Detected` : 'Healthy'}
                  </span>
                </span>
              </div>
            </div>
          </div>

          <div className="flex items-center gap-2 self-start sm:self-center">
            <span className="text-xs text-sage-400 font-medium">Last monitored {plant.lastMonitored}</span>
          </div>
        </div>
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Left Column */}
        <div className="space-y-6">
          {/* Health Score */}
          <div className="bg-white rounded-xl border border-sage-200 p-6 shadow-sm">
            <p className="text-xs tracking-wider uppercase font-semibold text-sage-500 mb-4">
              Health Score
            </p>
            <div className="flex flex-col sm:flex-row items-center justify-around gap-6">
              <HealthScoreRing score={plant.healthScore} size={140} />
              <div className="text-center sm:text-left">
                <p className="text-xs text-sage-400 uppercase tracking-wider font-semibold">Assessment</p>
                <p className="text-lg font-bold text-sage-800 mt-1">
                  {plant.healthScore >= 80 ? 'Healthy Condition' : plant.healthScore >= 60 ? 'Moderate Stress' : 'Critical Stress'}
                </p>
                <p className="text-xs text-sage-500 mt-1 max-w-[200px]">
                  Based on continuous ultrasonic cavitation frequency monitoring.
                </p>
              </div>
            </div>
          </div>

          {/* Current Stress Status */}
          {plant.stress && (
            <div className="bg-white rounded-xl border border-sage-200 p-6 shadow-sm">
              <p className="text-xs tracking-wider uppercase font-semibold text-sage-500 mb-4">
                Current Status
              </p>
              <div className="space-y-3.5">
                <div className="flex items-center justify-between pb-2 border-b border-sage-100">
                  <span className="text-sm text-sage-500">Stress Type</span>
                  <span className="font-semibold text-sage-800">{plant.stress.type === 'drought' ? 'Drought' : plant.stress.label}</span>
                </div>
                <div className="flex items-center justify-between pb-2 border-b border-sage-100">
                  <span className="text-sm text-sage-500">Severity</span>
                  <span className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-semibold ${severityColors[plant.stress.severity]}`}>
                    {plant.stress.severity === 'critical' ? (
                      <AlertOctagon className="w-3.5 h-3.5" />
                    ) : (
                      <AlertTriangle className="w-3.5 h-3.5" />
                    )}
                    {plant.stress.severity.charAt(0).toUpperCase() + plant.stress.severity.slice(1)}
                  </span>
                </div>
                <div className="flex items-center justify-between pb-2 border-b border-sage-100">
                  <span className="text-sm text-sage-500">Confidence</span>
                  <div className="flex items-center gap-2.5">
                    <div className="w-24 bg-sage-100 rounded-full h-2">
                      <div
                        className="h-2 rounded-full bg-sage-500 transition-all"
                        style={{ width: `${plant.stress.confidence}%` }}
                      />
                    </div>
                    <span className="font-bold text-sage-800 text-sm">{plant.stress.confidence}%</span>
                  </div>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-sage-500">Detected</span>
                  <span className="text-sage-700 text-sm font-medium">{plant.stress.detectedAt}</span>
                </div>
              </div>
            </div>
          )}

          {/* What This May Mean */}
          {plant.stress && (
            <div className="bg-cream-50/80 rounded-xl border border-cream-200/90 p-5">
              <div className="flex items-center gap-2 mb-2.5">
                <Info className="w-4 h-4 text-cream-500" />
                <p className="text-xs tracking-wider uppercase font-semibold text-sage-600">
                  What This May Mean
                </p>
              </div>
              <p className="text-sage-700 text-sm leading-relaxed">&ldquo;{plant.stress.meaning}&rdquo;</p>
            </div>
          )}

          {/* Recommended Action */}
          {plant.stress && (
            <div className="bg-mint-50/80 rounded-xl border border-mint-200/90 p-5">
              <div className="flex items-center gap-2 mb-2.5">
                <Lightbulb className="w-4 h-4 text-mint-600" />
                <p className="text-xs tracking-wider uppercase font-semibold text-sage-600">
                  Recommended Action
                </p>
              </div>
              <p className="text-sage-700 text-sm leading-relaxed">&ldquo;{plant.stress.recommendation}&rdquo;</p>
              {matchingAlert && (
                <div className="mt-4 pt-3 border-t border-mint-200/60">
                  {!isReviewed ? (
                    <button
                      onClick={() => markAlertReviewed(matchingAlert.id)}
                      className="inline-flex items-center gap-2 px-4 py-2 bg-sage-600 text-white rounded-lg hover:bg-sage-700 transition-colors text-sm font-medium shadow-xs"
                    >
                      <CheckCircle2 className="w-4 h-4" />
                      Mark as Reviewed
                    </button>
                  ) : (
                    <span className="inline-flex items-center gap-1.5 text-xs text-mint-700 font-medium">
                      <CheckCircle2 className="w-4 h-4" />
                      Alert marked as reviewed
                    </span>
                  )}
                </div>
              )}
            </div>
          )}
        </div>

        {/* Right Column */}
        <div className="space-y-6">
          {/* Ultrasonic Activity */}
          <div className="bg-white rounded-xl border border-sage-200 p-6 shadow-sm">
            <div className="flex items-center justify-between mb-4">
              <p className="text-xs tracking-wider uppercase font-semibold text-sage-500">
                Ultrasonic Activity
              </p>
              <span className="text-xs text-sage-400 font-mono">Sampling: 100 kHz</span>
            </div>
            <WaveformChart stressLevel={stressLevel} height={200} animated />
            <div className="mt-3 flex items-center justify-between text-sm">
              <div className="flex items-center gap-2">
                <Shield className="w-4 h-4 text-sage-400" />
                <span className="text-sage-500">
                  Signal Status:{' '}
                  <span className={`font-semibold ${
                    stressLevel === 'high' ? 'text-rose-500' : stressLevel === 'elevated' ? 'text-warm-600' : 'text-mint-600'
                  }`}>
                    {stressLevel === 'high' ? 'High Activity' : stressLevel === 'elevated' ? 'Elevated' : 'Normal'}
                  </span>
                </span>
              </div>
              <span className="text-xs text-sage-400">Live Acoustic Stream</span>
            </div>
          </div>

          {/* Recent Observations */}
          <div className="bg-white rounded-xl border border-sage-200 p-6 shadow-sm">
            <p className="text-xs tracking-wider uppercase font-semibold text-sage-500 mb-4">
              Recent Observations
            </p>
            <div className="space-y-0">
              {plant.observations.map((obs, i) => (
                <div key={i} className="flex items-start gap-3 relative py-3">
                  {/* Timeline line */}
                  {i < plant.observations.length - 1 && (
                    <div className="absolute left-[7px] top-7 w-0.5 h-[calc(100%-8px)] bg-sage-100" />
                  )}
                  {/* Dot */}
                  <div className={`w-3.5 h-3.5 rounded-full mt-0.5 flex-shrink-0 ${observationDotColors[obs.type]}`} />
                  {/* Content */}
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-sage-800">{obs.message}</p>
                    <div className="flex items-center gap-1 text-xs text-sage-400 mt-0.5">
                      <Clock className="w-3 h-3" />
                      {obs.time}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
