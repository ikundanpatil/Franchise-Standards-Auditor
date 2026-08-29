// =============================================================================
// MIT License
// Copyright (c) 2026 Aparavi Software AG
// =============================================================================

/** Small shared primitives: Avatar, Toggle, Divider, KeyValue, MetricPill. */

import React from 'react';
import { Icon } from '../Icon/Icon';
import { cx } from '../../utils/cx';
import type { IconName } from '../../types';
import styles from './Misc.module.css';

export const Avatar: React.FC<{ initials: string; size?: number; className?: string }> = ({
	initials,
	size = 40,
	className,
}) => (
	<span
		className={cx(styles.avatar, className)}
		style={{ width: size, height: size, fontSize: size * 0.36 }}
		aria-hidden="true"
	>
		{initials}
	</span>
);

export const Toggle: React.FC<{
	checked: boolean;
	onChange: (v: boolean) => void;
	label?: string;
}> = ({ checked, onChange, label }) => (
	<button
		type="button"
		role="switch"
		aria-checked={checked}
		aria-label={label}
		className={cx(styles.toggle, checked && styles.toggleOn)}
		onClick={() => onChange(!checked)}
	>
		<span className={styles.knob} />
	</button>
);

export const Divider: React.FC<{ label?: string; className?: string }> = ({ label, className }) =>
	label ? (
		<div className={cx(styles.dividerLabelled, className)}>
			<span />
			<em>{label}</em>
			<span />
		</div>
	) : (
		<hr className={cx(styles.divider, className)} />
	);

export const KeyValue: React.FC<{ k: string; v: React.ReactNode; icon?: IconName }> = ({
	k,
	v,
	icon,
}) => (
	<div className={styles.kv}>
		<span className={styles.kvKey}>
			{icon && <Icon name={icon} size={13} />}
			{k}
		</span>
		<span className={styles.kvVal}>{v}</span>
	</div>
);

export const MetricPill: React.FC<{
	icon: IconName;
	value: React.ReactNode;
	label: string;
	tone?: string;
}> = ({ icon, value, label, tone = 'info' }) => (
	<div className={styles.metric} data-fg-tone={tone}>
		<span className={styles.metricIcon}>
			<Icon name={icon} size={15} />
		</span>
		<span className={styles.metricBody}>
			<b>{value}</b>
			<i>{label}</i>
		</span>
	</div>
);
