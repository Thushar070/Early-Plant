import {
  Plant,
  Alert,
  HistoryEntry,
  HealthDataPoint,
  StressSeverity,
} from '@/types/plant';
import {
  plants as allPlants,
  alerts as allAlerts,
  historyEntries,
  healthData24h,
  healthData7d,
  healthData30d,
  dashboardSummary,
  monitoringDevice,
  stressTypes,
  howItWorksSteps,
  defaultUserSettings,
} from '@/data/mockData';

// ── Plant Service ─────────────────────────────────────────────────────────────

export function getPlants(): Plant[] {
  return allPlants;
}

export function getPlantById(id: string): Plant | undefined {
  return allPlants.find((p) => p.id === id);
}

export function getFeaturedPlants(): Plant[] {
  // Return a mix of stressed and healthy plants for the dashboard
  return [
    allPlants.find((p) => p.id === 'tomato-01')!,
    allPlants.find((p) => p.id === 'cucumber-08')!,
    allPlants.find((p) => p.id === 'wheat-12')!,
    allPlants.find((p) => p.id === 'corn-03')!,
  ];
}

// ── Alert Service ─────────────────────────────────────────────────────────────

let alertState = allAlerts.map((a) => ({ ...a }));

export function getAlerts(severity?: StressSeverity): Alert[] {
  if (!severity) return alertState;
  return alertState.filter((a) => a.severity === severity);
}

export function getAlertById(id: string): Alert | undefined {
  return alertState.find((a) => a.id === id);
}

export function markAlertReviewed(id: string): void {
  alertState = alertState.map((a) =>
    a.id === id ? { ...a, reviewed: true } : a
  );
}

export function getUnreviewedAlertCount(): number {
  return alertState.filter((a) => !a.reviewed).length;
}

export function resetAlerts(): void {
  alertState = allAlerts.map((a) => ({ ...a }));
}

// ── History Service ───────────────────────────────────────────────────────────

export function getHistoryEntries(): HistoryEntry[] {
  return historyEntries;
}

export function getHealthData(range: '24h' | '7d' | '30d'): HealthDataPoint[] {
  switch (range) {
    case '24h':
      return healthData24h;
    case '7d':
      return healthData7d;
    case '30d':
      return healthData30d;
    default:
      return healthData7d;
  }
}

// ── Dashboard Service ─────────────────────────────────────────────────────────

export function getDashboardSummary() {
  return dashboardSummary;
}

// ── Monitoring Service ────────────────────────────────────────────────────────

export function getMonitoringDevice() {
  return monitoringDevice;
}

// ── Info Service ──────────────────────────────────────────────────────────────

export function getStressTypes() {
  return stressTypes;
}

export function getHowItWorksSteps() {
  return howItWorksSteps;
}

// ── Settings Service ──────────────────────────────────────────────────────────

export function getDefaultSettings() {
  return { ...defaultUserSettings };
}
