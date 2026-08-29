// =============================================================================
// MIT License
// Copyright (c) 2026 Aparavi Software AG
// =============================================================================

import React, { useId } from 'react';
import { Icon } from '../Icon/Icon';
import { cx } from '../../utils/cx';
import type { IconName } from '../../types';
import styles from './Field.module.css';

interface CommonProps {
	label?: string;
	hint?: string;
	className?: string;
}

export interface TextFieldProps
	extends CommonProps,
		Omit<React.InputHTMLAttributes<HTMLInputElement>, 'className'> {
	icon?: IconName;
}

export const TextField: React.FC<TextFieldProps> = ({ label, hint, icon, className, id, ...rest }) => {
	const autoId = useId();
	const fieldId = id ?? autoId;
	return (
		<div className={cx(styles.field, className)}>
			{label && (
				<label className={styles.label} htmlFor={fieldId}>
					{label}
				</label>
			)}
			<div className={styles.control}>
				{icon && <Icon name={icon} size={17} className={styles.icon} />}
				<input id={fieldId} className={cx(styles.input, icon && styles.hasIcon)} {...rest} />
			</div>
			{hint && <p className={styles.hint}>{hint}</p>}
		</div>
	);
};

export interface TextAreaProps
	extends CommonProps,
		Omit<React.TextareaHTMLAttributes<HTMLTextAreaElement>, 'className'> {
	/** Character counter ceiling. */
	max?: number;
}

export const TextArea: React.FC<TextAreaProps> = ({
	label,
	hint,
	className,
	id,
	max,
	value,
	...rest
}) => {
	const autoId = useId();
	const fieldId = id ?? autoId;
	const len = typeof value === 'string' ? value.length : 0;
	return (
		<div className={cx(styles.field, className)}>
			{label && (
				<label className={styles.label} htmlFor={fieldId}>
					{label}
				</label>
			)}
			<textarea
				id={fieldId}
				className={cx(styles.input, styles.textarea)}
				maxLength={max}
				value={value}
				{...rest}
			/>
			<div className={styles.footRow}>
				{hint && <p className={styles.hint}>{hint}</p>}
				{max && <span className={styles.counter}>{len}/{max}</span>}
			</div>
		</div>
	);
};
