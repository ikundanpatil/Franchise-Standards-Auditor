// =============================================================================
// MIT License
// Copyright (c) 2026 Aparavi Software AG
// =============================================================================

import React, { useMemo } from 'react';
import {
	BarChart,
	Button,
	Card,
	Icon,
	InspectionRow,
	LineChart,
	MetricPill,
	PageHeader,
	RiskBadge,
	Screen,
	SectionHeader,
	Sparkline,
} from '../../components';
import { useNav } from '../../app/navigation';
import { CHART } from '../../data/palette';
import { inspectionsForStore } from '../../data/inspections';
import { storeById, STORES } from '../../data/stores';
import { COMPLAINT_TREND, COMPLAINT_WEEKS } from '../../data/dashboard';
import { longDate } from '../../lib/format';
import styles from './LocationMemory.module.css';

export const LocationMemory: React.FC = () => {
	const nav = useNav();
	const store = useMemo(
		() => storeById(nav.params.storeId ?? 's-204') ?? STORES[1],
		[nav.params.storeId],
	);

	const history = inspectionsForStore(store.id);

	const riskLabels = useMemo(
		() => store.riskSeries.map((_, i) => (i === store.riskSeries.length - 1 ? 'now' : `${(store.riskSeries.length - 1 - i) * 7}d`)),
		[store],
	);

	// Resolved vs unresolved violations across the last 6 months, derived from
	// the store's current open rate.
	const resolvedBars = useMemo(() => {
		const months = ['Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug'];
		return months.map((label, i) => {
			const total = 4 + Math.round(Math.sin(i) * 2 + i * 0.7);
			const unresolved = Math.max(0, Math.round(total * store.openRate * (i === 5 ? 1 : 0.6)));
			return {
				label,
				bars: [
					{ value: total - unresolved, color: CHART.green, name: 'Resolved' },
					{ value: unresolved, color: CHART.amber, name: 'Unresolved' },
				],
			};
		});
	}, [store]);

	const totalResolved = resolvedBars.reduce((s, m) => s + m.bars[0].value, 0);
	const totalOpen = resolvedBars.reduce((s, m) => s + m.bars[1].value, 0);

	return (
		<Screen
			header={
				<PageHeader
					title={store.name}
					subtitle={`${store.code} · ${store.region} · mgr ${store.manager}`}
					icon="map-pin"
					onBack={nav.back}
					action={{ icon: 'camera', label: 'New inspection', onClick: () => nav.navigate('upload', { storeId: store.id }) }}
				/>
			}
		>
			<Card padding="lg" className={styles.hero}>
				<div className={styles.heroTop}>
					<div>
						<span className={styles.score}>{store.complianceScore}</span>
						<span className={styles.scoreUnit}>/100</span>
					</div>
					<RiskBadge level={store.risk} />
				</div>
				<Sparkline data={store.trend} width={240} height={40} className={styles.heroSpark} />
				<p className={styles.addr}>
					<Icon name="map-pin" size={12} /> {store.address}
				</p>
				<div className={styles.pills}>
					<MetricPill icon="clipboard-check" value={history.filter((h) => h.status !== 'scheduled').length} label="inspections logged" tone="info" />
					<MetricPill icon="alert-triangle" value={store.openViolations} label="open violations" tone="risk" />
					<MetricPill icon="calendar" value={longDate(store.nextInspectionDue)} label="next due" tone="violet" />
				</div>
			</Card>

			<Card padding="lg">
				<SectionHeader title="Risk score · last 90 days" action={{ label: '90d', onClick: () => undefined }} />
				<LineChart
					series={[{ name: 'Risk index', color: CHART.red, points: store.riskSeries }]}
					labels={riskLabels}
					height={160}
					yMax={100}
				/>
			</Card>

			<Card padding="lg">
				<SectionHeader title="Complaint trend" />
				<LineChart
					series={COMPLAINT_TREND}
					labels={COMPLAINT_WEEKS}
					height={150}
					area
					formatValue={(n) => `${Math.round(n)}`}
				/>
			</Card>

			<Card padding="lg">
				<SectionHeader title="Resolved vs unresolved" />
				<BarChart groups={resolvedBars} stacked height={168} />
				<div className={styles.legend}>
					<span><i style={{ background: CHART.green }} /> Resolved · {totalResolved}</span>
					<span><i style={{ background: CHART.amber }} /> Unresolved · {totalOpen}</span>
				</div>
			</Card>

			<div>
				<SectionHeader title="Previous inspections" count={history.length} />
				<div className={styles.list}>
					{history.map((rec) => (
						<InspectionRow key={rec.id} record={rec} onClick={() => nav.navigate('report', { storeId: store.id })} />
					))}
				</div>
			</div>

			<Button variant="secondary" block icon="camera" onClick={() => nav.navigate('upload', { storeId: store.id })}>
				Start a new inspection here
			</Button>
		</Screen>
	);
};
