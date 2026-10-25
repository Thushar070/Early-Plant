'use client';

import Link from 'next/link';
import { Plant } from '@/types/plant';
import { MapPin, Clock, ChevronRight, AlertTriangle, CheckCircle2, AlertOctagon } from 'lucide-react';

interface PlantCardProps {
  plant: Plant;
}

export function PlantCard({ plant }: PlantCardProps) {
  const statusConfig = {
    healthy: {
      bg: 'bg-mint-50',
      iconBg: 'bg-mint-100',
      badge: 'bg-mint-100 text-mint-500',
      barColor: 'bg-mint-400',
      label: 'Healthy',
      Icon: CheckCircle2,
    },
    stressed: {
      bg: 'bg-white',
      iconBg: 'bg-warm-100',
      badge: 'bg-warm-100 text-warm-500',
      barColor: 'bg-warm-400',
      label: plant.stress?.label || 'Stress Detected',
      Icon: AlertTriangle,
    },
    critical: {
      bg: 'bg-white',
      iconBg: 'bg-rose-100',
      badge: 'bg-rose-100 text-rose-500',
      barColor: 'bg-rose-400',
      label: plant.stress?.label || 'Critical',
      Icon: AlertOctagon,
    },
  };

  const config = statusConfig[plant.status];
  const StatusIcon = config.Icon;
  const scoreBarColor =
    plant.healthScore >= 80
      ? 'bg-sage-400'
      : plant.healthScore >= 60
        ? 'bg-warm-400'
        : plant.healthScore >= 40
          ? 'bg-terracotta-400'
          : 'bg-rose-400';

  return (
    <Link href={`/dashboard/plants/${plant.id}`}>
      <div className="bg-white rounded-xl border border-sage-200 hover:border-sage-300 shadow-sm hover:shadow-md transition-all p-5 cursor-pointer group">
        <div className="flex items-start gap-4">
          {/* Plant Icon */}
          <div className={`flex-shrink-0 w-12 h-12 rounded-xl ${config.iconBg} flex items-center justify-center text-2xl`}>
            {plant.icon}
          </div>

          {/* Content */}
          <div className="flex-1 min-w-0">
            <div className="flex items-start justify-between gap-2">
              <div className="min-w-0">
                <h3 className="font-semibold text-sage-800 truncate">{plant.name}</h3>
                <div className="flex items-center gap-1 text-sage-500 text-sm mt-0.5">
                  <MapPin className="w-3.5 h-3.5 flex-shrink-0" />
                  <span className="truncate">{plant.location}</span>
                </div>
              </div>
              <ChevronRight className="w-5 h-5 text-sage-300 group-hover:text-sage-500 transition-colors flex-shrink-0 mt-1" />
            </div>

            {/* Status Badge */}
            <div className="mt-3">
              <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium ${config.badge}`}>
                <StatusIcon className="w-3.5 h-3.5" />
                {config.label}
              </span>
            </div>

            {/* Health Score Bar */}
            <div className="mt-3">
              <div className="flex items-center justify-between text-xs mb-1">
                <span className="text-sage-500 font-medium">Sample health score</span>
                <span className="font-semibold text-sage-700">{plant.healthScore}</span>
              </div>
              <div className="w-full bg-sage-100 rounded-full h-1.5">
                <div
                  className={`h-1.5 rounded-full ${scoreBarColor} transition-all duration-500`}
                  style={{ width: `${plant.healthScore}%` }}
                />
              </div>
            </div>

            {/* Last Monitored */}
            <div className="flex items-center gap-1 text-sage-400 text-xs mt-2.5">
              <Clock className="w-3 h-3" />
              <span>Monitored {plant.lastMonitored}</span>
            </div>
          </div>
        </div>
      </div>
    </Link>
  );
}
