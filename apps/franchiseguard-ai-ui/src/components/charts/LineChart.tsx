// =============================================================================
// MIT License
// Copyright (c) 2026 Aparavi Software AG
// =============================================================================

import React, { useMemo, useRef, useState } from 'react';
import { useReducedMotion } from '../../lib/hooks';
import { cx } from '../../utils/cx';
import type { ChartSeries } from '../../types';
import { areaFromPath, niceMax, scale, smoothPath, ticks, type Pt } from './chartUtils';
import styles from './LineChart.module.css';

export interface LineChartProps {
	series: ChartSeries[];
	labels: string[];
	height?: number;
	/** Force a Y ceiling; otherwise a "nice" max is derived. */
	yMax?: number;
	yMin?: number;
	area?: boolean;
	interactive?: boolean;
	formatValue?: (n: number) => string;
	/** Show only every n-th x label. */
	labelEvery?: number;
	className?: string;
}

const W = 328;
const PAD = { top: 12, right: 12, bottom: 24, left: 30 };

/** Multi-series smooth line / area chart with a tap-to-inspect crosshair. */
export const LineChart: React.FC<LineChartProps> = ({
	series,
	labels,
	height = 168,
	yMax,
	yMin = 0,
	area = true,
	interactive = true,
	formatValue = (n) => `${Math.round(n)}`,
	labelEvery,
	className,
}) => {
	const reduced = useReducedMotion();
	const H = height;
	const svgRef = useRef<SVGSVGElement>(null);
	const [active, setActive] = useState<number | null>(null);

	const geo = useMemo(() => {
		const allValues = series.flatMap((s) => s.points);
		const dataMax = yMax ?? niceMax(Math.max(1, ...allValues));
		const dataMin = yMin;
		const plotW = W - PAD.left - PAD.right;
		const plotH = H - PAD.top - PAD.bottom;
		const n = labels.length;
		const xAt = (i: number) => PAD.left + (n <= 1 ? plotW / 2 : (i / (n - 1)) * plotW);
		const yAt = (v: number) => PAD.top + plotH - scale(v, dataMin, dataMax, 0, plotH);

		const built = series.map((s) => {
			const pts: Pt[] = s.points.map((v, i) => ({ x: xAt(i), y: yAt(v) }));
			const path = smoothPath(pts);
			return { series: s, pts, path, areaPath: area ? areaFromPath(path, pts, PAD.top + plotH) : '' };
		});

		return { built, dataMax, dataMin, plotH, xAt, yAt, baseY: PAD.top + plotH, n };
	}, [series, labels.length, yMax, yMin, area, H]);

	const yTicks = ticks(geo.dataMax, 3).map((v) => v + geo.dataMin);
	const step = labelEvery ?? Math.ceil(labels.length / 6);

	const handleMove = (e: React.PointerEvent<SVGSVGElement>) => {
		if (!interactive || !svgRef.current) return;
		const rect = svgRef.current.getBoundingClientRect();
		const xRatio = (e.clientX - rect.left) / rect.width;
		const plotW = W - PAD.left - PAD.right;
		const rel = (xRatio * W - PAD.left) / plotW;
		const idx = Math.round(rel * (geo.n - 1));
		setActive(Math.max(0, Math.min(geo.n - 1, idx)));
	};

	const tipLeftPct = active != null ? (geo.xAt(active) / W) * 100 : 0;

	return (
		<div className={cx(styles.wrap, className)}>
			<svg
				ref={svgRef}
				viewBox={`0 0 ${W} ${H}`}
				width="100%"
				height={H}
				className={styles.svg}
				onPointerMove={handleMove}
				onPointerDown={handleMove}
				onPointerLeave={() => setActive(null)}
				role="img"
			>
				<defs>
					{geo.built.map(({ series: s }, i) => (
						<linearGradient key={i} id={`fg-lc-fill-${i}`} x1="0" y1="0" x2="0" y2="1">
							<stop offset="0%" stopColor={s.color} stopOpacity={0.28} />
							<stop offset="100%" stopColor={s.color} stopOpacity={0} />
						</linearGradient>
					))}
				</defs>

				{/* grid */}
				{yTicks.map((v, i) => {
					const y = geo.yAt(v);
					return (
						<g key={i}>
							<line x1={PAD.left} y1={y} x2={W - PAD.right} y2={y} className={styles.grid} />
							<text x={PAD.left - 6} y={y + 3} className={styles.yLabel} textAnchor="end">
								{formatValue(v)}
							</text>
						</g>
					);
				})}

				{/* areas + lines */}
				{geo.built.map(({ series: s, path, areaPath }, i) => (
					<g key={i}>
						{area && <path d={areaPath} fill={`url(#fg-lc-fill-${i})`} />}
						<path
							d={path}
							fill="none"
							stroke={s.color}
							strokeWidth={2.4}
							strokeLinecap="round"
							strokeLinejoin="round"
							vectorEffect="non-scaling-stroke"
							className={reduced ? undefined : styles.draw}
							style={{ animationDelay: `${i * 160}ms` }}
						/>
					</g>
				))}

				{/* x labels */}
				{labels.map((lbl, i) =>
					i % step === 0 || i === labels.length - 1 ? (
						<text key={i} x={geo.xAt(i)} y={H - 6} className={styles.xLabel} textAnchor="middle">
							{lbl}
						</text>
					) : null,
				)}

				{/* crosshair */}
				{active != null && (
					<g className={styles.cross}>
						<line
							x1={geo.xAt(active)}
							y1={PAD.top}
							x2={geo.xAt(active)}
							y2={geo.baseY}
							className={styles.crossLine}
						/>
						{geo.built.map(({ series: s }, i) => (
							<circle
								key={i}
								cx={geo.xAt(active)}
								cy={geo.yAt(s.points[active])}
								r={4}
								fill={s.color}
								stroke="var(--fg-surface)"
								strokeWidth={2}
							/>
						))}
					</g>
				)}
			</svg>

			{active != null && (
				<div className={styles.tip} style={{ left: `${tipLeftPct}%` }}>
					<span className={styles.tipLabel}>{labels[active]}</span>
					{geo.built.map(({ series: s }, i) => (
						<span key={i} className={styles.tipRow}>
							<i style={{ background: s.color }} />
							{s.name}
							<b>{formatValue(s.points[active])}</b>
						</span>
					))}
				</div>
			)}

			{series.length > 1 && (
				<div className={styles.legend}>
					{series.map((s) => (
						<span key={s.name} className={styles.legendItem}>
							<i style={{ background: s.color }} />
							{s.name}
						</span>
					))}
				</div>
			)}
		</div>
	);
};
