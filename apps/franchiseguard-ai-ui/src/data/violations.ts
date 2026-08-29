// =============================================================================
// MIT License
// Copyright (c) 2026 Aparavi Software AG
// =============================================================================

/** Catalogue of violation classes the (simulated) vision model can flag.
 *  `box` is a normalised [x, y, w, h] rectangle in 0–1 image space. */

import type { ViolationType } from '../types';

export const VIOLATION_TYPES: ViolationType[] = [
	{
		id: 'v-gloves',
		label: 'Missing Gloves',
		category: 'Staff Hygiene',
		icon: 'glove',
		severity: 'critical',
		box: [0.52, 0.28, 0.22, 0.26],
		rationale:
			'bare hands detected in the food-prep zone with no visible glove line at the wrist; direct ready-to-eat contact is likely',
		standardRef: 'BSM 4.2 · Hand protection during RTE prep',
		remediation: 'Re-brief shift on glove policy; place dispensers at every prep station.',
	},
	{
		id: 'v-floor',
		label: 'Dirty Kitchen Floor',
		category: 'Kitchen Cleanliness',
		icon: 'droplet',
		severity: 'major',
		box: [0.08, 0.66, 0.44, 0.28],
		rationale:
			'standing liquid and debris across the line-side floor with a visible spread pattern near the fryer',
		standardRef: 'BSM 2.1 · Floors clean, dry, unobstructed',
		remediation: 'Immediate spot-clean; add mid-shift floor check to the cleaning rota.',
	},
	{
		id: 'v-label',
		label: 'Expired Food Label',
		category: 'Food Storage',
		icon: 'price-tag',
		severity: 'critical',
		box: [0.6, 0.55, 0.2, 0.22],
		rationale:
			'day-dot label on the container reads two days past its use-by; product remains in the cold well',
		standardRef: 'BSM 3.4 · Date marking & stock rotation',
		remediation: 'Discard affected stock now; audit the full cold well and re-date.',
	},
	{
		id: 'v-uncovered',
		label: 'Food Left Uncovered',
		category: 'Food Storage',
		icon: 'package',
		severity: 'major',
		box: [0.28, 0.34, 0.24, 0.2],
		rationale:
			'open tray of prepared product on the counter with no lid or film and no active service in frame',
		standardRef: 'BSM 3.2 · Product protection when not in service',
		remediation: 'Cover and return to chilled storage; retrain on holding rules.',
	},
	{
		id: 'v-signage',
		label: 'Non-compliant Signage',
		category: 'Branding Compliance',
		icon: 'award',
		severity: 'minor',
		box: [0.05, 0.06, 0.3, 0.16],
		rationale:
			'menu board uses a superseded logo lockup and off-palette colour vs. the current brand kit',
		standardRef: 'BRAND 1.1 · Approved signage & lockups',
		remediation: 'Order the current board pack; remove legacy artwork within 14 days.',
	},
	{
		id: 'v-handwash',
		label: 'Handwash Sink Blocked',
		category: 'Staff Hygiene',
		icon: 'droplet',
		severity: 'major',
		box: [0.74, 0.4, 0.2, 0.34],
		rationale:
			'dedicated handwash basin is stacked with utensils, reducing access during service',
		standardRef: 'BSM 4.1 · Handwash stations kept clear',
		remediation: 'Clear the basin; mark it hands-only with fresh signage.',
	},
	{
		id: 'v-pest',
		label: 'Pest Entry Point',
		category: 'Pest Control',
		icon: 'bug',
		severity: 'major',
		box: [0.82, 0.72, 0.14, 0.2],
		rationale: 'gap under the rear door with no brush seal; daylight visible along the threshold',
		standardRef: 'BSM 6.3 · Proofing of external openings',
		remediation: 'Fit a brush strip; log with the pest contractor on next visit.',
	},
	{
		id: 'v-temp',
		label: 'Cold-Hold Above Range',
		category: 'Food Storage',
		icon: 'thermometer',
		severity: 'critical',
		box: [0.42, 0.5, 0.2, 0.24],
		rationale:
			'display unit thermometer reads 9°C against a 0–5°C standard; condensation on the glass',
		standardRef: 'BSM 3.1 · Cold holding 5°C or below',
		remediation: 'Move stock to a working unit; call refrigeration; record corrective action.',
	},
	{
		id: 'v-waste',
		label: 'Overflowing Waste Bin',
		category: 'Kitchen Cleanliness',
		icon: 'package',
		severity: 'minor',
		box: [0.12, 0.44, 0.16, 0.3],
		rationale: 'open bin past fill line beside the prep bench with no lid in place',
		standardRef: 'BSM 2.4 · Waste stored in lidded containers',
		remediation: 'Empty now; add a lidded bin and a mid-shift empty step.',
	},
	{
		id: 'v-uniform',
		label: 'Uniform Not to Spec',
		category: 'Branding Compliance',
		icon: 'user',
		severity: 'minor',
		box: [0.5, 0.12, 0.18, 0.4],
		rationale: 'crew member in a non-issued top with no name badge or apron',
		standardRef: 'BRAND 2.3 · Crew uniform standard',
		remediation: 'Issue correct uniform; badge every crew member on shift.',
	},
];

export const violationById = (id: string): ViolationType | undefined =>
	VIOLATION_TYPES.find((v) => v.id === id);
