// =============================================================================
// MIT License
// Copyright (c) 2026 Aparavi Software AG
// =============================================================================

import React, { useMemo, useState } from 'react';
import {
	Button,
	Card,
	Icon,
	PageHeader,
	RiskBadge,
	Screen,
	SegmentedControl,
} from '../../components';
import { useNav } from '../../app/navigation';
import { useToast } from '../../app/ToastHost';
import { MANAGER_ALERTS } from '../../data/alerts';
import { RISK_TONE } from '../../utils/risk';
import type { ManagerAlert, RiskLevel } from '../../types';
import styles from './ManagerAlerts.module.css';

type Filter = 'all' | 'critical' | 'high' | 'medium';
const SEGMENTS: Array<{ id: Filter; label: string }> = [
	{ id: 'all', label: 'All' },
	{ id: 'critical', label: 'Critical' },
	{ id: 'high', label: 'High' },
	{ id: 'medium', label: 'Medium' },
];

const STATUS_LABEL: Record<ManagerAlert['status'], string> = {
	open: 'Open',
	ack: 'Acknowledged',
	scheduled: 'Re-inspection booked',
	escalated: 'Escalated to Legal',
};

export const ManagerAlerts: React.FC = () => {
	const nav = useNav();
	const { flash } = useToast();
	const [filter, setFilter] = useState<Filter>('all');
	const [open, setOpen] = useState<string | null>(MANAGER_ALERTS[0].id);
	const [statuses, setStatuses] = useState<Record<string, ManagerAlert['status']>>(() =>
		Object.fromEntries(MANAGER_ALERTS.map((a) => [a.id, a.status])),
	);

	const list = useMemo(
		() => (filter === 'all' ? MANAGER_ALERTS : MANAGER_ALERTS.filter((a) => a.level === filter)),
		[filter],
	);

	const counts = useMemo(() => {
		const c: Record<RiskLevel, number> = { low: 0, medium: 0, high: 0, critical: 0 };
		MANAGER_ALERTS.forEach((a) => {
			c[a.level] += 1;
		});
		return c;
	}, []);

	const act = (a: ManagerAlert, kind: 'reinspect' | 'cure' | 'legal') => {
		const map = {
			reinspect: { status: 'scheduled' as const, msg: `Re-inspection booked for ${a.storeName} in 72h.`, icon: 'calendar' as const },
			cure: { status: 'ack' as const, msg: `Cure notice issued to ${a.storeName} — 7-day deadline.`, icon: 'file-text' as const },
			legal: { status: 'escalated' as const, msg: `${a.storeName} escalated to Legal & Compliance.`, icon: 'gavel' as const },
		}[kind];
		setStatuses((s) => ({ ...s, [a.id]: map.status }));
		flash(map.msg, map.icon);
	};

	return (
		<Screen
			header={
				<PageHeader
					title="Manager Alerts"
					subtitle={`${counts.critical} critical · ${counts.high} high · ${counts.medium} medium`}
					icon="bell"
					onBack={nav.back}
				/>
			}
		>
			<div className={styles.summary}>
				<div className={styles.sumCard} data-fg-tone="critical">
					<b>{counts.critical}</b>
					<span>Critical</span>
				</div>
				<div className={styles.sumCard} data-fg-tone="risk">
					<b>{counts.high}</b>
					<span>High</span>
				</div>
				<div className={styles.sumCard} data-fg-tone="warn">
					<b>{counts.medium}</b>
					<span>Medium</span>
				</div>
			</div>

			<SegmentedControl segments={SEGMENTS} value={filter} onChange={setFilter} />

			<div className={styles.list}>
				{list.map((a, i) => {
					const status = statuses[a.id];
					const isOpen = open === a.id;
					const handled = status !== 'open' && status !== 'ack';
					return (
						<Card
							key={a.id}
							padding="none"
							className={styles.card}
							style={{ animationDelay: `${i * 55}ms` }}
						>
							<button
								type="button"
								className={styles.head}
								onClick={() => setOpen((c) => (c === a.id ? null : a.id))}
								data-fg-tone={RISK_TONE[a.level]}
							>
								<span className={styles.glyph}>
									<Icon name={a.icon} size={18} />
								</span>
								<span className={styles.headBody}>
									<span className={styles.title}>{a.title}</span>
									<span className={styles.sub}>
										{a.storeName} · {a.storeCode} · {a.region}
									</span>
									<span className={styles.tags}>
										<RiskBadge level={a.level} />
										<span className={styles.meta}>
											<Icon name="sparkle" size={10} /> {Math.round(a.aiConfidence * 100)}%
										</span>
										<span className={styles.meta}>
											<Icon name="clock" size={10} /> {a.raisedAt}
										</span>
									</span>
								</span>
								<Icon
									name="chevron-down"
									size={16}
									className={`${styles.chev} ${isOpen ? styles.chevOpen : ''}`}
								/>
							</button>

							{isOpen && (
								<div className={styles.detail}>
									<p className={styles.detailText}>{a.detail}</p>
									<div className={styles.slaRow}>
										<span className={styles.sla}>
											<Icon name="target" size={11} /> {a.sla}
										</span>
										<span
											className={styles.statusPill}
											data-done={handled ? 'yes' : undefined}
										>
											{STATUS_LABEL[status]}
										</span>
									</div>
									<div className={styles.actions}>
										<Button size="sm" variant="secondary" icon="refresh" onClick={() => act(a, 'reinspect')}>
											Re-inspection
										</Button>
										<Button size="sm" variant="ghost" icon="file-text" onClick={() => act(a, 'cure')}>
											Cure notice
										</Button>
										<Button size="sm" variant="danger" icon="gavel" onClick={() => act(a, 'legal')}>
											Escalate legal
										</Button>
									</div>
								</div>
							)}
						</Card>
					);
				})}
			</div>
		</Screen>
	);
};
