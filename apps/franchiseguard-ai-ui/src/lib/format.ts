// =============================================================================
// MIT License
// Copyright (c) 2026 Aparavi Software AG
// =============================================================================

/** Small formatting helpers shared across screens. */

/** `1,234` grouped integer. */
export function group(n: number): string {
	return Math.round(n).toLocaleString('en-US');
}

/** `92%`, `4.3%` — value is already a percentage (0–100). */
export function pct(n: number, dp = 0): string {
	return `${n.toFixed(dp)}%`;
}

/** Ratio 0–1 → `92%`. */
export function ratioPct(n: number, dp = 0): string {
	return `${(n * 100).toFixed(dp)}%`;
}

/** Coerce an ISO string, epoch-ms number or Date into a Date. */
function asDate(input: Date | string | number): Date {
	return input instanceof Date ? input : new Date(input);
}

/** `Fri, 22 Aug` from a Date, ISO string or epoch ms. */
export function shortDate(input: Date | string | number): string {
	return asDate(input).toLocaleDateString('en-US', { weekday: 'short', day: 'numeric', month: 'short' });
}

/** `22 Aug 2026`. */
export function longDate(input: Date | string | number): string {
	return asDate(input).toLocaleDateString('en-US', { day: 'numeric', month: 'short', year: 'numeric' });
}

/** `14:05`. */
export function clockTime(input: Date | string | number): string {
	return asDate(input).toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', hour12: false });
}

/** Coarse "time ago" from an epoch ms. */
export function timeAgo(ms: number): string {
	const s = Math.max(1, Math.round((Date.now() - ms) / 1000));
	if (s < 60) return `${s}s ago`;
	const m = Math.round(s / 60);
	if (m < 60) return `${m} min ago`;
	const h = Math.round(m / 60);
	if (h < 24) return `${h} hr ago`;
	const d = Math.round(h / 24);
	return `${d} day${d === 1 ? '' : 's'} ago`;
}

/** `REP-2408-1193` style reference. */
export function makeRef(prefix: string): string {
	const now = new Date();
	const mm = String(now.getMonth() + 1).padStart(2, '0');
	const dd = String(now.getDate()).padStart(2, '0');
	const tail = Math.floor(1000 + Math.random() * 8999);
	return `${prefix}-${mm}${dd}-${tail}`;
}

/** Clamp text to `n` chars with an ellipsis. */
export function truncate(text: string, n: number): string {
	return text.length <= n ? text : `${text.slice(0, n - 1).trimEnd()}…`;
}
