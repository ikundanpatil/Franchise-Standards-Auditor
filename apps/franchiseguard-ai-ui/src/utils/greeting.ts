// =============================================================================
// MIT License
// Copyright (c) 2026 Aparavi Software AG
// =============================================================================

/** Time-of-day greeting for the welcome banner. */
export function getGreeting(date: Date = new Date()): string {
	const hour = date.getHours();
	if (hour < 12) return 'Good Morning';
	if (hour < 17) return 'Good Afternoon';
	return 'Good Evening';
}
