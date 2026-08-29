// =============================================================================
// MIT License
// Copyright (c) 2026 Aparavi Software AG
// =============================================================================

/** Aggregated content for the Home dashboard + Reports screens. */

import type { ChartSeries, DonutSlice, StatItem } from '../types';
import { CHART, SERIES } from './palette';
import { regionCounts, riskDistribution } from './stores';

export const KPIS: StatItem[] = [
	{
		id: 'compliance',
		label: 'Compliance Score',
		value: 92,
		countTo: 92,
		unit: '/100',
		tone: 'good',
		icon: 'shield-check',
		delta: { label: '4 pts vs last month', direction: 'up' },
		caption: 'network average',
		trend: [83, 85, 84, 88, 89, 91, 92],
	},
	{
		id: 'high-risk',
		label: 'High Risk Stores',
		value: 12,
		countTo: 12,
		tone: 'risk',
		icon: 'alert-triangle',
		delta: { label: '2 since last week', direction: 'up', invert: true },
		caption: 'score below 75',
		trend: [7, 8, 9, 9, 10, 11, 12],
	},
	{
		id: 'pending',
		label: 'Pending Inspections',
		value: 8,
		countTo: 8,
		tone: 'warn',
		icon: 'clipboard-clock',
		delta: { label: '3 overdue', direction: 'flat' },
		caption: 'due within 7 days',
		trend: [12, 11, 10, 9, 9, 8, 8],
	},
	{
		id: 'monitored',
		label: 'Stores Monitored',
		value: 156,
		countTo: 156,
		tone: 'violet',
		icon: 'storefront',
		delta: { label: '100% reporting', direction: 'up' },
		caption: 'across 5 regions',
		trend: [140, 144, 147, 150, 152, 154, 156],
	},
];

/** 12-month compliance vs. risk index. */
export const TREND_MONTHS = ['Sep', 'Oct', 'Nov', 'Dec', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug'];

export const COMPLIANCE_TREND: ChartSeries[] = [
	{
		name: 'Compliance',
		color: SERIES.compliance,
		points: [82, 83, 81, 84, 85, 86, 85, 87, 88, 89, 90, 92],
	},
	{
		name: 'Target',
		color: SERIES.target,
		points: [88, 88, 88, 88, 88, 88, 88, 88, 88, 88, 88, 88],
	},
];

/** Network-wide risk exposure index (higher = worse). */
export const RISK_INDEX_TREND: ChartSeries[] = [
	{
		name: 'Risk index',
		color: SERIES.risk,
		points: [41, 39, 44, 40, 37, 35, 36, 33, 31, 30, 28, 24],
	},
];

/** Risk categories across the network — donut. */
export const RISK_CATEGORY_SLICES: DonutSlice[] = [
	{ label: 'Staff Hygiene', value: 34, color: CHART.blue },
	{ label: 'Food Storage', value: 27, color: CHART.violet },
	{ label: 'Kitchen Cleanliness', value: 21, color: CHART.teal },
	{ label: 'Branding', value: 11, color: CHART.amber },
	{ label: 'Pest Control', value: 7, color: CHART.red },
];

/** Store risk mix from the live store list. */
export function riskMixSlices(): DonutSlice[] {
	const d = riskDistribution();
	return [
		{ label: 'Low', value: d.low, color: CHART.green },
		{ label: 'Medium', value: d.medium, color: CHART.amber },
		{ label: 'High', value: d.high, color: CHART.red },
		{ label: 'Critical', value: d.critical, color: '#a81430' },
	];
}

/** Store distribution by region — bar groups. */
export function storeDistribution() {
	return regionCounts().map((r) => ({
		label: r.region,
		bars: [{ value: r.count, color: CHART.blue }],
	}));
}

/** Inspection completion by week — planned vs completed. */
export const INSPECTION_COMPLETION = [
	{ label: 'W-4', bars: [{ value: 38, color: CHART.slate, name: 'Planned' }, { value: 35, color: CHART.blue, name: 'Done' }] },
	{ label: 'W-3', bars: [{ value: 40, color: CHART.slate, name: 'Planned' }, { value: 39, color: CHART.blue, name: 'Done' }] },
	{ label: 'W-2', bars: [{ value: 44, color: CHART.slate, name: 'Planned' }, { value: 41, color: CHART.blue, name: 'Done' }] },
	{ label: 'W-1', bars: [{ value: 46, color: CHART.slate, name: 'Planned' }, { value: 46, color: CHART.blue, name: 'Done' }] },
	{ label: 'This', bars: [{ value: 48, color: CHART.slate, name: 'Planned' }, { value: 34, color: CHART.blue, name: 'Done' }] },
];

/** Complaint trend by week — violet columns. */
export const COMPLAINT_TREND: ChartSeries[] = [
	{ name: 'Complaints', color: SERIES.complaints, points: [9, 12, 8, 14, 11, 7, 6, 5] },
];
export const COMPLAINT_WEEKS = ['Jul 07', 'Jul 14', 'Jul 21', 'Jul 28', 'Aug 04', 'Aug 11', 'Aug 18', 'Aug 25'];

/** Headline briefing shown under the welcome banner. */
export const OVERNIGHT_BRIEFING =
	'AI vision reviewed 34 inspection photos overnight, cleared 21 automatically and flagged 4 alerts for your review.';
