import {
  Plant,
  Alert,
  HistoryEntry,
  HealthDataPoint,
  MonitoringDevice,
  StressTypeInfo,
  HowItWorksStep,
  UserSettings,
} from '@/types/plant';

// ── Plants ────────────────────────────────────────────────────────────────────

export const plants: Plant[] = [
  {
    id: 'tomato-04',
    name: 'Tomato Plant 04',
    location: 'Greenhouse A',
    status: 'stressed',
    healthScore: 61,
    lastMonitored: '3 min ago',
    icon: '🍅',
    stress: {
      type: 'drought',
      label: 'Drought Stress',
      description: 'Possible water-related stress detected.',
      severity: 'high',
      confidence: 87,
      detectedAt: '12 minutes ago',
      recommendation:
        'Check soil moisture around the plant and verify irrigation system is working properly.',
      meaning:
        'The plant is showing an acoustic pattern associated with water stress. This may indicate insufficient water supply or root zone moisture deficit.',
    },
    observations: [
      { time: '10:42 AM', message: 'Elevated sample acoustic activity', type: 'alert' },
      { time: '10:35 AM', message: 'Acoustic pattern changed', type: 'warning' },
      { time: '10:20 AM', message: 'Normal activity', type: 'normal' },
    ],
  },
  {
    id: 'tomato-01',
    name: 'Tomato Plant 01',
    location: 'Greenhouse A',
    status: 'healthy',
    healthScore: 92,
    lastMonitored: '5 min ago',
    icon: '🍅',
    observations: [
      { time: '10:40 AM', message: 'Normal sample acoustic activity', type: 'normal' },
      { time: '10:20 AM', message: 'Routine monitoring check — no anomalies', type: 'normal' },
    ],
  },
  {
    id: 'cucumber-08',
    name: 'Cucumber Plant 08',
    location: 'Greenhouse A',
    status: 'stressed',
    healthScore: 61,
    lastMonitored: '8 min ago',
    icon: '🥒',
    stress: {
      type: 'heat_stress',
      label: 'Heat Stress',
      description: 'Possible stress associated with elevated temperature.',
      severity: 'medium',
      confidence: 76,
      detectedAt: '1 hour ago',
      recommendation:
        'Check greenhouse ventilation and consider adjusting shade cloth coverage. Monitor ambient temperature.',
      meaning:
        'The plant is showing an acoustic pattern that may be associated with heat-related stress. Elevated temperatures can cause cavitation events in xylem vessels.',
    },
    observations: [
      { time: '9:55 AM', message: 'Moderate sample acoustic activity increase', type: 'warning' },
      { time: '9:40 AM', message: 'Temperature-correlated acoustic pattern', type: 'warning' },
      { time: '9:20 AM', message: 'Normal activity', type: 'normal' },
    ],
  },
  {
    id: 'wheat-12',
    name: 'Wheat Plant 12',
    location: 'Field B',
    status: 'stressed',
    healthScore: 54,
    lastMonitored: '12 min ago',
    icon: '🌾',
    stress: {
      type: 'drought',
      label: 'Drought Risk',
      description: 'Possible water-related stress developing.',
      severity: 'high',
      confidence: 72,
      detectedAt: '3 hours ago',
      recommendation:
        'Inspect field irrigation coverage. Consider soil moisture testing in the affected area.',
      meaning:
        'Acoustic emissions suggest early signs of water deficit stress. The pattern is consistent with reduced turgor pressure.',
    },
    observations: [
      { time: '10:30 AM', message: 'Persistent elevated acoustic activity', type: 'alert' },
      { time: '10:00 AM', message: 'Unusual emission pattern detected', type: 'warning' },
      { time: '9:30 AM', message: 'Slight increase in sample acoustic activity', type: 'warning' },
    ],
  },
  {
    id: 'corn-03',
    name: 'Corn Plant 03',
    location: 'Field C',
    status: 'healthy',
    healthScore: 88,
    lastMonitored: '6 min ago',
    icon: '🌽',
    observations: [
      { time: '10:38 AM', message: 'Normal sample acoustic activity', type: 'normal' },
      { time: '10:15 AM', message: 'Routine check — healthy baseline', type: 'normal' },
    ],
  },
  {
    id: 'pepper-02',
    name: 'Bell Pepper 02',
    location: 'Greenhouse B',
    status: 'healthy',
    healthScore: 95,
    lastMonitored: '4 min ago',
    icon: '🫑',
    observations: [
      { time: '10:41 AM', message: 'Normal sample acoustic activity', type: 'normal' },
    ],
  },
  {
    id: 'lettuce-06',
    name: 'Lettuce Plant 06',
    location: 'Greenhouse B',
    status: 'healthy',
    healthScore: 89,
    lastMonitored: '7 min ago',
    icon: '🥬',
    observations: [
      { time: '10:36 AM', message: 'Normal sample acoustic activity', type: 'normal' },
    ],
  },
  {
    id: 'strawberry-05',
    name: 'Strawberry 05',
    location: 'Greenhouse A',
    status: 'critical',
    healthScore: 32,
    lastMonitored: '2 min ago',
    icon: '🍓',
    stress: {
      type: 'pest_infestation',
      label: 'Possible Pest Infestation',
      description: 'Acoustic pattern associated with pest-related stress detected.',
      severity: 'critical',
      confidence: 91,
      detectedAt: '30 minutes ago',
      recommendation:
        'Immediately inspect the plant for visible pest damage. Consider isolating the affected plant and checking neighboring plants.',
      meaning:
        'The acoustic emission pattern is consistent with mechanical damage caused by pest activity. The high frequency of emissions suggests active damage.',
    },
    observations: [
      { time: '10:43 AM', message: 'Example: rapid burst acoustic emissions', type: 'alert' },
      { time: '10:30 AM', message: 'Highly irregular acoustic pattern', type: 'alert' },
      { time: '10:15 AM', message: 'Increasing emission frequency', type: 'warning' },
      { time: '10:00 AM', message: 'Unusual acoustic pattern detected', type: 'warning' },
    ],
  },
  {
    id: 'basil-09',
    name: 'Basil Plant 09',
    location: 'Greenhouse B',
    status: 'healthy',
    healthScore: 91,
    lastMonitored: '9 min ago',
    icon: '🌿',
    observations: [
      { time: '10:35 AM', message: 'Normal activity', type: 'normal' },
    ],
  },
  {
    id: 'carrot-07',
    name: 'Carrot Plant 07',
    location: 'Field B',
    status: 'healthy',
    healthScore: 86,
    lastMonitored: '11 min ago',
    icon: '🥕',
    observations: [
      { time: '10:33 AM', message: 'Normal sample acoustic activity', type: 'normal' },
    ],
  },
];

// ── Dashboard Summary ─────────────────────────────────────────────────────────

export const dashboardSummary = {
  plantsMonitored: 24,
  healthyPlants: 18,
  plantsUnderStress: 4,
  criticalAlerts: 2,
  overallHealthScore: 82,
  overallStatus: 'Good' as const,
};

// ── Alerts ────────────────────────────────────────────────────────────────────

export const alerts: Alert[] = [
  {
    id: 'alert-1',
    plantId: 'strawberry-05',
    plantName: 'Strawberry 05',
    severity: 'critical',
    stressType: 'pest_infestation',
    stressLabel: 'Possible pest infestation',
    message: 'Acoustic pattern associated with pest activity detected in Strawberry 05.',
    location: 'Greenhouse A',
    timestamp: '30 min ago',
    confidence: 91,
    meaning: 'The acoustic emission pattern is consistent with mechanical damage caused by pest activity.',
    recommendation: 'Immediately inspect the plant for visible pest damage. Consider isolating the affected plant.',
    reviewed: false,
  },
  {
    id: 'alert-2',
    plantId: 'tomato-04',
    plantName: 'Tomato Plant 04',
    severity: 'high',
    stressType: 'drought',
    stressLabel: 'Drought stress detected',
    message: 'Drought stress detected in Tomato Plant 04.',
    location: 'Greenhouse A',
    timestamp: '12 min ago',
    confidence: 87,
    meaning: 'The plant is showing an acoustic pattern associated with water stress.',
    recommendation: 'Check soil moisture around the plant and verify irrigation.',
    reviewed: false,
  },
  {
    id: 'alert-3',
    plantId: 'wheat-12',
    plantName: 'Wheat Plant 12',
    severity: 'low',
    stressType: 'drought',
    stressLabel: 'Unusual acoustic activity',
    message: 'Unusual acoustic activity detected in Wheat Plant 12.',
    location: 'Field B',
    timestamp: '3 hours ago',
    confidence: 68,
    meaning: 'The plant is showing an acoustic pattern associated with early water stress or transpiration fluctuations.',
    recommendation: 'Inspect field irrigation coverage. Consider soil moisture testing.',
    reviewed: false,
  },
  {
    id: 'alert-4',
    plantId: 'cucumber-08',
    plantName: 'Cucumber Plant 08',
    severity: 'medium',
    stressType: 'heat_stress',
    stressLabel: 'Possible heat stress',
    message: 'Possible heat stress in Cucumber Plant 08.',
    location: 'Greenhouse A',
    timestamp: '1 hour ago',
    confidence: 76,
    meaning: 'The plant is showing an acoustic pattern that may be associated with heat-related stress.',
    recommendation: 'Check greenhouse ventilation and consider adjusting shade cloth coverage.',
    reviewed: false,
  },
  {
    id: 'alert-5',
    plantId: 'corn-03',
    plantName: 'Corn Plant 03',
    severity: 'low',
    stressType: 'nutrient_deficiency',
    stressLabel: 'Unusual acoustic activity',
    message: 'Brief unusual acoustic activity detected in Corn Plant 03.',
    location: 'Field C',
    timestamp: '5 hours ago',
    confidence: 42,
    meaning: 'A brief, low-intensity acoustic anomaly was recorded. This may not indicate significant stress.',
    recommendation: 'No immediate action required. Continue monitoring for recurring patterns.',
    reviewed: true,
  },
];

// ── History ───────────────────────────────────────────────────────────────────

export const historyEntries: HistoryEntry[] = [
  { date: 'Sep 22', plantId: 'strawberry-05', plantName: 'Strawberry 05', stressType: 'pest_infestation', stressLabel: 'Pest Activity', severity: 'critical', confidence: 91 },
  { date: 'Sep 22', plantId: 'tomato-04', plantName: 'Tomato Plant 04', stressType: 'drought', stressLabel: 'Drought', severity: 'high', confidence: 87 },
  { date: 'Sep 22', plantId: 'wheat-12', plantName: 'Wheat Plant 12', stressType: 'drought', stressLabel: 'Drought', severity: 'high', confidence: 72 },
  { date: 'Sep 21', plantId: 'cucumber-08', plantName: 'Cucumber Plant 08', stressType: 'heat_stress', stressLabel: 'Heat Stress', severity: 'medium', confidence: 76 },
  { date: 'Sep 20', plantId: 'tomato-04', plantName: 'Tomato Plant 04', stressType: 'drought', stressLabel: 'Drought', severity: 'medium', confidence: 64 },
  { date: 'Sep 19', plantId: 'lettuce-06', plantName: 'Lettuce Plant 06', stressType: 'nutrient_deficiency', stressLabel: 'Nutrient Deficiency', severity: 'low', confidence: 51 },
  { date: 'Sep 18', plantId: 'corn-03', plantName: 'Corn Plant 03', stressType: 'mechanical_damage', stressLabel: 'Mechanical Damage', severity: 'low', confidence: 45 },
  { date: 'Sep 17', plantId: 'strawberry-05', plantName: 'Strawberry 05', stressType: 'heat_stress', stressLabel: 'Heat Stress', severity: 'medium', confidence: 68 },
  { date: 'Sep 15', plantId: 'wheat-12', plantName: 'Wheat Plant 12', stressType: 'drought', stressLabel: 'Drought', severity: 'low', confidence: 53 },
];

// ── Health Chart Data ─────────────────────────────────────────────────────────

export const healthData24h: HealthDataPoint[] = [
  { time: '12 AM', score: 88, label: '12 AM' },
  { time: '2 AM', score: 87, label: '2 AM' },
  { time: '4 AM', score: 87, label: '4 AM' },
  { time: '6 AM', score: 86, label: '6 AM' },
  { time: '8 AM', score: 85, label: '8 AM' },
  { time: '10 AM', score: 83, label: '10 AM' },
  { time: '12 PM', score: 82, label: '12 PM' },
  { time: '2 PM', score: 80, label: '2 PM' },
  { time: '4 PM', score: 79, label: '4 PM' },
  { time: '6 PM', score: 81, label: '6 PM' },
  { time: '8 PM', score: 82, label: '8 PM' },
  { time: '10 PM', score: 82, label: '10 PM' },
];

export const healthData7d: HealthDataPoint[] = [
  { time: 'Mon', score: 89, label: 'Mon' },
  { time: 'Tue', score: 87, label: 'Tue' },
  { time: 'Wed', score: 85, label: 'Wed' },
  { time: 'Thu', score: 83, label: 'Thu' },
  { time: 'Fri', score: 84, label: 'Fri' },
  { time: 'Sat', score: 83, label: 'Sat' },
  { time: 'Sun', score: 82, label: 'Sun' },
];

export const healthData30d: HealthDataPoint[] = [
  { time: 'Aug 24', score: 92, label: 'Aug 24' },
  { time: 'Aug 27', score: 91, label: 'Aug 27' },
  { time: 'Aug 30', score: 90, label: 'Aug 30' },
  { time: 'Sep 02', score: 89, label: 'Sep 02' },
  { time: 'Sep 05', score: 88, label: 'Sep 05' },
  { time: 'Sep 08', score: 87, label: 'Sep 08' },
  { time: 'Sep 11', score: 86, label: 'Sep 11' },
  { time: 'Sep 14', score: 85, label: 'Sep 14' },
  { time: 'Sep 17', score: 84, label: 'Sep 17' },
  { time: 'Sep 20', score: 83, label: 'Sep 20' },
  { time: 'Sep 22', score: 82, label: 'Sep 22' },
];

// ── Monitoring ────────────────────────────────────────────────────────────────

export const monitoringDevice: MonitoringDevice = {
  id: 'node-01',
  name: 'Demo monitor label',
  status: 'connected',
  plantsConnected: 8,
  lastSignal: '3 seconds ago',
};

// ── Settings ──────────────────────────────────────────────────────────────────

export const defaultUserSettings: UserSettings = {
  name: 'Alex Green',
  email: 'alex@plantsense.ai',
  notifications: {
    stressAlerts: true,
    criticalAlerts: true,
    dailySummary: false,
  },
  monitoringInterval: '30s',
};

// ── Stress Types Info ─────────────────────────────────────────────────────────

export const stressTypes: StressTypeInfo[] = [
  {
    type: 'drought',
    label: 'Drought',
    description: 'Possible water-related stress. Acoustic emissions may indicate cavitation events in xylem vessels due to insufficient water.',
    icon: 'droplets',
  },
  {
    type: 'heat_stress',
    label: 'Heat Stress',
    description: 'Possible stress associated with elevated temperature. High temperatures can cause increased acoustic emissions from plant tissues.',
    icon: 'thermometer',
  },
  {
    type: 'mechanical_damage',
    label: 'Mechanical Damage',
    description: 'Possible physical damage to the plant. Sudden acoustic bursts may indicate tissue breakage or external force impact.',
    icon: 'shield-alert',
  },
  {
    type: 'nutrient_deficiency',
    label: 'Nutrient Deficiency',
    description: 'Possible stress associated with insufficient nutrients. Subtle changes in acoustic patterns may correlate with nutrient uptake issues.',
    icon: 'flask-conical',
  },
  {
    type: 'pest_infestation',
    label: 'Pest Infestation',
    description: 'Possible acoustic pattern associated with pest-related stress. Repeated mechanical micro-damage from feeding activity can generate characteristic emissions.',
    icon: 'bug',
  },
];

// ── How It Works ──────────────────────────────────────────────────────────────

export const howItWorksSteps: HowItWorksStep[] = [
  {
    step: 1,
    title: 'Plant-related audio is recorded',
    description: 'The prototype explores whether recorded acoustic signals may contain patterns associated with plant stress.',
    icon: 'sprout',
  },
  {
    step: 2,
    title: 'Sensor captures the acoustic signal',
    description: 'This dashboard uses sample data; no physical sensor or live recording is connected.',
    icon: 'radio',
  },
  {
    step: 3,
    title: 'AI analyzes the signal',
    description: 'ML experiments transform recordings into features such as log-Mel spectrograms.',
    icon: 'brain',
  },
  {
    step: 4,
    title: 'Stress pattern is classified',
    description: 'Research experiments compare five target classes, with low recorded validation performance.',
    icon: 'scan-search',
  },
  {
    step: 5,
    title: 'User receives an alert and suggested action',
    description: 'The prototype dashboard displays illustrative sample alerts and recommendations, not verified predictions.',
    icon: 'bell-ring',
  },
];

// ── Waveform Mock Data ────────────────────────────────────────────────────────

export function generateWaveformData(points: number = 100): number[] {
  const data: number[] = [];
  for (let i = 0; i < points; i++) {
    const base = Math.sin(i * 0.15) * 30;
    const noise = (Math.random() - 0.5) * 20;
    const spike = i > 60 && i < 75 ? Math.sin((i - 60) * 0.4) * 40 : 0;
    data.push(base + noise + spike + 50);
  }
  return data;
}

export function generateFrequencyData(): { freq: string; value: number }[] {
  return [
    { freq: 'Bin 1', value: 25 },
    { freq: 'Bin 2', value: 45 },
    { freq: 'Bin 3', value: 72 },
    { freq: 'Bin 4', value: 58 },
    { freq: 'Bin 5', value: 38 },
    { freq: 'Bin 6', value: 22 },
    { freq: 'Bin 7', value: 15 },
    { freq: 'Bin 8', value: 8 },
  ];
}
