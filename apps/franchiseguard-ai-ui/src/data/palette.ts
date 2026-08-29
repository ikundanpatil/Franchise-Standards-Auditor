// =============================================================================
// MIT License
// Copyright (c) 2026 Aparavi Software AG
// =============================================================================

/** Categorical chart colours — blue/violet led, semantic accents after. */
export const CHART = {
	blue: '#1f5bff',
	violet: '#7c5cff',
	teal: '#12b5a6',
	green: '#12a05f',
	amber: '#e08404',
	red: '#e23b2f',
	slate: '#8592a9',
	indigo: '#4636d9',
} as const;

export const SERIES = {
	compliance: CHART.blue,
	risk: CHART.red,
	target: CHART.slate,
	resolved: CHART.green,
	unresolved: CHART.amber,
	complaints: CHART.violet,
} as const;
