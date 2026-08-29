// =============================================================================
// MIT License
// Copyright (c) 2026 Aparavi Software AG
// =============================================================================

/** Barrel for the mock data layer — swap these modules for live APIs later. */

export { MANAGER } from './manager';
export { CHART, SERIES } from './palette';
export {
	STORES,
	REGIONS,
	storeById,
	riskDistribution,
	regionCounts,
} from './stores';
export { CHECKLIST } from './checklist';
export { VIOLATION_TYPES, violationById } from './violations';
export {
	INSPECTIONS,
	TODAY_SCHEDULE,
	todaysInspections,
	inspectionsForStore,
} from './inspections';
export { MANAGER_ALERTS, RECENT_ALERTS, managerAlertById } from './alerts';
export {
	KPIS,
	TREND_MONTHS,
	COMPLIANCE_TREND,
	RISK_INDEX_TREND,
	RISK_CATEGORY_SLICES,
	riskMixSlices,
	storeDistribution,
	INSPECTION_COMPLETION,
	COMPLAINT_TREND,
	COMPLAINT_WEEKS,
	OVERNIGHT_BRIEFING,
} from './dashboard';
export { SAVED_REPORTS, reportForStore, type ReportSummary } from './reports';
