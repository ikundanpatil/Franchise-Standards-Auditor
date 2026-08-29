// =============================================================================
// MIT License
// Copyright (c) 2026 Aparavi Software AG
// =============================================================================

import React, { useMemo } from 'react';
import { useMounted } from '../../lib/hooks';
import { cx } from '../../utils/cx';
import { niceMax, ticks } from './chartUtils';
import styles from './BarChart.module.css';

export interface Bar {
	value: number;
	color: string;
	name?: string;
}

export interface BarGroup {
	label: string;
	bars: Bar[];
}

export interface BarChartProps {
	groups: BarGroup[];
	height?: number;
	yMax?: number;
	stacked?: boolean;
	showValues?: boolean;
	formatValue?: (n: number) => string;
	className?: string;
}

const W = 328;
const PAD = { top: 14, right: 8, bottom: 26, left: 28 };

/** Grouped or stacked column chart with a grow-in animation. */
export const BarChart: React.FC<BarChartProps> = ({
	groups,
	height = 176,
	yMax,
	stacked = false,
	showValues = false,
	formatValue = (n) => `${Math.round(n)}`,
	className,
}) => {
	const mounted = useMounted(60);
	const H = height;

	const geo = useMemo(() => {
		const totals = groups.map((g) =>
			stacked ? g.bars.reduce((s, b) => s + b.value, 0) : Math.max(...g.bars.map((b) => b.value)),
		);
		const max = yMax ?? niceMax(Math.max(1, ...totals));
		const plotW = W - PAD.left - PAD.right;
		const plotH = H - PAD.top - PAD.bottom;
		const gw = plotW / groups.length;
		const baseY = PAD.top + plotH;
		return { max, plotW, plotH, gw, baseY };
	}, [groups, yMax, stacked, H]);

	const yTicks = ticks(geo.max, 3);
	const barCount = groups[0]?.bars.length ?? 1;
	const innerPad = geo.gw * 0.22;
	const slot = (geo.gw - innerPad * 2) / (stacked ? 1 : barCount);
	const barW = Math.min(slot * (stacked ? 0.5 : 0.78), 26);

	return (
		<div className={cx(styles.wrap, className)}>
			<svg viewBox={`0 0 ${W} ${H}`} width="100%" height={H} className={styles.svg} role="img">
				{yTicks.map((v, i) => {
					const y = geo.baseY - (v / geo.max) * geo.plotH;
					return (
						<g key={i}>
							<line x1={PAD.left} y1={y} x2={W - PAD.right} y2={y} className={styles.grid} />
							<text x={PAD.left - 6} y={y + 3} className={styles.yLabel} textAnchor="end">
								{formatValue(v)}
							</text>
						</g>
					);
				})}

				{groups.map((g, gi) => {
					const gx = PAD.left + gi * geo.gw + innerPad;
					let stackAcc = 0;
					return (
						<g key={gi}>
							{g.bars.map((b, bi) => {
								const h = mounted ? (b.value / geo.max) * geo.plotH : 0;
								let x: number;
								let y: number;
								if (stacked) {
									x = gx + (slot - barW) / 2;
									y = geo.baseY - stackAcc - h;
									stackAcc += h;
								} else {
									x = gx + bi * slot + (slot - barW) / 2;
									y = geo.baseY - h;
								}
								return (
									<g key={bi}>
										<rect
											x={x}
											y={y}
											width={barW}
											height={Math.max(0, h)}
											rx={Math.min(barW / 2, 5)}
											fill={b.color}
											className={styles.bar}
											style={{ transitionDelay: `${gi * 70 + bi * 40}ms` }}
										/>
										{showValues && !stacked && mounted && (
											<text x={x + barW / 2} y={y - 5} className={styles.valLabel} textAnchor="middle">
												{formatValue(b.value)}
											</text>
										)}
									</g>
								);
							})}
							<text
								x={gx + (geo.gw - innerPad * 2) / 2}
								y={H - 8}
								className={styles.xLabel}
								textAnchor="middle"
							>
								{g.label}
							</text>
						</g>
					);
				})}
			</svg>
		</div>
	);
};
