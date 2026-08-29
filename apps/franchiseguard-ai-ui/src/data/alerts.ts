// =============================================================================
// MIT License
// Copyright (c) 2026 Aparavi Software AG
// =============================================================================

import type { AlertItem, ManagerAlert } from '../types';

/** Priority queue for the Manager Alerts screen. */
export const MANAGER_ALERTS: ManagerAlert[] = [
	{
		id: 'ma-501',
		title: 'Cold-hold unit above safe range',
		storeName: 'Burger Hub',
		storeCode: '#133',
		region: 'Airport',
		level: 'critical',
		category: 'Food Storage',
		icon: 'thermometer',
		raisedAt: '18 min ago',
		detail:
			'AI vision read the display thermometer at 9°C during the lunch push. Two prior cold-chain flags in 30 days. Franchisee not yet responded.',
		aiConfidence: 0.94,
		sla: 'Action due in 2h',
		status: 'open',
	},
	{
		id: 'ma-502',
		title: 'Repeat glove-use violation in prep zone',
		storeName: 'Wok This Way',
		storeCode: '#141',
		region: 'Airport',
		level: 'critical',
		category: 'Staff Hygiene',
		icon: 'glove',
		raisedAt: '1 hr ago',
		detail:
			'Third bare-hands detection this cycle. Pattern suggests a training gap on the evening shift rather than a one-off.',
		aiConfidence: 0.91,
		sla: 'Action due in 4h',
		status: 'open',
	},
	{
		id: 'ma-503',
		title: 'Blocked handwash sink during service',
		storeName: 'Pizza Planet',
		storeCode: '#204',
		region: 'Riverside',
		level: 'high',
		category: 'Staff Hygiene',
		icon: 'droplet',
		raisedAt: '3 hr ago',
		detail:
			'Handwash basin stacked with utensils in two consecutive photo uploads. Store is already on the watch list.',
		aiConfidence: 0.88,
		sla: 'Action due today',
		status: 'ack',
	},
	{
		id: 'ma-504',
		title: 'Rear-door pest proofing gap',
		storeName: 'Grill House 12',
		storeCode: '#189',
		region: 'Harbor',
		level: 'medium',
		category: 'Pest Control',
		icon: 'bug',
		raisedAt: '6 hr ago',
		detail: 'Daylight visible under the rear door. No brush seal fitted. Contractor visit due Friday.',
		aiConfidence: 0.79,
		sla: 'Action due in 3 days',
		status: 'scheduled',
	},
	{
		id: 'ma-505',
		title: 'Legacy signage on menu board',
		storeName: 'The Roasted Bean',
		storeCode: '#092',
		region: 'Westside',
		level: 'medium',
		category: 'Branding Compliance',
		icon: 'award',
		raisedAt: '1 day ago',
		detail:
			'Superseded logo lockup detected. Brand kit refresh not actioned since the franchise changed hands.',
		aiConfidence: 0.73,
		sla: 'Action due in 14 days',
		status: 'open',
	},
	{
		id: 'ma-506',
		title: 'Uncovered product on make table',
		storeName: 'FreshBowl Kitchen',
		storeCode: '#087',
		region: 'Downtown',
		level: 'medium',
		category: 'Food Storage',
		icon: 'package',
		raisedAt: '1 day ago',
		detail: 'Open tray with no active service in frame. First occurrence for this location.',
		aiConfidence: 0.81,
		sla: 'Action due in 2 days',
		status: 'open',
	},
];

/** Compact alert feed for the Home dashboard. */
export const RECENT_ALERTS: AlertItem[] = [
	{
		id: 'a1',
		title: 'Dirty Kitchen Floor',
		location: 'Store #204 · Pizza Planet',
		timeAgo: '12 min ago',
		level: 'high',
		icon: 'droplet',
		aiFlagged: true,
	},
	{
		id: 'a2',
		title: 'Missing Gloves',
		location: 'Store #141 · Wok This Way',
		timeAgo: '1 hr ago',
		level: 'critical',
		icon: 'glove',
		aiFlagged: true,
	},
	{
		id: 'a3',
		title: 'Expired Food Label',
		location: 'Store #133 · Burger Hub',
		timeAgo: '3 hr ago',
		level: 'critical',
		icon: 'price-tag',
		aiFlagged: true,
	},
	{
		id: 'a4',
		title: 'Non-compliant Signage',
		location: 'Store #092 · The Roasted Bean',
		timeAgo: '5 hr ago',
		level: 'medium',
		icon: 'award',
		aiFlagged: true,
	},
];

export const managerAlertById = (id: string): ManagerAlert | undefined =>
	MANAGER_ALERTS.find((a) => a.id === id);
