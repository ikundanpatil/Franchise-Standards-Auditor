// =============================================================================
// MIT License
// Copyright (c) 2026 Aparavi Software AG
// =============================================================================

/**
 * Home Dashboard — Area Manager landing screen: network KPIs (glass tiles,
 * animated counters), today's inspections, a compliance trend chart, a risk
 * mix donut and the latest AI-flagged alerts.
 */

import React from 'react';
import {
	AlertCard,
	Button,
	Card,
	DonutChart,
	InspectionRow,
	LineChart,
	SectionHeader,
	StatTile,
	WelcomeBanner,
} from '../../components';
import { useNav } from '../../app/navigation';
import { useToast } from '../../app/ToastHost';
import {
	COMPLIANCE_TREND,
	KPIS,
	OVERNIGHT_BRIEFING,
	RECENT_ALERTS,
	RISK_CATEGORY_SLICES,
	TODAY_SCHEDULE,
	TREND_MONTHS,
} from '../../data';
import styles from './HomeDashboard.module.css';

export const HomeDashboard: React.FC<{ managerName: string }> = ({ managerName }) => {
	const nav = useNav();
	const { flash } = useToast();

	return (
		<main className={styles.scroll}>
			<WelcomeBanner
				className={styles.reveal}
				name={managerName}
				subtitle={OVERNIGHT_BRIEFING}
			/>

			<section className={styles.stats} aria-label="Network at a glance">
				{KPIS.map((kpi, i) => {
					const { id, ...rest } = kpi;
					return (
						<StatTile
							key={id}
							{...rest}
							index={i}
							className={styles.reveal}
							style={{ animationDelay: `${60 + i * 55}ms` }}
							onClick={() => nav.navigate('reports')}
						/>
					);
				})}
			</section>

			<Button
				className={styles.reveal}
				style={{ animationDelay: '300ms' }}
				variant="primary"
				size="lg"
				block
				icon="camera"
				iconRight="sparkles"
				onClick={() => nav.navigate('upload')}
			>
				Upload Inspection
			</Button>

			<section className={styles.reveal} style={{ animationDelay: '340ms' }}>
				<SectionHeader
					title="Today's Inspections"
					count={TODAY_SCHEDULE.length}
					action={{ label: 'View all', onClick: () => nav.navigate('inspections') }}
				/>
				<div className={styles.list}>
					{TODAY_SCHEDULE.map((rec) => (
						<InspectionRow
							key={rec.id}
							record={rec}
							onClick={() => nav.navigate('memory', { storeId: rec.storeId })}
						/>
					))}
				</div>
			</section>

			<Card className={styles.reveal} style={{ animationDelay: '380ms' }} padding="lg">
				<SectionHeader
					title="Compliance Trend"
					action={{ label: '12 mo', onClick: () => flash('Showing the last 12 months.') }}
				/>
				<LineChart
					series={COMPLIANCE_TREND}
					labels={TREND_MONTHS}
					height={170}
					yMin={70}
					yMax={100}
					formatValue={(n) => `${Math.round(n)}`}
				/>
			</Card>

			<Card className={styles.reveal} style={{ animationDelay: '420ms' }} padding="lg">
				<SectionHeader title="Risk Categories" />
				<DonutChart slices={RISK_CATEGORY_SLICES} centerLabel="findings" />
			</Card>

			<section className={styles.reveal} style={{ animationDelay: '460ms' }}>
				<SectionHeader
					title="Recent Alerts"
					count={RECENT_ALERTS.length}
					action={{ label: 'Manager alerts', onClick: () => nav.navigate('alerts') }}
				/>
				<div className={styles.list}>
					{RECENT_ALERTS.map((alert) => {
						const { id, ...rest } = alert;
						return <AlertCard key={id} {...rest} onClick={() => nav.navigate('alerts')} />;
					})}
				</div>
			</section>
		</main>
	);
};

export default HomeDashboard;
