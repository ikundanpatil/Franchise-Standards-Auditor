// =============================================================================
// MIT License
// Copyright (c) 2026 Aparavi Software AG
// =============================================================================

import React from 'react';
import { cx } from '../../utils/cx';
import styles from './Card.module.css';

interface BaseProps {
	className?: string;
	style?: React.CSSProperties;
	children: React.ReactNode;
	/** Render as a button and wire the press affordance. */
	onClick?: () => void;
	padding?: 'sm' | 'md' | 'lg' | 'none';
}

/** Standard 24px rounded surface. */
export const Card: React.FC<BaseProps> = ({ className, style, children, onClick, padding = 'md' }) => {
	const cls = cx(styles.card, styles[`p-${padding}`], onClick && styles.pressable, className);
	if (onClick) {
		return (
			<button type="button" className={cls} style={style} onClick={onClick}>
				{children}
			</button>
		);
	}
	return (
		<div className={cls} style={style}>
			{children}
		</div>
	);
};

/** Frosted-glass surface for statistic tiles. */
export const GlassCard: React.FC<BaseProps & { tone?: string }> = ({
	className,
	style,
	children,
	onClick,
	padding = 'md',
	tone,
}) => {
	const cls = cx(styles.glass, styles[`p-${padding}`], onClick && styles.pressable, className);
	const inner = (
		<>
			<span className={styles.glassSheen} aria-hidden="true" />
			{children}
		</>
	);
	if (onClick) {
		return (
			<button type="button" className={cls} style={style} onClick={onClick} data-fg-tone={tone}>
				{inner}
			</button>
		);
	}
	return (
		<div className={cls} style={style} data-fg-tone={tone}>
			{inner}
		</div>
	);
};
