// =============================================================================
// MIT License
// Copyright (c) 2026 Aparavi Software AG
// =============================================================================

import React, { useCallback, useRef, useState } from 'react';
import { Icon } from '../Icon/Icon';
import { cx } from '../../utils/cx';
import type { IconName } from '../../types';
import styles from './Button.module.css';

type Variant = 'primary' | 'secondary' | 'ghost' | 'danger' | 'glass';
type Size = 'sm' | 'md' | 'lg';

export interface ButtonProps extends Omit<React.ButtonHTMLAttributes<HTMLButtonElement>, 'children'> {
	variant?: Variant;
	size?: Size;
	icon?: IconName;
	iconRight?: IconName;
	block?: boolean;
	loading?: boolean;
	children?: React.ReactNode;
}

interface Ripple {
	id: number;
	x: number;
	y: number;
	size: number;
}

/** Material-ish button with a tap ripple. */
export const Button: React.FC<ButtonProps> = ({
	variant = 'primary',
	size = 'md',
	icon,
	iconRight,
	block,
	loading,
	className,
	onClick,
	disabled,
	children,
	...rest
}) => {
	const [ripples, setRipples] = useState<Ripple[]>([]);
	const seq = useRef(0);

	const handleClick = useCallback(
		(e: React.MouseEvent<HTMLButtonElement>) => {
			const el = e.currentTarget;
			const rect = el.getBoundingClientRect();
			const size = Math.max(rect.width, rect.height) * 1.1;
			const id = seq.current++;
			setRipples((r) => [
				...r,
				{ id, size, x: e.clientX - rect.left - size / 2, y: e.clientY - rect.top - size / 2 },
			]);
			setTimeout(() => setRipples((r) => r.filter((rp) => rp.id !== id)), 620);
			onClick?.(e);
		},
		[onClick],
	);

	return (
		<button
			type="button"
			className={cx(
				styles.btn,
				styles[variant],
				styles[size],
				block && styles.block,
				loading && styles.loading,
				className,
			)}
			onClick={handleClick}
			disabled={disabled || loading}
			aria-busy={loading || undefined}
			{...rest}
		>
			<span className={styles.ripples} aria-hidden="true">
				{ripples.map((r) => (
					<span
						key={r.id}
						className={styles.ripple}
						style={{ left: r.x, top: r.y, width: r.size, height: r.size }}
					/>
				))}
			</span>
			{loading ? (
				<span className={styles.spinner} aria-hidden="true" />
			) : (
				icon && <Icon name={icon} size={size === 'lg' ? 20 : 17} />
			)}
			{children && <span className={styles.label}>{children}</span>}
			{iconRight && !loading && <Icon name={iconRight} size={size === 'lg' ? 20 : 17} />}
		</button>
	);
};
