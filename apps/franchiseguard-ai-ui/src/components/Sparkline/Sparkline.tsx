// =============================================================================
// MIT License
// Copyright (c) 2026 Aparavi Software AG
// =============================================================================

import React from 'react';
import { cx } from '../../utils/cx';
import styles from './Sparkline.module.css';

export interface SparklineProps {
	/** Series, oldest → newest. Needs at least two points. */
	data: number[];
	width?: number;
	height?: number;
	className?: string;
}

/** Minimal trend line with a soft area fill and an emphasised endpoint. */
export const Sparkline: React.FC<SparklineProps> = ({ data, width = 64, height = 22, className }) => {
	if (data.length < 2) return null;

	const pad = 2;
	const min = Math.min(...data);
	const max = Math.max(...data);
	const span = max - min || 1;
	const step = (width - pad * 2) / (data.length - 1);

	const points = data.map((value, i) => {
		const x = pad + i * step;
		const y = height - pad - ((value - min) / span) * (height - pad * 2);
		return [x, y] as const;
	});

	const line = points.map(([x, y], i) => `${i ? 'L' : 'M'}${x.toFixed(1)},${y.toFixed(1)}`).join(' ');
	const [firstX] = points[0];
	const [lastX, lastY] = points[points.length - 1];
	const area = `${line} L${lastX.toFixed(1)},${height} L${firstX.toFixed(1)},${height} Z`;

	return (
		<svg
			className={cx(styles.spark, className)}
			viewBox={`0 0 ${width} ${height}`}
			width={width}
			height={height}
			role="presentation"
			aria-hidden="true"
		>
			<path className={styles.area} d={area} />
			<path className={styles.line} d={line} />
			<circle className={styles.cap} cx={lastX} cy={lastY} r={2.4} />
		</svg>
	);
};
