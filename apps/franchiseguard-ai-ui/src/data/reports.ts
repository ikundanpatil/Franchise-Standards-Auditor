// =============================================================================
// MIT License
// Copyright (c) 2026 Aparavi Software AG
// =============================================================================

import type { ComplianceReport, RiskLevel, Severity } from '../types';
import { composeAnalysis, composeReport } from '../lib/ai';
import { MANAGER } from './manager';
import { storeById } from './stores';

export interface ReportSummary {
	id: string;
	ref: string;
	storeId: string;
	storeName: string;
	storeCode: string;
	date: string;
	riskScore: number;
	risk: RiskLevel;
	grade: string;
	counts: Record<Severity, number>;
	inspector: string;
}

/** Previously generated reports for the Reports tab. Newest first. */
export const SAVED_REPORTS: ReportSummary[] = [
	{
		id: 'rep-9042',
		ref: 'FG-REP-0829-4471',
		storeId: 's-133',
		storeName: 'Burger Hub',
		storeCode: '#133',
		date: '2026-08-29T09:12:00',
		riskScore: 82,
		risk: 'critical',
		grade: 'D',
		counts: { minor: 1, major: 3, critical: 3 },
		inspector: MANAGER.name,
	},
	{
		id: 'rep-9041',
		ref: 'FG-REP-0828-3310',
		storeId: 's-204',
		storeName: 'Pizza Planet',
		storeCode: '#204',
		date: '2026-08-28T16:47:00',
		riskScore: 61,
		risk: 'high',
		grade: 'C',
		counts: { minor: 2, major: 2, critical: 1 },
		inspector: MANAGER.name,
	},
	{
		id: 'rep-9040',
		ref: 'FG-REP-0828-2984',
		storeId: 's-141',
		storeName: 'Wok This Way',
		storeCode: '#141',
		date: '2026-08-28T11:20:00',
		riskScore: 58,
		risk: 'high',
		grade: 'C+',
		counts: { minor: 1, major: 3, critical: 1 },
		inspector: 'R. Delgado',
	},
	{
		id: 'rep-9039',
		ref: 'FG-REP-0827-1750',
		storeId: 's-087',
		storeName: 'FreshBowl Kitchen',
		storeCode: '#087',
		date: '2026-08-27T14:31:00',
		riskScore: 34,
		risk: 'medium',
		grade: 'B',
		counts: { minor: 2, major: 1, critical: 0 },
		inspector: MANAGER.name,
	},
	{
		id: 'rep-9038',
		ref: 'FG-REP-0826-1194',
		storeId: 's-092',
		storeName: 'The Roasted Bean',
		storeCode: '#092',
		date: '2026-08-26T15:38:00',
		riskScore: 47,
		risk: 'high',
		grade: 'C+',
		counts: { minor: 1, major: 2, critical: 0 },
		inspector: MANAGER.name,
	},
	{
		id: 'rep-9037',
		ref: 'FG-REP-0824-0928',
		storeId: 's-201',
		storeName: 'StarBrew Cafe',
		storeCode: '#201',
		date: '2026-08-24T09:52:00',
		riskScore: 6,
		risk: 'low',
		grade: 'A',
		counts: { minor: 0, major: 0, critical: 0 },
		inspector: MANAGER.name,
	},
];

/** Compose a full report on demand for a saved summary (detail view). */
export function reportForStore(storeId: string): ComplianceReport | null {
	const store = storeById(storeId);
	if (!store) return null;
	const analysis = composeAnalysis(store);
	return composeReport(analysis, store, MANAGER.name);
}
