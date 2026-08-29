// =============================================================================
// MIT License
// Copyright (c) 2026 Aparavi Software AG
// =============================================================================

import React, { useMemo, useState } from 'react';
import { Icon } from '../Icon/Icon';
import { RiskBadge } from '../RiskBadge/RiskBadge';
import { Sheet } from '../primitives/Sheet';
import { TextField } from '../primitives/Field';
import { STORES } from '../../data/stores';
import { cx } from '../../utils/cx';
import type { Store } from '../../types';
import styles from './StoreSelector.module.css';

export interface StoreSelectorProps {
	value: Store | null;
	onChange: (store: Store) => void;
	className?: string;
}

/** Field that opens a searchable store picker sheet. */
export const StoreSelector: React.FC<StoreSelectorProps> = ({ value, onChange, className }) => {
	const [open, setOpen] = useState(false);
	const [q, setQ] = useState('');

	const results = useMemo(() => {
		const term = q.trim().toLowerCase();
		if (!term) return STORES;
		return STORES.filter(
			(s) =>
				s.name.toLowerCase().includes(term) ||
				s.code.includes(term) ||
				s.region.toLowerCase().includes(term),
		);
	}, [q]);

	return (
		<>
			<button
				type="button"
				className={cx(styles.trigger, className)}
				onClick={() => setOpen(true)}
			>
				<span className={styles.leading}>
					<span className={styles.pin}>
						<Icon name="storefront" size={18} />
					</span>
					{value ? (
						<span className={styles.picked}>
							<b>{value.name}</b>
							<i>
								{value.code} · {value.region}
							</i>
						</span>
					) : (
						<span className={styles.placeholder}>Select a store to inspect</span>
					)}
				</span>
				<Icon name="chevron-down" size={18} className={styles.chev} />
			</button>

			<Sheet open={open} onClose={() => setOpen(false)} title="Choose store">
				<TextField
					icon="search"
					placeholder="Search name, code or region"
					value={q}
					onChange={(e) => setQ(e.target.value)}
					className={styles.search}
				/>
				<ul className={styles.list}>
					{results.map((s) => (
						<li key={s.id}>
							<button
								type="button"
								className={cx(styles.row, value?.id === s.id && styles.rowActive)}
								onClick={() => {
									onChange(s);
									setOpen(false);
									setQ('');
								}}
							>
								<span className={styles.rowMain}>
									<b>{s.name}</b>
									<i>
										{s.code} · {s.region} · {s.complianceScore}/100
									</i>
								</span>
								<RiskBadge level={s.risk} />
							</button>
						</li>
					))}
					{!results.length && <li className={styles.empty}>No stores match “{q}”.</li>}
				</ul>
			</Sheet>
		</>
	);
};
