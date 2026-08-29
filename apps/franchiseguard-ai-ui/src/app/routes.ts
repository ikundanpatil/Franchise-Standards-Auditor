// =============================================================================
// MIT License
// Copyright (c) 2026 Aparavi Software AG
// =============================================================================

/** Screen registry + bottom-nav configuration for the navigator. */

import type { AnalysisResult, ComplianceReport, IconName, NavItem } from '../types';

export type ScreenName =
	| 'splash'
	| 'login'
	| 'home'
	| 'inspections'
	| 'upload'
	| 'analysis'
	| 'report'
	| 'memory'
	| 'alerts'
	| 'reports'
	| 'profile';

/** Payload carried between screens. All fields optional. */
export interface NavParams {
	storeId?: string;
	alertId?: string;
	reportId?: string;
	analysis?: AnalysisResult;
	report?: ComplianceReport;
	/** Preselected checklist / focus area passed into the upload flow. */
	focus?: string;
}

export type TabId = 'home' | 'inspections' | 'reports' | 'profile';

export const TABS: NavItem[] = [
	{ id: 'home', label: 'Home', icon: 'home' },
	{ id: 'inspections', label: 'Inspections', icon: 'clipboard-list' },
	{ id: 'reports', label: 'Reports', icon: 'chart' },
	{ id: 'profile', label: 'Profile', icon: 'user' },
];

/** Which tab should read as active while a given screen is on top. */
export const SCREEN_TAB: Record<ScreenName, TabId | null> = {
	splash: null,
	login: null,
	home: 'home',
	inspections: 'inspections',
	upload: 'inspections',
	analysis: 'inspections',
	report: 'reports',
	memory: 'inspections',
	alerts: 'home',
	reports: 'reports',
	profile: 'profile',
};

/** The screen a tap on each tab lands on. */
export const TAB_ROOT: Record<TabId, ScreenName> = {
	home: 'home',
	inspections: 'inspections',
	reports: 'reports',
	profile: 'profile',
};

/** Screens that render inside the app chrome (header + bottom nav). */
export const CHROME_SCREENS: ReadonlySet<ScreenName> = new Set<ScreenName>([
	'home',
	'inspections',
	'reports',
	'profile',
]);

export interface ScreenMeta {
	title: string;
	icon: IconName;
}

export const SCREEN_META: Partial<Record<ScreenName, ScreenMeta>> = {
	upload: { title: 'New Inspection', icon: 'camera' },
	analysis: { title: 'AI Analysis', icon: 'brain' },
	report: { title: 'Compliance Report', icon: 'file-text' },
	memory: { title: 'Location Memory', icon: 'map-pin' },
	alerts: { title: 'Manager Alerts', icon: 'bell' },
};
