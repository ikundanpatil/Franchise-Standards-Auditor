// =============================================================================
// MIT License
// Copyright (c) 2026 Aparavi Software AG
// =============================================================================

import { useCallback, useEffect, useRef, useState } from 'react';

/** True when the OS asks for reduced motion. */
export function useReducedMotion(): boolean {
	const [reduced, setReduced] = useState(() =>
		typeof window !== 'undefined' && typeof window.matchMedia === 'function'
			? window.matchMedia('(prefers-reduced-motion: reduce)').matches
			: false,
	);

	useEffect(() => {
		if (typeof window === 'undefined' || typeof window.matchMedia !== 'function') return;
		const mq = window.matchMedia('(prefers-reduced-motion: reduce)');
		const onChange = () => setReduced(mq.matches);
		mq.addEventListener('change', onChange);
		return () => mq.removeEventListener('change', onChange);
	}, []);

	return reduced;
}

interface CountUpOpts {
	duration?: number;
	decimals?: number;
	/** Delay before the animation starts, ms. */
	startDelay?: number;
}

/** Animate a number from 0 → `target` with an ease-out curve. */
export function useCountUp(target: number, opts: CountUpOpts = {}): number {
	const { duration = 1100, decimals = 0, startDelay = 0 } = opts;
	const reduced = useReducedMotion();
	const [value, setValue] = useState(reduced ? target : 0);
	const frame = useRef<number>();
	const factor = 10 ** decimals;

	useEffect(() => {
		if (reduced) {
			setValue(target);
			return;
		}
		let start = 0;
		let stopped = false;
		const startAt = performance.now() + startDelay;

		const tick = (now: number) => {
			if (stopped) return;
			if (now < startAt) {
				frame.current = requestAnimationFrame(tick);
				return;
			}
			if (!start) start = now;
			const t = Math.min(1, (now - startAt) / duration);
			const eased = 1 - Math.pow(1 - t, 3);
			setValue(Math.round(target * eased * factor) / factor);
			if (t < 1) frame.current = requestAnimationFrame(tick);
		};

		frame.current = requestAnimationFrame(tick);
		return () => {
			stopped = true;
			if (frame.current) cancelAnimationFrame(frame.current);
		};
	}, [target, duration, factor, startDelay, reduced]);

	return value;
}

/** Flip to `true` one tick after mount — drives enter transitions. */
export function useMounted(delayMs = 20): boolean {
	const [on, setOn] = useState(false);
	useEffect(() => {
		const id = setTimeout(() => setOn(true), delayMs);
		return () => clearTimeout(id);
	}, [delayMs]);
	return on;
}

/** A short-lived boolean flag — great for "just tapped" / ripple states. */
export function useFlash(ms = 1600): [boolean, () => void] {
	const [on, setOn] = useState(false);
	const timer = useRef<ReturnType<typeof setTimeout>>();
	const trigger = useCallback(() => {
		setOn(true);
		clearTimeout(timer.current);
		timer.current = setTimeout(() => setOn(false), ms);
	}, [ms]);
	useEffect(() => () => clearTimeout(timer.current), []);
	return [on, trigger];
}

/**
 * Step through an ordered list of labels on a timer — used by the AI
 * "analyzing" overlay to narrate progress. Returns the active index and a
 * 0–1 progress value; calls `onDone` once the last step elapses.
 */
export function useStepper(steps: readonly string[], stepMs: number, onDone?: () => void): {
	index: number;
	progress: number;
	label: string;
} {
	const [index, setIndex] = useState(0);
	const doneRef = useRef(onDone);
	doneRef.current = onDone;

	useEffect(() => {
		setIndex(0);
		let i = 0;
		const id = setInterval(() => {
			i += 1;
			if (i >= steps.length) {
				clearInterval(id);
				doneRef.current?.();
				return;
			}
			setIndex(i);
		}, stepMs);
		return () => clearInterval(id);
	}, [steps, stepMs]);

	return {
		index,
		progress: steps.length > 1 ? index / (steps.length - 1) : 1,
		label: steps[index] ?? steps[steps.length - 1] ?? '',
	};
}
