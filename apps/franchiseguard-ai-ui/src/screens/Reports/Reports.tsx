// =============================================================================
// MIT License
// Copyright (c) 2026 Aparavi Software AG
// =============================================================================

/**
 * Reports — the "Reports" tab: network analytics (compliance trend, risk
 * breakdown) over the generated compliance reports, plus a tappable list of
 * every report produced this cycle.
 */

import React, { useMemo, useState } from 'react';
import {
	Button,
	Card,
	DonutChart,
	Icon,
	LineChart,
	RiskBadge,
	SectionHeader,
	SegmentedControl,
} from '../../components';
import { useNav } from '../../app/navigation';
import { useToast } from '../../app/ToastHost';
import { SAVED_REPORTS } from '../../data/reports';
import {
	COMPLIANCE_TREND,
	RISK_CATEGORY_SLICES,
	TREND_MONTHS,
	riskMixSlices,
} from '../../data/dashboard';
import { longDate } from '../../lib/format';
import { RISK_TONE } from '../../utils/risk';
import styles from './Reports.module.css';

type View = 'categories' | 'stores';

const VIEW_SEGMENTS: Array<{ id: View; label: string }> = [
	{ id: 'categories', label: 'By category' },
	{ id: 'stores', label: 'By store risk' },
];

export const Reports: React.FC = () => {
	const nav = useNav();
	const { flash } = useToast();
	const [view, setView] = useState<View>('categories');

	const totals = useMemo(() => {
		const t = { critical: 0, major: 0, minor: 0 };
		SAVED_REPORTS.forEach((r) => {
			t.critical += r.counts.critical;
			t.major += r.counts.major;
			t.minor += r.counts.minor;
		});
		return t;
	}, []);

	const findings = totals.critical + totals.major + totals.minor;

	return (
		<main className={styles.scroll}>
			<header className={`${styles.head} ${styles.reveal}`}>
				<div>
					<h1 className={styles.title}>Reports</h1>
					<p className={styles.sub}>
						{SAVED_REPORTS.length} generated · {findings} findings
					</p>
				</div>
				<Button
					size="sm"
					variant="ghost"
					icon="download"
					onClick={() => flash('Exporting all reports as a ZIP…', 'download')}
				>
					Export
				</Button>
			</header>

			<section className={`${styles.kpis} ${styles.reveal}`} style={{ animationDelay: '60ms' }}>
				<div className={styles.kpi} data-fg-tone="critical">
					<b>{totals.critical}</b>
					<span>Critical</span>
				</div>
				<div className={styles.kpi} data-fg-tone="risk">
					<b>{totals.major}</b>
					<span>Major</span>
				</div>
				<div className={styles.kpi} data-fg-tone="warn">
					<b>{totals.minor}</b>
					<span>Minor</span>
				</div>
			</section>

			<Card padding="lg" className={styles.reveal} style={{ animationDelay: '110ms' }}>
				<SectionHeader
					title="Compliance trend"
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

			<Card padding="lg" className={styles.reveal} style={{ animationDelay: '150ms' }}>
				<SectionHeader title="Risk breakdown" />
				<SegmentedControl segments={VIEW_SEGMENTS} value={view} onChange={setView} />
				<div className={styles.donutWrap}>
					<DonutChart
						slices={view === 'categories' ? RISK_CATEGORY_SLICES : riskMixSlices()}
						centerLabel={view === 'categories' ? 'findings' : 'stores'}
					/>
				</div>
			</Card>

			<section className={styles.reveal} style={{ animationDelay: '190ms' }}>
				<SectionHeader title="Generated reports" count={SAVED_REPORTS.length} />
				<div className={styles.list}>
					{SAVED_REPORTS.map((r) => (
						<button
							key={r.id}
							type="button"
							className={styles.report}
							data-fg-tone={RISK_TONE[r.risk]}
							onClick={() => nav.navigate('report', { storeId: r.storeId })}
						>
							<span className={styles.grade}>{r.grade}</span>
							<span className={styles.rMain}>
								<span className={styles.rTop}>
									<span className={styles.rStore}>{r.storeName}</span>
									<span className={styles.rCode}>{r.storeCode}</span>
								</span>
								<span className={styles.rRef}>{r.ref}</span>
								<span className={styles.rFoot}>
									<RiskBadge level={r.risk} />
									<span className={styles.rMeta}>
										<Icon name="calendar" size={10} /> {longDate(r.date)}
									</span>
									<span className={styles.rMeta}>
										<Icon name="user" size={10} /> {r.inspector}
									</span>
								</span>
							</span>
							<Icon name="chevron-right" size={17} className={styles.rChev} />
						</button>
					))}
				</div>
			</section>
		</main>
	);
};

export default Reports;
