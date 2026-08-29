// =============================================================================
// MIT License
// Copyright (c) 2026 Aparavi Software AG
// =============================================================================

import React from 'react';
import { cx } from '../../utils/cx';
import styles from './Skeleton.module.css';

export interface SkeletonProps {
	width?: number | string;
	height?: number | string;
	radius?: number | string;
	className?: string;
	style?: React.CSSProperties;
}

/** Shimmering placeholder block. */
export const Skeleton: React.FC<SkeletonProps> = ({ width, height = 14, radius = 8, className, style }) => (
	<span
		className={cx(styles.sk, className)}
		style={{ width, height, borderRadius: radius, ...style }}
		aria-hidden="true"
	/>
);

/** A stack of text lines, last one short. */
export const SkeletonText: React.FC<{ lines?: number; className?: string }> = ({
	lines = 3,
	className,
}) => (
	<span className={cx(styles.stack, className)} aria-hidden="true">
		{Array.from({ length: lines }).map((_, i) => (
			<Skeleton key={i} height={11} width={i === lines - 1 ? '55%' : '100%'} />
		))}
	</span>
);
