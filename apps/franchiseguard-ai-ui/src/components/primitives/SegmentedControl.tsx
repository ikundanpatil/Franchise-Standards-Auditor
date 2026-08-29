// =============================================================================
// MIT License
// Copyright (c) 2026 Aparavi Software AG
// =============================================================================

import React from 'react';
import { cx } from '../../utils/cx';
import styles from './SegmentedControl.module.css';

export interface Segment<T extends string = string> {
	id: T;
	label: string;
}

export interface SegmentedControlProps<T extends string = string> {
	segments: Array<Segment<T>>;
	value: T;
	onChange: (id: T) => void;
	className?: string;
}

/** iOS-style segmented switch with a sliding thumb. */
export function SegmentedControl<T extends string = string>({
	segments,
	value,
	onChange,
	className,
}: SegmentedControlProps<T>): React.ReactElement {
	const index = Math.max(0, segments.findIndex((s) => s.id === value));
	return (
		<div className={cx(styles.wrap, className)} role="tablist">
			<span
				className={styles.thumb}
				style={{
					width: `calc(${100 / segments.length}% - 4px)`,
					transform: `translateX(calc(${index * 100}% + ${index * 4}px))`,
				}}
				aria-hidden="true"
			/>
			{segments.map((s) => (
				<button
					key={s.id}
					type="button"
					role="tab"
					aria-selected={s.id === value}
					className={cx(styles.seg, s.id === value && styles.active)}
					onClick={() => onChange(s.id)}
				>
					{s.label}
				</button>
			))}
		</div>
	);
}
