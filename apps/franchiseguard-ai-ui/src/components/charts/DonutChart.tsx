// =============================================================================
// MIT License
// Copyright (c) 2026 Aparavi Software AG
// =============================================================================

import React, { useMemo, useState } from 'react';
import { useMounted } from '../../lib/hooks';
import { cx } from '../../utils/cx';
import type { DonutSlice } from '../../types';
import styles from './DonutChart.module.css';

export interface DonutChartProps {
	slices: DonutSlice[];
	size?: number;
	thickness?: number;
	/** Big number in the middle; defaults to the total. */
	centerValue?: string;
	centerLabel?: string;
	className?: string;
}

const GAP_DEG = 3;

/** Ring chart with a sweep-in animation and tappable segments. */
export const DonutChart: React.FC<DonutChartProps> = ({
	slices,
	size = 148,
	thickness = 20,
	centerValue,
	centerLabel,
	className,
}) => {
	const mounted = useMounted(80);
	const [active, setActive] = useState<number | null>(null);
	const r = (size - thickness) / 2;
	const circ = 2 * Math.PI * r;
	const total = slices.reduce((s, d) => s + d.value, 0) || 1;

	const segs = useMemo(() => {
		let acc = 0;
		return slices.map((d) => {
			const frac = d.value / total;
			const seg = { ...d, frac, offset: acc };
			acc += frac;
			return seg;
		});
	}, [slices, total]);

	const shown = active != null ? segs[active] : null;

	return (
		<div className={cx(styles.wrap, className)}>
			<div className={styles.ring} style={{ width: size, height: size }}>
				<svg width={size} height={size} viewBox={`0 0 ${size} ${size}`}>
					<circle
						cx={size / 2}
						cy={size / 2}
						r={r}
						fill="none"
						stroke="var(--fg-hairline)"
						strokeWidth={thickness}
					/>
					{segs.map((s, i) => {
						const dash = Math.max(0, s.frac * circ - GAP_DEG);
						return (
							<circle
								key={i}
								cx={size / 2}
								cy={size / 2}
								r={r}
								fill="none"
								stroke={s.color}
								strokeWidth={active === i ? thickness + 3 : thickness}
								strokeLinecap="round"
								strokeDasharray={`${mounted ? dash : 0} ${circ}`}
								strokeDashoffset={-s.offset * circ}
								transform={`rotate(-90 ${size / 2} ${size / 2})`}
								className={styles.seg}
								style={{ transitionDelay: `${i * 90}ms` }}
								onPointerEnter={() => setActive(i)}
								onPointerLeave={() => setActive(null)}
								onClick={() => setActive(active === i ? null : i)}
							/>
						);
					})}
				</svg>
				<div className={styles.center}>
					<span className={styles.centerValue}>
						{shown ? `${Math.round(shown.frac * 100)}%` : centerValue ?? Math.round(total)}
					</span>
					<span className={styles.centerLabel}>{shown ? shown.label : centerLabel ?? 'Total'}</span>
				</div>
			</div>

			<ul className={styles.legend}>
				{segs.map((s, i) => (
					<li key={i}>
						<button
							type="button"
							className={cx(styles.legendBtn, active === i && styles.legendActive)}
							onPointerEnter={() => setActive(i)}
							onPointerLeave={() => setActive(null)}
							onClick={() => setActive(active === i ? null : i)}
						>
							<i style={{ background: s.color }} />
							<span className={styles.legendLabel}>{s.label}</span>
							<b>{s.value}</b>
						</button>
					</li>
				))}
			</ul>
		</div>
	);
};
