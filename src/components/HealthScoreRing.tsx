'use client';

import { useMemo } from 'react';

interface HealthScoreRingProps {
  score: number;
  size?: number;
  strokeWidth?: number;
}

export function HealthScoreRing({ score, size = 160, strokeWidth = 10 }: HealthScoreRingProps) {
  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (score / 100) * circumference;

  const color = useMemo(() => {
    if (score >= 80) return { stroke: '#778c63', text: 'text-sage-600' }; // sage-500
    if (score >= 60) return { stroke: '#e8b93d', text: 'text-warm-500' }; // warm-500
    if (score >= 40) return { stroke: '#e58a66', text: 'text-terracotta-400' };
    return { stroke: '#e07a7a', text: 'text-rose-400' };
  }, [score]);

  return (
    <div className="relative inline-flex items-center justify-center" style={{ width: size, height: size }}>
      <svg width={size} height={size} className="-rotate-90">
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke="#e8ebe3"
          strokeWidth={strokeWidth}
        />
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke={color.stroke}
          strokeWidth={strokeWidth}
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          strokeLinecap="round"
          className="transition-all duration-1000 ease-out"
        />
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <span className={`text-3xl font-bold ${color.text}`}>{score}</span>
        <span className="text-sm text-sage-400">/100</span>
      </div>
    </div>
  );
}
