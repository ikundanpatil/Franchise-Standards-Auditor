// =============================================================================
// MIT License
// Copyright (c) 2026 Aparavi Software AG
// =============================================================================

/**
 * Inspections — the "Inspections" tab: every logged and scheduled inspection
 * across the network, with a status filter, search, a completion chart and a
 * tappable list that routes into the report or the upload flow.
 */

import React, { useMemo, useState } from 'react';
import {
	BarChart,
	Button,
	Card,
	Icon,
	InspectionRow,
	SectionHeader,
	SegmentedControl,
	TextField,
} from '../../components';
import { useNav } from '../../app/navigation';
import { INSPECTIONS } from '../../data/inspections';
import { INSPECTION_COMPLETION } from '../../data/dashboard';
import { CHART } from '../../data/palette';
import type { InspectionRecord } from '../../types';
import styles from './Inspections.module.css';

type Filter = 'all' | 'flagged' | 'passed' | 'scheduled';

const SEGMENTS: Array<{ id: Filter; label: string }> = [
	{ id: 'all', label: 'All' },
	{ id: 'flagged', label: 'Flagged' },
	{ id: 'passed', label: 'Passed' },
	{ id: 'scheduled', label: 'Scheduled' },
];

const MATCH: Record<Filter, (r: InspectionRecord) => boolean> = {
	all: () => true,
	flagged: (r) => r.status === 'flagged' || r.status === 'failed',
	passed: (r) => r.status === 'passed',
	scheduled: (r) => r.status === 'scheduled',
};

const SUMMARY = [
	['passed', 'Passed', 'good'],
	['flagged', 'Flagged', 'warn'],
	['failed', 'Failed', 'critical'],
	['scheduled', 'Scheduled', 'info'],
] as const;

export const Inspections: React.FC = () => {
	const nav = useNav();
	const [filter, setFilter] = useState<Filter>('all');
	const [query, setQuery] = useState('');

	const counts = useMemo(() => {
		const c: Record<InspectionRecord['status'], number> = {
			passed: 0,
			flagged: 0,
			failed: 0,
			scheduled: 0,
		};
		INSPECTIONS.forEach((r) => {
			c[r.status] += 1;
		});
		return c;
	}, []);

	const list = useMemo(() => {
		const term = query.trim().toLowerCase();
		return INSPECTIONS.filter(MATCH[filter]).filter(
			(r) =>
				!term ||
				r.storeName.toLowerCase().includes(term) ||
				r.storeCode.toLowerCase().includes(term),
		);
	}, [filter, query]);

	const open = (r: InspectionRecord) =>
		r.status === 'scheduled'
			? nav.navigate('upload', { storeId: r.storeId })
			: nav.navigate('report', { storeId: r.storeId });

	return (
		<main className={styles.scroll}>
			<header className={`${styles.head} ${styles.reveal}`}>
				<div>
					<h1 className={styles.title}>Inspections</h1>
					<p className={styles.sub}>
						{INSPECTIONS.length} logged · {counts.scheduled} scheduled
					</p>
				</div>
				<Button size="sm" variant="primary" icon="camera" onClick={() => nav.navigate('upload')}>
					New
				</Button>
			</header>

			<section className={`${styles.summary} ${styles.reveal}`} style={{ animationDelay: '60ms' }}>
				{SUMMARY.map(([key, label, tone]) => (
					<div key={key} className={styles.sumCard} data-fg-tone={tone}>
						<b>{counts[key]}</b>
						<span>{label}</span>
					</div>
				))}
			</section>

			<div className={styles.reveal} style={{ animationDelay: '110ms' }}>
				<SegmentedControl segments={SEGMENTS} value={filter} onChange={setFilter} />
			</div>

			<TextField
				className={styles.reveal}
				icon="search"
				placeholder="Search store name or code"
				value={query}
				onChange={(e) => setQuery(e.target.value)}
			/>

			<Card padding="lg" className={styles.reveal} style={{ animationDelay: '160ms' }}>
				<SectionHeader title="Completion by week" />
				<BarChart groups={INSPECTION_COMPLETION} height={168} />
				<div className={styles.legend}>
					<span>
						<i style={{ background: CHART.slate }} /> Planned
					</span>
					<span>
						<i style={{ background: CHART.blue }} /> Completed
					</span>
				</div>
			</Card>

			<section className={styles.reveal} style={{ animationDelay: '200ms' }}>
				<SectionHeader
					title={filter === 'all' ? 'All inspections' : SEGMENTS.find((s) => s.id === filter)!.label}
					count={list.length}
				/>
				<div className={styles.list}>
					{list.length ? (
						list.map((r) => (
							<InspectionRow key={r.id} record={r} onClick={() => open(r)} />
						))
					) : (
						<p className={styles.empty}>
							<Icon name="search" size={15} /> No inspections match “{query}”.
						</p>
					)}
				</div>
			</section>
		</main>
	);
};

export default Inspections;
