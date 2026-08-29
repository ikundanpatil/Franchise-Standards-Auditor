// =============================================================================
// MIT License
// Copyright (c) 2026 Aparavi Software AG
// =============================================================================

import React, { useEffect, useRef, useState } from 'react';
import { useCountUp, useReducedMotion } from '../../lib/hooks';
import { cx } from '../../utils/cx';
import styles from './ProgressRing.module.css';

export interface ProgressRingProps {
	/** 0–100. */
	value: number;
	size?: number;
	stroke?: number;
	label?: string;
	sublabel?: string;
	/** CSS colour (or var) for the arc; defaults to the brand gradient. */
	color?: string;
	track?: string;
	className?: string;
	/** Show the animated numeric value in the centre. */
	showValue?: boolean;
	decimals?: number;
}

/** Circular gauge with an animated sweep + count-up centre value. */
export const ProgressRing: React.FC<ProgressRingProps> = ({
	value,
	size = 132,
	stroke = 12,
	label,
	sublabel,
	color,
	track,
	className,
	showValue = true,
	decimals = 0,
}) => {
	const reduced = useReducedMotion();
	const r = (size - stroke) / 2;
	const circ = 2 * Math.PI * r;
	const clamped = Math.max(0, Math.min(100, value));
	const [progress, setProgress] = useState(reduced ? clamped : 0);
	const shown = useCountUp(clamped, { decimals, duration: 1200 });
	const raf = useRef<number>();

	useEffect(() => {
		if (reduced) {
			setProgress(clamped);
			return;
		}
		const start = performance.now();
		const from = 0;
		const tick = (now: number) => {
			const t = Math.min(1, (now - start) / 1200);
			const eased = 1 - Math.pow(1 - t, 3);
			setProgress(from + (clamped - from) * eased);
			if (t < 1) raf.current = requestAnimationFrame(tick);
		};
		raf.current = requestAnimationFrame(tick);
		return () => {
			if (raf.current) cancelAnimationFrame(raf.current);
		};
	}, [clamped, reduced]);

	const offset = circ * (1 - progress / 100);
	const gid = `fg-ring-${size}-${stroke}`;

	return (
		<div className={cx(styles.wrap, className)} style={{ width: size, height: size }}>
			<svg width={size} height={size} viewBox={`0 0 ${size} ${size}`} className={styles.svg}>
				<defs>
					<linearGradient id={gid} x1="0%" y1="0%" x2="100%" y2="100%">
						<stop offset="0%" stopColor="var(--fg-brand)" />
						<stop offset="100%" stopColor="var(--fg-violet)" />
					</linearGradient>
				</defs>
				<circle
					cx={size / 2}
					cy={size / 2}
					r={r}
					fill="none"
					stroke={track ?? 'var(--fg-hairline)'}
					strokeWidth={stroke}
				/>
				<circle
					cx={size / 2}
					cy={size / 2}
					r={r}
					fill="none"
					stroke={color ?? `url(#${gid})`}
					strokeWidth={stroke}
					strokeLinecap="round"
					strokeDasharray={circ}
					strokeDashoffset={offset}
					transform={`rotate(-90 ${size / 2} ${size / 2})`}
				/>
			</svg>
			<div className={styles.center}>
				{showValue && (
					<span className={styles.value}>
						{decimals ? shown.toFixed(decimals) : Math.round(shown)}
					</span>
				)}
				{label && <span className={styles.label}>{label}</span>}
				{sublabel && <span className={styles.sub}>{sublabel}</span>}
			</div>
		</div>
	);
};
