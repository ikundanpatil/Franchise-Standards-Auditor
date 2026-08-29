// =============================================================================
// MIT License
// Copyright (c) 2026 Aparavi Software AG
// =============================================================================

/**
 * Tiny deterministic-ish PRNG helpers for the fake AI layer — enough
 * variation to feel alive across demo runs without pulling a dependency.
 */

/** mulberry32 — fast seeded PRNG returning [0, 1). */
export function mulberry32(seed: number): () => number {
	let a = seed >>> 0;
	return () => {
		a |= 0;
		a = (a + 0x6d2b79f5) | 0;
		let t = Math.imul(a ^ (a >>> 15), 1 | a);
		t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
		return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
	};
}

/** A default generator reseeded on each import tick. */
let rng = mulberry32((Date.now() % 2147483647) || 1);

/** Reseed the shared generator (handy for reproducible screenshots). */
export function reseed(seed: number): void {
	rng = mulberry32(seed >>> 0 || 1);
}

/** Float in [min, max). */
export function rand(min = 0, max = 1): number {
	return min + (max - min) * rng();
}

/** Integer in [min, max] inclusive. */
export function randInt(min: number, max: number): number {
	return Math.floor(rand(min, max + 1));
}

/** Round to `dp` decimals. */
export function round(n: number, dp = 0): number {
	const f = 10 ** dp;
	return Math.round(n * f) / f;
}

/** Nudge a value by ±amount, clamped to [lo, hi]. */
export function jitter(value: number, amount: number, lo = -Infinity, hi = Infinity): number {
	return clamp(value + rand(-amount, amount), lo, hi);
}

export function clamp(n: number, lo: number, hi: number): number {
	return Math.min(hi, Math.max(lo, n));
}

/** Random element of a non-empty array. */
export function pick<T>(items: readonly T[]): T {
	return items[randInt(0, items.length - 1)];
}

/** Fisher–Yates shuffle (returns a new array). */
export function shuffle<T>(items: readonly T[]): T[] {
	const out = items.slice();
	for (let i = out.length - 1; i > 0; i--) {
		const j = randInt(0, i);
		[out[i], out[j]] = [out[j], out[i]];
	}
	return out;
}

/** Take up to `n` random items. */
export function sample<T>(items: readonly T[], n: number): T[] {
	return shuffle(items).slice(0, Math.max(0, Math.min(n, items.length)));
}

/** True with probability `p`. */
export function chance(p: number): boolean {
	return rng() < p;
}

/** Promise that resolves after `ms` (with a little natural jitter). */
export function delay(ms: number, spread = 0): Promise<void> {
	const t = spread > 0 ? ms + rand(-spread, spread) : ms;
	return new Promise((resolve) => setTimeout(resolve, Math.max(0, t)));
}

/** Confidence score that reads like a model output: 0.71–0.98, 2dp. */
export function confidence(floor = 0.71, ceil = 0.98): number {
	return round(rand(floor, ceil), 2);
}
