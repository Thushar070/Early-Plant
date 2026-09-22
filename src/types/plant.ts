export type StressSeverity = 'critical' | 'high' | 'medium' | 'low';

export type StressType =
  | 'drought'
  | 'heat_stress'
  | 'mechanical_damage'
  | 'nutrient_deficiency'
  | 'pest_infestation';

export type PlantStatus = 'healthy' | 'stressed' | 'critical';

export interface StressInfo {
  type: StressType;
  label: string;
  description: string;
  severity: StressSeverity;
  confidence: number;
  detectedAt: string;
  recommendation: string;
  meaning: string;
}

export interface Observation {
  time: string;
  message: string;
  type: 'normal' | 'warning' | 'alert';
}

export interface Plant {
  id: string;
  name: string;
  location: string;
  status: PlantStatus;
  healthScore: number;
  lastMonitored: string;
  icon: string;
  stress?: StressInfo;
  observations: Observation[];
}

export interface Alert {
  id: string;
  plantId: string;
  plantName: string;
  severity: StressSeverity;
  stressType: StressType;
  stressLabel: string;
  message: string;
  location: string;
  timestamp: string;
  confidence: number;
  meaning: string;
  recommendation: string;
  reviewed: boolean;
}

export interface HistoryEntry {
  date: string;
  plantId: string;
  plantName: string;
  stressType: StressType;
  stressLabel: string;
  severity: StressSeverity;
  confidence: number;
}

export interface HealthDataPoint {
  time: string;
  score: number;
  label: string;
}

export interface MonitoringDevice {
  id: string;
  name: string;
  status: 'connected' | 'disconnected';
  plantsConnected: number;
  lastSignal: string;
}

export interface NotificationSettings {
  stressAlerts: boolean;
  criticalAlerts: boolean;
  dailySummary: boolean;
}

export interface UserSettings {
  name: string;
  email: string;
  notifications: NotificationSettings;
  monitoringInterval: string;
}

export interface StressTypeInfo {
  type: StressType;
  label: string;
  description: string;
  icon: string;
}

export interface HowItWorksStep {
  step: number;
  title: string;
  description: string;
  icon: string;
}
