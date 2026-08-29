// =============================================================================
// MIT License
// Copyright (c) 2026 Aparavi Software AG
// =============================================================================

/** Mock content for the Home Dashboard — swap for live API data later. */

import type { AlertItem, NavItem, StatItem } from '../../types';

export const STATS: StatItem[] = [
	{
		id: 'compliance',
		label: 'Compliance Score',
		value: 92,
		unit: '/100',
		tone: 'good',
		icon: 'shield-check',
		delta: { label: '4 pts vs last month', direction: 'up' },
		caption: 'network average',
		trend: [78, 80, 79, 84, 86, 90, 92],
	},
	{
		id: 'high-risk',
		label: 'High Risk Stores',
		value: 12,
		tone: 'risk',
		icon: 'alert-triangle',
		delta: { label: '2 since last week', direction: 'up' },
		caption: 'score below 70',
		trend: [6, 7, 9, 8, 10, 11, 12],
	},
	{
		id: 'pending',
		label: 'Pending Inspections',
		value: 8,
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
		tone: 'info',
		icon: 'storefront',
		delta: { label: '100% reporting', direction: 'up' },
		caption: 'across 4 regions',
		trend: [140, 144, 147, 150, 152, 154, 156],
	},
];

export const ALERTS: AlertItem[] = [
	{
		id: 'a1',
		title: 'Dirty Kitchen Floor',
		location: 'Store #204 · Riverside Plaza',
		timeAgo: '12 min ago',
		level: 'high',
		icon: 'droplet',
		aiFlagged: true,
	},
	{
		id: 'a2',
		title: 'Missing Gloves',
		location: 'Store #087 · Downtown Center',
		timeAgo: '1 hr ago',
		level: 'medium',
		icon: 'glove',
		aiFlagged: true,
	},
	{
		id: 'a3',
		title: 'Expired Food Label',
		location: 'Store #133 · Airport Terminal C',
		timeAgo: '3 hr ago',
		level: 'critical',
		icon: 'price-tag',
		aiFlagged: true,
	},
];

export const NAV_ITEMS: NavItem[] = [
	{ id: 'home', label: 'Home', icon: 'home' },
	{ id: 'inspections', label: 'Inspections', icon: 'clipboard-list' },
	{ id: 'reports', label: 'Reports', icon: 'chart' },
	{ id: 'profile', label: 'Profile', icon: 'user' },
];
