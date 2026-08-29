// =============================================================================
// MIT License
// Copyright (c) 2026 Aparavi Software AG
// =============================================================================

import type { ChecklistItemDef } from '../types';

/** The five brand-standard areas scored on every inspection. */
export const CHECKLIST: ChecklistItemDef[] = [
	{
		id: 'kitchen',
		label: 'Kitchen Cleanliness',
		icon: 'broom',
		hint: 'Floors, surfaces, drains, waste handling',
	},
	{
		id: 'hygiene',
		label: 'Staff Hygiene',
		icon: 'glove',
		hint: 'Gloves, hairnets, handwash logs, uniforms',
	},
	{
		id: 'storage',
		label: 'Food Storage',
		icon: 'thermometer',
		hint: 'Cold-hold temps, labelling, FIFO rotation',
	},
	{
		id: 'branding',
		label: 'Branding Compliance',
		icon: 'award',
		hint: 'Signage, menu boards, uniform spec, packaging',
	},
	{
		id: 'pest',
		label: 'Pest Control',
		icon: 'bug',
		hint: 'Bait stations, entry seals, service records',
	},
];
