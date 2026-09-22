'use client';

import { useState, useEffect, useCallback, useRef } from 'react';
import { generateWaveformData } from '@/data/mockData';

interface WaveformChartProps {
  animated?: boolean;
  height?: number;
  stressLevel?: 'normal' | 'elevated' | 'high';
}

export function WaveformChart({ animated = true, height = 200, stressLevel = 'normal' }: WaveformChartProps) {
  const [data, setData] = useState<number[]>(() => generateWaveformData(120));
  const svgRef = useRef<SVGSVGElement>(null);

  const regenerate = useCallback(() => {
    setData(generateWaveformData(120));
  }, []);

  useEffect(() => {
    if (!animated) return;
    const interval = setInterval(regenerate, 2500);
    return () => clearInterval(interval);
  }, [animated, regenerate]);

  const strokeColor =
    stressLevel === 'high'
      ? '#e58a66'   // terracotta-400
      : stressLevel === 'elevated'
        ? '#e8b93d' // warm-500
        : '#95a680'; // sage-400

  const fillColor =
    stressLevel === 'high'
      ? 'rgba(229,138,102,0.15)'
      : stressLevel === 'elevated'
        ? 'rgba(232,185,61,0.12)'
        : 'rgba(149,166,128,0.12)';

  const width = 600;
  const padding = 4;
  const pointSpacing = (width - padding * 2) / (data.length - 1);

  const points = data
    .map((val, i) => {
      const x = padding + i * pointSpacing;
      const y = height - padding - (val / 100) * (height - padding * 2);
      return `${x},${y}`;
    })
    .join(' ');

  const areaPoints = `${padding},${height - padding} ${points} ${width - padding},${height - padding}`;

  return (
    <div className="bg-sage-50 border border-sage-200 rounded-lg p-3 overflow-hidden">
      <svg
        ref={svgRef}
        viewBox={`0 0 ${width} ${height}`}
        className="w-full"
        preserveAspectRatio="none"
        style={{ height }}
      >
        {/* Grid lines */}
        {[0.25, 0.5, 0.75].map((frac) => (
          <line
            key={frac}
            x1={padding}
            y1={height * frac}
            x2={width - padding}
            y2={height * frac}
            stroke="#d4dac9"
            strokeWidth="0.5"
            strokeDasharray="4 4"
          />
        ))}

        {/* Area fill */}
        <polygon
          points={areaPoints}
          fill={fillColor}
          className="transition-all duration-700"
        />

        {/* Waveform line */}
        <polyline
          points={points}
          fill="none"
          stroke={strokeColor}
          strokeWidth="2"
          strokeLinejoin="round"
          strokeLinecap="round"
          className="transition-all duration-700"
        />
      </svg>
    </div>
  );
}
