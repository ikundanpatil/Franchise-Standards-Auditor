// =============================================================================
// MIT License
// Copyright (c) 2026 Aparavi Software AG
// =============================================================================

/** Geometry helpers shared by the SVG chart primitives. */

export interface Pt {
	x: number;
	y: number;
}

/** Map a value in [d0, d1] onto [r0, r1]. */
export function scale(v: number, d0: number, d1: number, r0: number, r1: number): number {
	if (d1 === d0) return (r0 + r1) / 2;
	return r0 + ((v - d0) / (d1 - d0)) * (r1 - r0);
}

/** Build a smooth path through points using a Catmull-Rom → cubic Bézier. */
export function smoothPath(pts: Pt[], tension = 0.5): string {
	if (pts.length < 2) return pts.length ? `M${pts[0].x},${pts[0].y}` : '';
	const d: string[] = [`M${r(pts[0].x)},${r(pts[0].y)}`];
	for (let i = 0; i < pts.length - 1; i++) {
		const p0 = pts[i - 1] ?? pts[i];
		const p1 = pts[i];
		const p2 = pts[i + 1];
		const p3 = pts[i + 2] ?? p2;
		const c1x = p1.x + ((p2.x - p0.x) / 6) * tension * 2;
		const c1y = p1.y + ((p2.y - p0.y) / 6) * tension * 2;
		const c2x = p2.x - ((p3.x - p1.x) / 6) * tension * 2;
		const c2y = p2.y - ((p3.y - p1.y) / 6) * tension * 2;
		d.push(`C${r(c1x)},${r(c1y)} ${r(c2x)},${r(c2y)} ${r(p2.x)},${r(p2.y)}`);
	}
	return d.join(' ');
}

/** Straight polyline path. */
export function linePath(pts: Pt[]): string {
	return pts.map((p, i) => `${i ? 'L' : 'M'}${r(p.x)},${r(p.y)}`).join(' ');
}

/** Close a line path down to the baseline to make an area fill. */
export function areaFromPath(path: string, pts: Pt[], baseY: number): string {
	if (!pts.length) return '';
	const first = pts[0];
	const last = pts[pts.length - 1];
	return `${path} L${r(last.x)},${r(baseY)} L${r(first.x)},${r(baseY)} Z`;
}

/** "Nice" rounded max for an axis. */
export function niceMax(max: number): number {
	if (max <= 0) return 1;
	const mag = 10 ** Math.floor(Math.log10(max));
	const norm = max / mag;
	const step = norm <= 1 ? 1 : norm <= 2 ? 2 : norm <= 5 ? 5 : 10;
	return step * mag;
}

/** Evenly spaced tick values from 0 to max. */
export function ticks(max: number, count = 4): number[] {
	return Array.from({ length: count + 1 }, (_, i) => (max / count) * i);
}

function r(n: number): number {
	return Math.round(n * 100) / 100;
}
